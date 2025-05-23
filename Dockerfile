
FROM python:3.12.1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

EXPOSE 80

CMD ["fastapi", "run", "src/main.py", "--port", "80"]