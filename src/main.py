import json
import time
import queue
import threading
from flask import Flask, request, jsonify
from fediverse_task_fetcher import FediverseTaskFetcher
from fediverse_task_reposter import FediverseTaskReposter
from flask_cors import CORS
from mastodon_util import MastodonUtil
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allows all origins

# Local queues for tasks and results
task_queue = queue.Queue()
result_queue = queue.Queue()

def post_to_queue(task_data):
    """Posts the fetched task to a local queue, including the original post."""
    task_queue.put(task_data)
    print(f"Task enqueued: {task_data}")

def task_worker():
    """Processes tasks from the queue (mock function)."""
    while True:
        task_data = task_queue.get()
        if task_data is None:
            break

        completed_task = task_data["tasks"].pop(0)
        processed_value = task_data['value'].upper()  # Mock task processing

        task_result = {
            "author": task_data["author"],
            "result": processed_value,
            "remaining_tasks": task_data["tasks"] if task_data["tasks"] else None
        }

        result_queue.put(task_result)
        print(f"Task processed: {task_result}")
        task_queue.task_done()
        time.sleep(1)

def subscribe_to_topic():
    """Listens for processed results and sends them to Mastodon."""
    reposter = FediverseTaskReposter()
    print("Subscribed to topic. Listening for task results...")
    while True:
        result = result_queue.get()
        if result is None:
            break
        reposter.send_result(result)
        result_queue.task_done()
        time.sleep(1)

def fetch_tasks_from_fediverse():
    """Fetches new tasks from the Fediverse and adds them to the queue."""
    fetcher = FediverseTaskFetcher()
    print("Listening for tasks from the Fediverse...")
    while True:
        print("Start fetch ...")
        posts = fetcher.fetch_posts()
        for post in posts:
            try:
                post_to_queue(post)
            except json.JSONDecodeError:
                print(f"Skipping invalid task format from {post['author']}")
        time.sleep(30)  # Poll every 30 seconds

@app.route("/send_prompt", methods=["POST"])
def send_prompt():
    """Receives prompt from frontend and adds it to task queue."""
    data = request.json
    task_id = str(len(task_queue.queue) + 1)
    task_entry = {"id": task_id, "tasks": data["tasks"], "value": data["value"], "options": data["options"], "author": "frontend_user"}
    mastodonUtil = MastodonUtil()
    target_hashtag = os.getenv("FETCH_HASHTAG", "hyperloop")
    mastodonUtil.post_status(json.dumps(task_entry) + str(f"#{target_hashtag}"))
    print(f"Task send to Mastodon: {task_entry}")
    return jsonify({"message": "Task received", "task_id": task_id})

@app.route("/get_result", methods=["POST"])
def get_result():
    """Fetches processed results for frontend."""
    if not result_queue.empty():
        result = result_queue.get()
        return jsonify(result)
    return jsonify({"result": None})

if __name__ == "__main__":
    # Start worker threads
    threading.Thread(target=task_worker, daemon=True).start()
    threading.Thread(target=subscribe_to_topic, daemon=True).start()
    threading.Thread(target=fetch_tasks_from_fediverse, daemon=True).start()  # Regularly fetches new Fediverse tasks
    app.run(debug=True)
