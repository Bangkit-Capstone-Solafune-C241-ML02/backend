from flask import Flask, jsonify, request
import os
import socket

host_name = socket.gethostname()
ip_address = socket.gethostbyname(host_name)

app = Flask(__name__)


@app.route("/")
def home():
    return "App is running"


if __name__ == "__main__":
    app.run(host=ip_address, port=5000)