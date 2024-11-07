FROM python
RUN apt-get update && apt-get install python3-pip -y
WORKDIR /projeto_final
COPY . /projeto_final/
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]