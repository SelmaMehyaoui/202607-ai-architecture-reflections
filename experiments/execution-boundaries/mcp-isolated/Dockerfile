FROM python:3.11.13-slim@sha256:9bffe4353b925a1656688797ebc68f9c525e79b1d377a764d232182a519eeec4

RUN useradd --create-home --uid 10001 experiment
WORKDIR /app
RUN pip install --no-cache-dir "mcp>=1.27,<2"
COPY common/ /app/common/
COPY mcp-isolated/server.py /app/server.py
USER experiment
ENTRYPOINT ["python", "/app/server.py"]
