from flask import Flask, request, jsonify, send_file
import os
from tasks import generate_screenshot

app = Flask(__name__)

@app.route("/screenshot", methods=["POST"])
def create_screenshot():
    data = request.json
    task = generate_screenshot.delay(data["url"])
    return jsonify({"task_id": task.id})

@app.route("/task/<task_id>/status")
def task_status(task_id):
    from celery_app import celery  # 這裡懶得初始化
    task = celery.AsyncResult(task_id)
    if task.state == "SUCCESS":
        return jsonify({"status": task.state, "download_url": f"/screenshot/{task_id}.png"})
    return jsonify({"status": task.state})

@app.route("/screenshot/<filename>")
def get_screenshot(filename):
    file_path = os.path.join("screenshots", filename)
    return send_file(file_path, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
