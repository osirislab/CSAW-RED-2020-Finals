FROM python:3.7

RUN mkdir /opt/app
WORKDIR /opt/app

RUN pip3 install gunicorn
RUN pip3 install crcmod
RUN pip3 install flask

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]