FROM python:3.10-slim

LABEL maintainer="olehoryshshuk@gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set non interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# set environment variables for webdriver_manager
ENV WDM_LOCAL 1
ENV WDM_CACHE_DIR /usr/local/wdm

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    gnupg \
    ca-certificates \
    curl \
    apt-transport-https \
    build-essential \
    cmake \
    libtool && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Google's GPG key and Chrome repository
RUN curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

# install system dependencies and python dependencies using shell script
COPY scripts/entrypoint.sh /usr/src/app/scripts/entrypoint.sh
RUN chmod +x scripts/entrypoint.sh