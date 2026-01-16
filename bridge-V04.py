# NeuralGuard Engine v8.6 - Diagnóstico Ativo
import cv2
import time
import os
import base64
import threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Usando subtype=1 (Sub-stream) para maior fluidez
RTSP_URL = "rtsp://admin:SSmed3102@192.168.0.164:554/cam/realmonitor?channel=1&subtype=0"
SAVE_PATH = "Fotos"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

last_frame = None
camera_status = "Iniciando..."

def update_camera():
    global last_frame, camera_status
    print(f">>> TENTANDO CONECTAR EM: {RTSP_URL}")
    cap = cv2.VideoCapture(RTSP_URL)
    
    while True:
        success, frame = cap.read()
        if success:
            camera_status = "Conectado"
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            last_frame = buffer.tobytes()
        else:
            camera_status = "Erro: Falha ao ler stream (Verifique IP/Senha)"
            print(f"!!! {camera_status}")
            time.sleep(5)
            cap = cv2.VideoCapture(RTSP_URL)

threading.Thread(target=update_camera, daemon=True).start()

@app.route('/')
@app.route('/video_feed')
@app.route('/snapshot')
def get_frame():
    if last_frame is None: 
        return f"Erro na Camera: {camera_status}", 503
    return Response(last_frame, mimetype='image/jpeg')

@app.route('/save_face', methods=['POST'])
def save_face():
    try:
        data = request.json
        img_b64 = data.get('image').split(',')[1]
        filename = f"face_{int(time.time())}.jpg"
        with open(os.path.join(SAVE_PATH, filename), "wb") as f:
            f.write(base64.b64decode(img_b64))
        return jsonify({"status": "ok"})
    except: return jsonify({"status": "error"}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "bridge_ready",
        "camera": camera_status,
        "engine": "v8.6"
    })

if __name__ == "__main__":
    print("------------------------------------------")
    print("   NEURALGUARD ENGINE v8.6 - DIAGNÓSTICO  ")
    print("------------------------------------------")
    print(">>> FLASK: http://0.0.0.0:5050")
    print(">>> PASTA DE FOTOS: " + os.path.abspath(SAVE_PATH))
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)

