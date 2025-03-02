from flask import Flask, request, jsonify, send_file
import os
from tasks import generate_screenshot

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <h1>歡迎來到 CeleryShot API</h1>
    <h2>可用的 API 端點：</h2>
    <ul style="font-size: 1.2em; line-height: 1.6;">
        <li><strong>POST /screenshot</strong> - 建立新的截圖任務</li>
        <li><strong>GET /task/&lt;task_id&gt;/status</strong> - 檢查任務狀態</li>
        <li><strong>GET /screenshot/&lt;filename&gt;</strong> - 下載截圖</li>
    </ul>
    <p style="margin-top: 20px;">
        使用方法：<br>
        1. 使用 POST /screenshot 並提供 URL 來建立截圖任務<br>
        2. 使用返回的 task_id 查詢任務狀態<br>
        3. 當任務完成時，使用提供的下載連結取得截圖
    </p>
    """

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
    app.run(port=8000, debug=True)
