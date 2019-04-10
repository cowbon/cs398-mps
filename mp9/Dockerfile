FROM tiangolo/uwsgi-nginx-flask:python3.6
COPY app.py /
COPY templates/ /templates/
RUN pip3 install requests Flask bs4
CMD python3 /app.py
