from flask import Flask, jsonify, request
from flask_cors import CORS
from model import main_func
import json

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET', 'POST'])
def index():
    if(request.method == "POST"):
        bytesOfVideo = request.get_data()
        with open('video.mp4', 'wb') as out:
            out.write(bytesOfVideo)
        print("Processing video file.")
        transcript, summary, quiz = main_func('video.mp4')
        return json.dumps({"transcript": transcript, "summary": summary, "quiz": quiz}), 200