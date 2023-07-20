FROM python:3.10.6-slim

ARG BRANCH=default_branch
ENV APP_BRANCH=$BRANCH
EXPOSE 8000

# Install Git
RUN apt-get update && apt-get install -y git

# Install app
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run Battlesnake
CMD [ "python", "main.py"]
