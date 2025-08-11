from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np, torch
M_LABELS = ["الطويل","المديد","البسيط","الوافر","الكامل","الهزج","الرجز","الرمل",
            "السريع","المنسرح","الخفيف","المضارع","المقتضب","المجتث","المتقارب","المتدارك"]

_tok = AutoTokenizer.from_pretrained("faisalq/bert-base-arapoembert")
_clf = AutoModelForSequenceClassification.from_pretrained(
    "faisalq/bert-base-arapoembert", num_labels=len(M_LABELS))

def predict_meter(text: str):
    inputs = _tok(text, truncation=True, padding=True, return_tensors="pt")
    with torch.no_grad():
        logits = _clf(**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1).cpu().numpy()
    idx = int(np.argmax(probs))
    return M_LABELS[idx], float(probs[idx])
