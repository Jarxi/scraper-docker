## Use an official Python runtime as a parent image
FROM python:3.7
#
## Set the working directory to /app
WORKDIR /scraper-docker
#
## Copy the current directory contents into the container at /scraper-docker
COPY requirements.txt /scraper-docker
#
## Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

## install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
RUN apt-get install libnss3
#
# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Install xlsx
RUN pip install xlsxwriter
RUN pip install selenium
RUN pip install pandas

# set display port to avoid crash
ENV DISPLAY=:99

COPY . /scraper-docker

# Run app.py when the container launches
CMD ["python3", "-u","app.py"]

