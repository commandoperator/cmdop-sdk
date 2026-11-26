# Standalone stdio fixture for the product-container reference example.
FROM python:3.13-slim
WORKDIR /opt/report
RUN python -m pip install --no-cache-dir "fastmcp==4.2.6" "mcp==2.3.0"
COPY server.py read_report.py build.json ./
USER 65532:65532
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python", "/opt/report/server.py"]
