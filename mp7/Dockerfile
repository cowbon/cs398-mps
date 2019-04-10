# Part 1
FROM ubuntu

# Part 2
LABEL CLASS="CS398"\
      NETID="ianchin2"

# Part 3
RUN apt update -y && apt install python3 -y
RUN apt install python3-pip -y && pip3 install flask

# Part 4
COPY info.txt /data/
RUN useradd cs398
USER cs398
ENV SCHOOL="uiuc"

# Part 5
COPY app.py /home/
CMD python3 /home/app.py
