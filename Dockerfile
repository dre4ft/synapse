FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean  # Installe Python, pip et venv

WORKDIR /root/

COPY . .

RUN python3 -m venv backend_venv

RUN backend_venv/bin/pip install -r backend/requirements.txt

EXPOSE 80

CMD ["backend_venv/bin/python3", "backend/main.py"]
