FROM python:3.5.6-jessie


COPY ./src /srv

# install application dependencies

RUN cd /srv && pip install -r requirements.txt

ENV PYTHONPATH="/srv:/srv/bot:${PYTHONPATH}"

WORKDIR /srv/bot

# expose ports to the outer world

CMD python bot.py
