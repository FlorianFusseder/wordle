import os

import waitress
from flask import Flask, request, make_response

import wordle

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def solve():
    if request.method == 'POST':
        if request.content_length < 110:
            json = request.get_json(force=True)
            matches, _ = wordle.find_words(json)
            return {
                'matches': matches[:10]
            }
    elif request.method == 'GET':
        return make_response("UP", 200)


if __name__ == '__main__':
    port = int(os.getenv("PORT", "8081"))
    print(f"Using Port: {port}")
    waitress.serve(app, port=port, url_scheme='http')
