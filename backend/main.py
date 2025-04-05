# app.py
from flask import Flask, request, jsonify
from mastodon import Mastodon
from flask_cors import CORS
import queue
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
q = queue.Queue()

# Set up Mastodon API
mastodon_client = Mastodon(
    access_token=os.getenv("ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL")  # change if using other instance
)

@app.route("/send_prompt", methods=["POST"])
def send_prompt():
    data = request.json
    prompt = data.get("value")
    hashtag = data.get("hashtag")

    if not prompt or not hashtag:
        return jsonify({"error": "Missing data"}), 400

    toot_text = f"{prompt} {hashtag}"
    mastodon_client.status_post(toot_text)

    return jsonify({"status": "Posted"}), 200

@app.route("/receive_reply", methods=["POST"])
def receive_reply():
    data = request.json
    reply_content = data.get("content")
    if reply_content:
        q.put(reply_content)
    return jsonify({"status": "received"}), 200

@app.route("/get_result")
def get_result():
    if not q.empty():
        return jsonify({"result": q.get(), "loops": []})
    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True)
