FROM python:alpine

LABEL Maintainer="sulavthapa"

WORKDIR /src

RUN pip install flask
RUN pip install requests
RUN pip install rq

COPY . .

CMD ["python3","app.py"]