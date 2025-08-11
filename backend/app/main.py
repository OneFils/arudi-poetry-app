from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import jwt, os

from .db import Base, engine, get_db
from .models import TextDoc, Analysis, User
from .schemas import AnalyzeIn, AnalyzeOut, LineOut
from .auth import router as auth_router, require_user
from .nlp.diacritizer import diacritize
from .nlp.prosody import to_prosody, tail_qafiyah
from .nlp.rules import rule_match, TAFAIL
from .nlp.hf_model import predict_meter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Arudi API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"])
app.include_router(auth_router)


def uid_from_auth(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.split()[1]
    return require_user(token)


@app.post("/analyze", response_model=AnalyzeOut)
def analyze(body: AnalyzeIn, db: Session = Depends(get_db), uid: int = Depends(uid_from_auth)):
    lines = [l for l in (body.text or "").splitlines() if l.strip()]
    if not lines:
        return {"results": []}
    # save text
    doc = TextDoc(user_id=uid, raw_text=body.text)
    db.add(doc)
    db.flush()
    results = []
    for line in lines:
        d = diacritize(line)
        pros = to_prosody(d)
        rb_meter, rb_taf, rb_p = rule_match(pros)
        ml_meter, ml_p = predict_meter(line)
        if rb_meter and rb_meter == ml_meter:
            meter, conf, taf = rb_meter, (rb_p + ml_p) / 2, rb_taf
        else:
            if ml_p >= rb_p:
                meter, conf = ml_meter, ml_p
            else:
                meter, conf = rb_meter, rb_p
            taf = TAFAIL.get(meter or "", "")
        q = tail_qafiyah(line)
        res = {"line": line, "meter": meter or "غير محدد", "tafail": taf, "qafiyah": q, "confidence": round(conf, 3)}
        results.append(res)
        db.add(
            Analysis(
                text_id=doc.id,
                meter=res["meter"],
                tafail=res["tafail"],
                qafiyah=res["qafiyah"],
                confidence=int(res["confidence"] * 100),
                payload={"prosody": pros, "diacritized": d},
            )
        )
    db.commit()
    return {"results": [LineOut(**r) for r in results]}


@app.get("/library")
def library(db: Session = Depends(get_db), uid: int = Depends(uid_from_auth)):
    docs = (
        db.query(TextDoc)
        .filter(TextDoc.user_id == uid)
        .order_by(TextDoc.created_at.desc())
        .all()
    )
    return [
        {"id": d.id, "created_at": str(d.created_at), "preview": d.raw_text[:60]}
        for d in docs
    ]
