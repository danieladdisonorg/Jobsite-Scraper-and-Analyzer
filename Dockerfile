FROM python:3.10-slim

LABEL maintainer="olehoryshshuk@gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt ./

# set non interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# set environment variables for webdriver_manager
ENV WDM_LOCAL 1
ENV WDM_CACHE_DIR /usr/local/wdm

# install system dependencies and python dependencies using shell script
COPY install_dependencies.sh /usr/src/app/install_dependencies.sh
RUN chmod +x ./install_dependencies.sh
RUN ./install_dependencies.sh

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
