FROM python:3.12-alpine AS dependencies
WORKDIR /build
RUN apk add --no-cache build-base libpq-dev
COPY requirements.txt .
# Build the C adapter against Alpine's libpq; leave compilers in this stage.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt 'psycopg[c]'

FROM python:3.12-alpine
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apk add --no-cache libpq \
    && addgroup -g 10001 appuser \
    && adduser -D -u 10001 -G appuser appuser
COPY --from=dependencies /install /usr/local
# Fail the image build if the PostgreSQL adapter cannot load its runtime library.
RUN python -c 'import psycopg; assert psycopg.pq.__impl__ == "c"'
COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
