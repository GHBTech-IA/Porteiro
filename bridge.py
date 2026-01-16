# NeuralGuard Engine v9.1 - Universal Stable
import cv2
import time
import os
import base64
import threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CONFIGURAÇÕES DA CÂMERA
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
    
    # Lista de tentativas comuns para Intelbras, Hikvision e Dahua
    url_patterns = [
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/cam/realmonitor?channel=1&subtype=1",
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/Streaming/Channels/102",
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/cam/realmonitor?channel=1&subtype=0",
        f"rtsp://{CAM_USER}:{CAM_PASS}@{CAM_IP}:554/live/ch0"
    ]
    
    pattern_idx = 0
    
    while True:
        url = url_patterns[pattern_idx % len(url_patterns)]
        print(f"[*] Tentando conexão: {url}")
        
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            print(f"[!] Falha no padrão {pattern_idx + 1}. Tentando outro...")
            camera_status = f"Erro no Fluxo {pattern_idx + 1}"
            pattern_idx += 1
            time.sleep(2)
            continue

        print(f"[OK] Câmera Conectada!")
        camera_status = "Online (Sinal OK)"
        
        fail_count = 0
        while fail_count < 20:
            success, frame = cap.read()
            if success:
                # Otimização de imagem para transmissão via túnel
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                last_frame = buffer.tobytes()
                fail_count = 0
            else:
                fail_count += 1
                time.sleep(0.01)
        
        print("[!] Sinal perdido. Reiniciando...")
        cap.release()
        pattern_idx += 1
        time.sleep(1)

# Inicia thread de captura em segundo plano
threading.Thread(target=update_camera, daemon=True).start()

@app.route('/video_feed')
def get_frame():
    if last_frame is None:
        return "Aguardando sinal...", 503
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
        print(f"[STORAGE] Rosto salvo: {filename}")
        return jsonify({"status": "ok", "file": filename})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "bridge_ready", 
        "camera": camera_status, 
        "v": "9.1",
        "storage_count": len(os.listdir(SAVE_PATH)) if os.path.exists(SAVE_PATH) else 0
    })

if __name__ == "__main__":
    print("\n" + "="*50)
    print("      NEURALGUARD BRIDGE v9.1 - UNIVERSAL")
    print("="*50)
    print(f"[*] Escutando em: http://0.0.0.0:5050")
    print(f"[*] Alvo: {CAM_IP}")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5050, threaded=True)


