FROM python:3.11.9-slim
WORKDIR /app
COPY . /app
RUN apt-get update &&\
   apt-get install -y curl
RUN pip install requests
RUN pip install pytest
EXPOSE 6543
CMD ["python", "quotes_server.py"]