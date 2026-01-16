# NeuralGuard Engine v8.8 - Enterprise Edition
import cv2
import time
import os
import base64
import threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SUBTYPES = [1, 0] 
SAVE_PATH = "Fotos"
if not os.path.exists(SAVE_PATH): os.makedirs(SAVE_PATH)

last_frame = None
camera_status = "Iniciando..."

def update_camera():
    global last_frame, camera_status
    curr = 0
    while True:
        subtype = SUBTYPES[curr % 2]
        url = f"rtsp://admin:SSmed3102@192.168.0.164:554/cam/realmonitor?channel=1&subtype={subtype}"
        cap = cv2.VideoCapture(url)
        start = time.time()
        while time.time() - start < 15:
            success, frame = cap.read()
            if success:
                camera_status = f"Online (CH {subtype})"
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                last_frame = buffer.tobytes()
            else: break
        cap.release()
        curr += 1
        time.sleep(1)

threading.Thread(target=update_camera, daemon=True).start()

@app.route('/snapshot')
@app.route('/video_feed')
def get_frame():
    if last_frame is None: return "Wait...", 503
    return Response(last_frame, mimetype='image/jpeg')

@app.route('/save_face', methods=['POST'])
def save_face():
    try:
        data = request.json
        img_b64 = data.get('image').split(',')[1]
        filename = f"face_{int(time.time())}.jpg"
        filepath = os.path.join(SAVE_PATH, filename)
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(img_b64))
        print(f">>> ROSTO SALVO: {filename}")
        return jsonify({"status": "ok", "file": filename})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/list_photos')
def list_photos():
    files = os.listdir(SAVE_PATH)
    return jsonify({"count": len(files), "latest": sorted(files)[-5:] if files else []})

@app.route('/health')
def health():
    return jsonify({"status": "bridge_ready", "camera": camera_status, "v": "8.8"})

if __name__ == "__main__":
    print("--- NEURALGUARD v8.8 ---")
    app.run(host='0.0.0.0', port=5050, threaded=True)

