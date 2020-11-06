#!/usr/bin/env python
import json
import socket
import tempfile
from base64 import b64encode
from subprocess import check_output
from urllib.parse import urlparse, urlunparse

import requests
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config["BOOTSTRAP_SERVE_LOCAL"] = True
bootstrap = Bootstrap(app)

MAX_FILE_SIZE = 3000000  # 3 MB


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        link = request.form.get("link").strip()

        output = ""


        if link:
            parsed_link = urlparse(link)

            try:
                hostname = parsed_link.netloc.split(":")[0]
                dns = socket.gethostbyname(hostname)
            except:
                dns = None

            #replace url with ec2 mock
            if parsed_link.netloc == "169.254.169.254" or dns == "169.254.169.254":
                parsed_link = parsed_link._replace(netloc="localhost:1338")
                link = urlunparse(parsed_link)

            # check file size
            if (
                int(
                    requests.get(link, stream=True).headers.get(
                        "content-length"
                    )
                )
                >= MAX_FILE_SIZE
            ):
                output = "File too large. Refusing to process."
                image = b64encode(b"Invalid File").decode("utf-8")
                return render_template("index.html", output=output, image=image)

            content = requests.get(link).content

            with tempfile.NamedTemporaryFile() as f:
                f.seek(0)
                f.write(content)
                file_name = f.name
                try:
                    output = check_output(["exiftool", file_name]).decode("utf-8")
                except:
                    output = "Invalid URL"
                f.close()

            image = b64encode(content).decode("utf-8")

        else:
            return render_template("index.html")

        return render_template("index.html", output=output, image=image)

    elif request.method == "GET":
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
