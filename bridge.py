# NeuralGuard Bridge v9.6 - HIGH-DEFINITION EDITION
import cv2, time, os, base64, threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CONFIGURAÇÕES DA SUA CÂMERA
# Alterado para subtype=0 para pegar a resolução máxima (Main Stream)
RTSP_URL = "rtsp://admin:SSmed3102@192.168.0.164:554/cam/realmonitor?channel=1&subtype=0"
SAVE_PATH = "Fotos"

if not os.path.exists(SAVE_PATH): 
    os.makedirs(SAVE_PATH)

last_frame = None
camera_status = "Iniciando..."
capture_count = 0

def update_camera():
    global last_frame, camera_status
    print(f"[!] INICIANDO MODO HD (Subtype 0): {RTSP_URL}")
    while True:
        cap = cv2.VideoCapture(RTSP_URL)
        if not cap.isOpened():
            camera_status = "Erro RTSP"
            time.sleep(5)
            continue
        
        camera_status = "Online (HD)"
        while True:
            success, frame = cap.read()
            if not success: break
            
            # Teto aumentado para 1080p (1920px de largura)
            h, w = frame.shape[:2]
            if w > 1920:
                frame = cv2.resize(frame, (1920, int(h * (1920/w))))

            # Qualidade aumentada para 90 (Foco em detalhes faciais)
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            last_frame = buffer.tobytes()
        cap.release()
        time.sleep(1)

threading.Thread(target=update_camera, daemon=True).start()

@app.route('/video_feed')
def get_frame():
    if last_frame is None: return "Sem Sinal", 503
    return Response(last_frame, mimetype='image/jpeg')

@app.route('/health')
def health():
    return jsonify({
        "status": "bridge_v9.6_hd_ready", 
        "camera": camera_status,
        "captures_saved": capture_count
    })

@app.route('/save_face', methods=['POST'])
def save():
    global capture_count
    try:
        data = request.json
        img_b64 = data.get('image').split(',')[1]
        timestamp = int(time.time())
        fname = f"NG_HD_{timestamp}.jpg"
        
        full_path = os.path.join(SAVE_PATH, fname)
        with open(full_path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        
        capture_count += 1
        return jsonify({"status": "ok", "path": full_path})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)

