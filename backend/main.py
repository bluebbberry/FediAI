from flask import Flask, request, jsonify
from flask_cors import CORS
import mastodon
import queue
import threading
import time
import re
import os
from dotenv import load_dotenv
from mastodon import Mastodon

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

# Store sent posts + replies we've already seen
sent_posts = []  # Each entry: {"id": post_id, "seen_replies": set(reply_ids)}

@app.route("/send_prompt", methods=["POST"])
def send_prompt():
    data = request.json
    prompt = data.get("value")
    hashtag = data.get("hashtag")

    if not prompt or not hashtag:
        return jsonify({"error": "Missing data"}), 400

    toot_text = f"{prompt} {hashtag}"
    post = mastodon_client.status_post(toot_text)

    sent_posts.append({
        "id": int(post["id"]),
        "seen_replies": set()
    })

    return jsonify({"status": "Posted"}), 200

@app.route("/get_result")
def get_result():
    if not q.empty():
        return jsonify({"result": q.get(), "loops": []})
    return jsonify({})

def strip_html(raw_html):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', raw_html)

def listen_for_replies():
    while True:
        try:
            for post in sent_posts:
                post_id = post["id"]
                seen_replies = post["seen_replies"]

                context = mastodon_client.status_context(post_id)
                descendants = context.get("descendants", [])

                for reply in descendants:
                    reply_id = int(reply["id"])
                    if reply_id not in seen_replies:
                        reply_text = strip_html(reply["content"])
                        q.put(reply_text)
                        seen_replies.add(reply_id)
                        print(f"💬 New reply to {post_id}: {reply_text}")

        except Exception as e:
            print(f"❌ Error checking replies: {e}")

        time.sleep(5)

# Start reply checking thread
threading.Thread(target=listen_for_replies, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
