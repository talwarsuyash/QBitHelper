FROM python:latest
FROM gorialis/discord.py
RUN pip install -U discord-py-slash-command
RUN pip install -U qbittorrent-api
RUN pip install -U python-dotenv
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot
ENV token ""
ENV qbit_host ""
ENV qbit_port ""
ENV qbit_user ""
ENV qbit_pass ""
COPY . .
CMD ["python3","-u","QBit.py"]