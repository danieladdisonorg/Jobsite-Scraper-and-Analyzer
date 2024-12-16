FROM python:3.10-slim

LABEL maintainer="olehoryshshuk@gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt ./

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libtool

# Upgrade pip to avoid issues with old versions
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
