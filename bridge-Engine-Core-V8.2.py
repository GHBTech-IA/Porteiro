import cv2
import time
import os
import base64
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CONFIGURAÇÕES
RTSP_URL = "rtsp://admin:admin123@192.168.0.164:554/cam/realmonitor?channel=1&subtype=0"
SAVE_PATH = "Fotos"

# Garante que a pasta exista
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

last_frame = None

def update_camera():
    global last_frame
    cap = cv2.VideoCapture(RTSP_URL)
    while True:
        success, frame = cap.read()
        if success:
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            last_frame = buffer.tobytes()
        else:
            time.sleep(1)
            cap = cv2.VideoCapture(RTSP_URL)

import threading
threading.Thread(target=update_camera, daemon=True).start()

# ROTA COMPATÍVEL COM V7.1 E V8.0
@app.route('/')
@app.route('/video_feed')
@app.route('/snapshot')
def get_frame():
    if last_frame is None:
        return "Aguardando camera...", 503
    return Response(last_frame, mimetype='image/jpeg')

@app.route('/save_face', methods=['POST'])
def save_face():
    try:
        data = request.json
        img_b64 = data.get('image').split(',')[1]
        filename = f"face_{int(time.time())}.jpg"
        with open(os.path.join(SAVE_PATH, filename), "wb") as f:
            f.write(base64.b64decode(img_b64))
        print(f">>> FOTO SALVA EM {SAVE_PATH}/{filename}")
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "bridge_ready"})

if __name__ == "__main__":
    print(">>> ENGINE v8.2 - ESTABILIDADE V7.1 RESTAURADA")
    print(">>> AGUARDANDO CONEXOES NA PORTA 5050...")
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)