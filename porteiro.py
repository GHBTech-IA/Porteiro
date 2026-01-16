
# RTSP_URL = "rtsp://admin:SSmed3102@192.168.0.164:554/cam/realmonitor?channel=1&subtype=0"
#           rtsp://usuario:senha@IP_DA_CAMERA    :554/cam/realmonitor?channel=1&subtype=0
#           rtsp://usuario:senha@IP_DA_CAMERA    :554/cam/realmonitor?channel=1&subtype=1
#
import os
import cv2
import time
import datetime
import logging
from deepface import DeepFace
from flask import Flask, Response

# Suprimir logs do TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|max_delay;5000000'

logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('deepface').setLevel(logging.ERROR)

# RTSP da câmera (teste no VLC antes) 
#RTSP_URL = "rtsp://admin:SENHA@192.168.0.164:554/cam/realmonitor?channel=1&subtype=1"
RTSP_URL = "rtsp://admin:SSmed3102@192.168.0.164:554/cam/realmonitor?channel=1&subtype=0"

OUTPUT_DIR = "Fotos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

DETECTOR_BACKEND = "retinaface"
MARGIN = 0.2

unique_faces = 0
saved_count = 0
discarded_frames = 0

app = Flask(__name__)

def open_stream(url):
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

def gen_frames():
    global unique_faces, saved_count, discarded_frames
    cap = open_stream(RTSP_URL)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            discarded_frames += 1
            print(f"[WARN] Frame inválido descartado. Total: {discarded_frames}")
            cap.release()
            time.sleep(1)
            cap = open_stream(RTSP_URL)
            continue

        # Reduzir janela em 50%
        frame = cv2.resize(frame, (int(frame.shape[1] * 0.5), int(frame.shape[0] * 0.5)))

        try:
            detections = DeepFace.extract_faces(frame, detector_backend=DETECTOR_BACKEND, enforce_detection=False)
        except Exception:
            detections = []
            discarded_frames += 1

        if detections:
            for detection in detections:
                if "facial_area" not in detection:
                    discarded_frames += 1
                    continue

                fa = detection["facial_area"]
                x, y, w, h = int(fa["x"]), int(fa["y"]), int(fa["w"]), int(fa["h"])

                area = w * h
                if w < 50 or h < 50 or area < 4000:
                    discarded_frames += 1
                    continue
                aspect_ratio = h / w
                if aspect_ratio < 0.7 or aspect_ratio > 1.6:
                    discarded_frames += 1
                    continue

                H, W = frame.shape[:2]
                x0 = max(0, int(x - w * MARGIN))
                y0 = max(0, int(y - h * MARGIN))
                x1 = min(W, int(x + w * (1 + MARGIN)))
                y1 = min(H, int(y + h * (1 + MARGIN)))

                if x1 <= x0 or y1 <= y0:
                    discarded_frames += 1
                    continue

                face_img = frame[y0:y1, x0:x1]

                gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                dark_pixels = cv2.countNonZero(cv2.inRange(gray, 0, 50))
                dark_ratio = dark_pixels / gray.size
                if dark_ratio > 0.6:
                    discarded_frames += 1
                    continue

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(OUTPUT_DIR, f"face_{unique_faces+1}_{timestamp}.jpg")
                cv2.imwrite(filename, face_img)
                saved_count += 1
                unique_faces += 1

                cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)

        else:
            discarded_frames += 1

        # HUD
        cv2.putText(frame, f"Rostos: {unique_faces}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f"Descartados: {discarded_frames}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Codificar frame como JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return '<html><body><h1>Detecção Facial</h1><img src="/video_feed"></body></html>'

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)