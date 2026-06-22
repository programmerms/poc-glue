FROM python:3.10-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
COPY tests /app/tests
COPY pytest.ini /app/pytest.ini

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "jobs.tailor_proposal_job"]
