import cv2
import time
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CONFIGURACOES RTSP
RTSP_URL = "rtsp://admin:SSmed3102@192.168.0.164:554/cam/realmonitor?channel=1&subtype=0"

def generate_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.5)
            cap = cv2.VideoCapture(RTSP_URL)
            continue
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/health')
def health():
    return jsonify({"status": "bridge_ready", "version": "6.9", "port": 5050})

if __name__ == "__main__":
    print("--- NEURALGUARD ENGINE v6.9 ---")
    print("PORTA: 5050 | STATUS: AGUARDANDO")
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True)
