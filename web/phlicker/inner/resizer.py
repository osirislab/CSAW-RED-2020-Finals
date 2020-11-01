from flask import Flask, request, Response, abort, send_file
import io
import PIL.Image
import requests
import tempfile


MAX_SIZE = 10*1024*1024

app = Flask(__name__)
app.config.from_object('config.Prod')


@app.route("/resize")
def resize():
    url = request.args['url']

    if not url.startswith(f'http://{app.config["DOMAIN"]}'):
        abort(400)

    try:
        r = requests.get(url, stream=True)
    except Exception:
        abort(400)

    if not ('w' in request.args or 'h' in request.args):
        return Response(
            r.iter_content(chunk_size=4096),
            content_type=r.headers['Content-Type'],
        )

    with tempfile.TemporaryFile() as tmp:
        for chunk in r.iter_content(chunk_size=4096):
            tmp.write(chunk)
            if tmp.tell() > MAX_SIZE:
                abort(400)

        tmp.seek(0)

        img = PIL.Image.open(tmp)
        w, h = img.size
        if 'w' in request.args and 'h' in request.args:
            w = int(request.args['w'])
            h = int(request.args['h'])
        elif 'w' in request.args:
            ratio = int(request.args['w']) / w
            w = int(request.args['w'])
            h = int(h * ratio)
        elif 'h' in request.args:
            ratio = int(request.args['h']) / h
            w = int(w * ratio)
            h = int(request.args['h'])

        resized = img.resize((w, h))
        out = io.BytesIO()
        resized.save(out, format="png")
        out.seek(0)
        return send_file(
            out,
            mimetype='image/png',
        )


if __name__ == "__main__":
    app.run(port=8000)
