FROM python:3.7
ADD requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

# Add the other things
WORKDIR user_setting
ADD . .
ENTRYPOINT ["python3", "__main__.py"]