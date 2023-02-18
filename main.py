from flask import Flask, send_file, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET', 'POST'])
def index():
    if(request.method == "POST"):
        bytesOfVideo = request.get_data()
        with open('video.mp4', 'wb') as out:
            out.write(bytesOfVideo)
        return "Video read"