FROM python:3.7
RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY nats-quote-sub /tmp/nats-quote-sub/
CMD python /tmp/nats-quote-sub
