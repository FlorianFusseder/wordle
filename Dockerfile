FROM python:3.8.13
COPY ./requirements-web.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY ./wordle.py /app
COPY ./webserver.py /app
COPY ./5long.txt /app
COPY ./statistics.json /app
COPY ./whitelist.txt /app
ENTRYPOINT [ "waitress-serve" ]
CMD [ "webserver:app", "--port=$PORT" ]