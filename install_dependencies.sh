#!/usr/bin/env bash

# Install system dependencies
apt-get update && apt-get install -y \
  build-essential \
  cmake \
  libtool \
  wget \
  gnupg

# Add Google Chrome's repository and GPG key for scraping
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install Google Chrome for scraping
apt-get -y install google-chrome-stable

# Clean up
apt-get clean && rm -rf /var/lib/apt/lists/*

# upgrade pip to avoid issues with old versions
pip install --upgrade pip

# install project dependencies
pip install --no-cache-dir -r /usr/src/app/requirements.txt
