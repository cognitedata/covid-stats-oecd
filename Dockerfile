FROM python:3.7-slim AS builder

WORKDIR /

COPY requirements.txt requirements.txt

ENV PYTHONUNBUFFERED=1
RUN pip3 install --target=/app -r requirements.txt
COPY streamlit_app.py /app

FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app
ENV PYTHONPATH /app
EXPOSE 8501

ENTRYPOINT [ "streamlit", "run", "/app/streamlit_app.py"]