#FROM python:3.7
FROM pypy:3.6
RUN apt-get update -y && apt-get install -y git gcc g++
ADD requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

# Add the other things
WORKDIR token_dispenser
ADD ./ .
ENTRYPOINT ["pypy3", "__main__.py"]