FROM python:3.10-buster

RUN pip3 install dnslib==0.9.16
COPY nonexistent_dns.py /nonexistent_dns.py

CMD ["python3", "/nonexistent_dns.py"]
