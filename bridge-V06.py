# NeuralGuard Engine v8.9 - Universal RTSP Diagnostic Edition
import cv2
import time
import os
import base64
import threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CONFIGURAÇÕES INJETADAS
CAM_USER = "admin"
CAM_PASS = "SSmed3102"
CAM_IP = "192.168.0.164"
SAVE_PATH = "Fotos"

if not os.path.exists(SAVE_PATH): 
    os.makedirs(SAVE_PATH)

last_frame = None
camera_status = "Iniciando..."

def update_camera():
    global last_frame, camera_status
    
    # Formatos de URL para testar (Dahua, Hikvision, Genérico)
    url_patterns = [
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/cam/realmonitor?channel=1&subtype=1",
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/cam/realmonitor?channel=1&subtype=0",
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/Streaming/Channels/102",
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/live/ch0"
    ]
    
    pattern_idx = 0
    
    while True:
        url = url_patterns[pattern_idx % len(url_patterns)]
        print(f"[*] Tentando: {url}")
        
        # CAP_FFMPEG é essencial no Ubuntu para evitar falhas de codec
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            camera_status = f"Erro no Padrão {pattern_idx + 1}"
            print(f"[!] Falha. Tentando próximo padrão em 3s...")
            pattern_idx += 1
            time.sleep(3)
            continue

        print(f"[OK] Conectado! Usando: {url}")
        camera_status = "Online (Sinal OK)"
        
        fail_count = 0
        while fail_count < 10:
            success, frame = cap.read()
            if success:
                # Redimensionar para 720p se for muito grande para economizar banda do túnel
                if frame.shape[1] > 1280:
                    frame = cv2.resize(frame, (1280, 720))
                    
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                last_frame = buffer.tobytes()
                fail_count = 0
            else:
                fail_count += 1
                time.sleep(0.1)
        
        print("[!] Stream interrompido. Reiniciando busca...")
        cap.release()
        pattern_idx += 1
        time.sleep(1)

threading.Thread(target=update_camera, daemon=True).start()

@app.route('/snapshot')
@app.route('/video_feed')
def get_frame():
    if last_frame is None:
        return "Aguardando sinal da camera...", 503
    return Response(last_frame, mimetype='image/jpeg')

@app.route('/save_face', methods=['POST'])
def save_face():
    try:
        data = request.json
        img_data = data.get('image').split(',')[1]
        filename = f"face_{int(time.time())}.jpg"
        filepath = os.path.join(SAVE_PATH, filename)
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(img_data))
        print(f"[DISK] Evidência salva: {filename}")
        return jsonify({"status": "ok", "file": filename})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "bridge_ready", 
        "camera": camera_status, 
        "v": "8.9",
        "storage": len(os.listdir(SAVE_PATH)) if os.path.exists(SAVE_PATH) else 0
    })

if __name__ == "__main__":
    print("\n" + "="*50)
    print("      NEURALGUARD BRIDGE v8.9 - UNIVERSAL")
    print("="*50)
    print(f"[*] Escutando em: http://0.0.0.0:5050")
    print(f"[*] Alvo: {CAM_IP}")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5050, threaded=True)
