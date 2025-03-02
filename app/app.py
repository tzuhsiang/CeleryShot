from flask import Flask, request, jsonify, send_file
import os
from tasks import generate_screenshot

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CeleryShot - 網頁截圖服務</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .input-group { margin: 20px 0; }
            input[type="url"] { width: 70%; padding: 8px; }
            button { padding: 8px 15px; background: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            #result { margin-top: 20px; padding: 10px; border: 1px solid #ddd; display: none; }
            .loading { display: none; }
        </style>
    </head>
    <body>
        <h1>歡迎來到 CeleryShot</h1>
        <p>輸入網址來獲取網頁截圖</p>
        
        <div class="input-group">
            <input type="url" id="urlInput" placeholder="請輸入網址 (例如: https://www.example.com)" required>
            <button onclick="takeScreenshot()">取得截圖</button>
        </div>
        
        <div id="result">
            <p>任務狀態: <span id="taskStatus">等待中...</span></p>
            <p id="downloadLink" style="display: none">
                <a href="#" target="_blank">下載截圖</a>
            </p>
        </div>

        <script>
        async function takeScreenshot() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                alert('請輸入有效的網址');
                return;
            }

            document.getElementById('result').style.display = 'block';
            document.getElementById('taskStatus').textContent = '處理中...';
            document.getElementById('downloadLink').style.display = 'none';

            try {
                // 建立截圖任務
                const response = await fetch('/screenshot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                const data = await response.json();
                const taskId = data.task_id;

                // 定期檢查任務狀態
                const checkStatus = async () => {
                    const statusResponse = await fetch(`/task/${taskId}/status`);
                    const statusData = await statusResponse.json();
                    document.getElementById('taskStatus').textContent = statusData.status;

                    if (statusData.status === 'SUCCESS') {
                        document.getElementById('downloadLink').style.display = 'block';
                        document.getElementById('downloadLink').querySelector('a').href = statusData.download_url;
                        document.getElementById('downloadLink').querySelector('a').textContent = '點擊此處下載截圖';
                    } else {
                        setTimeout(checkStatus, 2000);  // 每2秒檢查一次
                    }
                };

                checkStatus();
            } catch (error) {
                document.getElementById('taskStatus').textContent = '發生錯誤: ' + error.message;
            }
        }
        </script>
    </body>
    </html>
    """

@app.route("/screenshot", methods=["POST"])
def create_screenshot():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "未提供 URL"}), 400
    
    if not data["url"].startswith(('http://', 'https://')):
        return jsonify({"error": "無效的 URL 格式"}), 400

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
