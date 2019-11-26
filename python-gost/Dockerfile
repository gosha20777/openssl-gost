FROM rnix/openssl-gost
RUN apt install python3-dev python3-pip -y
RUN pip3 install flask
EXPOSE 80
CMD ["python3", "server.py"]