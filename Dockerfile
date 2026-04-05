FROM python:3.11-slim

# OpenEnv metadata labels for Hugging Face Spaces
LABEL org.opencontainers.image.title="Email Triage OpenEnv"
LABEL org.opencontainers.image.description="A real-world OpenEnv environment for email triage and response"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="EmitBoi"
LABEL org.opencontainers.image.source="https://huggingface.co/spaces/EmitBoi/email-triage-env"
LABEL openenv.name="email-triage-env"
LABEL openenv.version="1.0.0"
LABEL openenv.tasks="email_classify,email_respond,email_thread"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY inference.py .
COPY openenv.yaml .
COPY README.md .
COPY pyproject.toml .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for HF Spaces
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import httpx; r=httpx.get('http://localhost:7860/'); assert r.status_code==200"

# Start the FastAPI server
CMD ["python", "-m", "uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "7860"]
