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

# cmd to launch app when container is run
CMD streamlit run anallyticabot.py

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'