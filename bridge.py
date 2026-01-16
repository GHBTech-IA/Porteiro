# NeuralGuard Bridge v9.2 - Debug Edition
import cv2, time, os, base64, threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print(">>> INICIANDO NEURALGUARD BRIDGE...")
SAVE_PATH = "Fotos"
if not os.path.exists(SAVE_PATH): os.makedirs(SAVE_PATH)

last_frame = None
camera_status = "Desconectado"

def update_camera():
    global last_frame, camera_status
    url = f"rtsp://admin:SSmed3102@192.168.0.164:554/cam/realmonitor?channel=1&subtype=1"
    print(f">>> TENTANDO CONECTAR EM: {url}")
    
    while True:
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            print(">>> ERRO: NAO FOI POSSIVEL ABRIR O FLUXO RTSP. VERIFIQUE IP/SENHA.")
            camera_status = "Erro RTSP"
            time.sleep(5)
            continue
        
        print(">>> CONEXAO RTSP ESTABELECIDA COM SUCESSO!")
        camera_status = "Online"
        while True:
            success, frame = cap.read()
            if not success:
                print(">>> AVISO: FALHA AO LER FRAME.")
                break
            _, buffer = cv2.imencode('.jpg', frame)
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
    return jsonify({"status": "bridge_ready", "camera": camera_status})

@app.route('/save_face', methods=['POST'])
def save():
    try:
        img_data = request.json.get('image').split(',')[1]
        fname = f"face_{int(time.time())}.jpg"
        with open(os.path.join(SAVE_PATH, fname), "wb") as f:
            f.write(base64.b64decode(img_data))
        print(f">>> ROSTO SALVO: {fname}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f">>> ERRO AO SALVAR: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)


