# --- model-export: 빌드 타임 전용. PyTorch는 이 스테이지에만 있고 최종 이미지엔 안 들어간다. ---
# 자세한 이유는 scripts/export_embedding_model.py 참고.
FROM python:3.12-slim AS model-export
WORKDIR /export
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir transformers onnx onnxruntime onnxscript numpy
COPY scripts/export_embedding_model.py .
RUN python export_embedding_model.py /export/models

# --- 런타임 이미지: onnxruntime만 있고 가볍다. ---
FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY --from=model-export /export/models /app/var/models
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
