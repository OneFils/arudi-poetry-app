FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY app /app/app
COPY requirements.txt /app/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git wget && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# تنزيل الموديل أثناء البناء لضمان جاهزيته
RUN python - <<'PY'
from transformers import AutoTokenizer, AutoModelForSequenceClassification
m = 'faisalq/bert-base-arapoembert'
AutoTokenizer.from_pretrained(m)
AutoModelForSequenceClassification.from_pretrained(m)
print('HF models cached')
PY

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
