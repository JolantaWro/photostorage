FROM python:3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /photostorage_service

WORKDIR /photostorage_service

COPY . /photostorage_service/

RUN pip install -r requirements.txt
