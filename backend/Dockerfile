FROM python:3.8.13
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY ../bot/wordle.py /app
COPY webserver.py /app
COPY ../bot/5long.txt /app
COPY ../bot/statistics.json /app
COPY ../bot/whitelist.txt /app
ENTRYPOINT [ "python" ]
CMD [ "webserver.py"]