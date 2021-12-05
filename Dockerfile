FROM python:3-onbuild
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["python", "manage.py", "runsslserver","--certificate","./server.crt","--key","./server.key", "0.0.0.0:8000"]


# runsslserver --certificate ./server.crt --key ./server.key 0.0.0.0:8000