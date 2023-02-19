from flask import Flask, request
from flask_cors import CORS
from model import main_func, generate_quiz, generate_summary
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
    
@app.route("/regen_quiz", methods=['POST'])
def regen_quiz():
    quiz = generate_quiz(request.form["transcript"])
    return json.dumps({"quiz": quiz}), 200

@app.route("/regen_summary", methods=['POST'])
def regen_summary():
    summary = generate_summary(request.form["transcript"])
    return json.dumps({"summary": summary}), 200