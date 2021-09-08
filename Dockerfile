FROM python:3.7
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8501
COPY streamlit_app.py ./app.py
ENTRYPOINT ["streamlit", "run"]
CMD ["streamlit_app.py"]
