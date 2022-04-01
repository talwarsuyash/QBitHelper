FROM python:latest
FROM gorialis/discord.py
RUN pip install -U discord-py-slash-command
RUN pip install -U qbittorrent-api
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY . .
CMD ["python3","QBit.py"]