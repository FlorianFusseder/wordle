from flask import Flask, request, jsonify

import wordle

app = Flask(__name__)


@app.route("/", methods=['POST'])
def solve():
    if request.method == 'POST':
        if request.content_length < 110:
            json = request.get_json(force=True)
            matches, _ = wordle.find_words(json)
            return {
                'matches': matches[:10]
            }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
