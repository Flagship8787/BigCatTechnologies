# Builder stage
FROM python:3.12-slim AS builder

RUN pip install uv

WORKDIR /app

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
