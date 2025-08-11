from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    texts = relationship("TextDoc", back_populates="user")

class TextDoc(Base):
    __tablename__ = "texts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    analyses = relationship("Analysis", back_populates="text")
    user = relationship("User", back_populates="texts")

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    text_id = Column(Integer, ForeignKey("texts.id"))
    meter = Column(String(40))
    tafail = Column(Text)
    qafiyah = Column(String(4))
    confidence = Column(Integer)
    payload = Column(JSON)
    text = relationship("TextDoc", back_populates="analyses")
