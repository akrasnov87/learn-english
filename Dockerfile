FROM ubuntu:20.04
RUN apt update && apt upgrade -y
COPY learning /app/learning
COPY app.py /app/app.py
COPY util.py /app/util.py
WORKDIR /app
ARG DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC
RUN apt install python python3-pip -y
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN apt-get clean autoclean
RUN apt-get autoremove --yes
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN chmod -R 774 /app
RUN groupadd -r learn && useradd -r -g learn learn
RUN chown -R learn:learn /app
RUN python3 -c "import nltk;nltk.download('stopwords', download_dir='/home/learn/nltk_data')"
RUN python3 -c "import nltk;nltk.download('punkt', download_dir='/home/learn/nltk_data')"

ENTRYPOINT [ "python3" ]
USER learn
CMD [ "-m", "streamlit", "run", "/app/app.py" ]