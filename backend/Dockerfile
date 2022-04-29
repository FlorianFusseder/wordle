FROM python:3.8.13-alpine

RUN mkdir -p /app/wordle_bot
RUN mkdir /files
RUN touch /app/wordle_bot/__init__.py
RUN mkdir /app/files

COPY wordle_bot/wordle.py /app/wordle_bot
COPY backend/webserver.py /app
COPY files/5long.txt /files
COPY files/statistics.json /files
COPY files/whitelist.txt /files

COPY backend/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "webserver.py"]