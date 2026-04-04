# Multi-stage build for Kostal Piko BA Energy Monitoring

# Stage 1: Builder
FROM python:3.13-slim


WORKDIR /app

# Copy application code
COPY . .


ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
# Set environment to use venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create non-root user for security
RUN useradd -m -u 1023 appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /opt/venv

# Switch to non-root user
USER appuser



RUN pip install -r requirements.txt

# Healthcheck (optional)
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import logging; logging.info('Container is running')" || exit 1

# Default command - can be overridden
# Entrypoint - stellt sicher, dass Python PID 1 ist
ENTRYPOINT ["python", "-u"]
# CMD ["python", "monitoring_template.py", "Kostal_Piko_BA"]
# set via compose: command: ["python", "monitoring_template.py", "Kostal_Piko_BA"]
