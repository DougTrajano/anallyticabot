# base image
FROM python:3.7

# making directory of app
RUN mkdir /app
WORKDIR /app

# exposing default port for streamlit
EXPOSE 8501

# copy over requirements
COPY requirements.txt /app/

# install pip then packages
RUN pip install --upgrade pip \
    && pip install -r requirements.txt --upgrade

# copying all files over
COPY . /app/

ENV PYTHONPATH="${PYTHONPATH}:/app"