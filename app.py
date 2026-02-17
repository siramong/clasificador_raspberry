from flask import Flask, render_template, Response, jsonify, request
import cv2
import joblib
import threading
import time
import os
import atexit
import logging

from services.hardware import (
    SERVO_ENTRADA,
    SERVO_SALIDA,
    SERVO_PLASTICO,
    SERVO_VIDRIO,
    mover_servo,
    leer_peso,
    leer_inductivo,
    leer_ir_entrada,
    leer_ir_salida,
    cleanup_hardware,
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= VARIABLES =================
estado = {
    "material": "Ninguno",
    "plastico": 0,
    "vidrio": 0,
    "metal": 0,
    "peso": 0.0,
    "activo": True,
}
estado_lock = threading.Lock()
camara_lock = threading.Lock()

CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
MODEL_PATH = os.getenv("MODEL_PATH", "modelo_plastico_vidrio.pkl")

cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    logger.warning("No se pudo abrir la cámara (índice %s).", CAMERA_INDEX)

try:
    modelo = joblib.load(MODEL_PATH)
    logger.info("Modelo cargado desde %s", MODEL_PATH)
except Exception:
    logger.exception("No se pudo cargar el modelo en %s. Se usará clasificación por fallback.", MODEL_PATH)
    modelo = None

# ================= IA =================
def detectar_material_ia(frame):
    if modelo is None:
        return "plastico"

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    brillo = gray.mean()
    bordes = edges.sum()

    X = [[brillo, bordes]]
    resultado = modelo.predict(X)
    return resultado[0]

# ================= LOOP PRINCIPAL =================
def loop_clasificacion():
    while True:
        with estado_lock:
            sistema_activo = estado["activo"]

        if sistema_activo and leer_ir_entrada() == 0:

            mover_servo(SERVO_ENTRADA, 1500)

            while leer_ir_salida() == 1:
                time.sleep(0.05)

            mover_servo(SERVO_ENTRADA, 500)

            if leer_inductivo() == 0:
                with estado_lock:
                    estado["material"] = "metal"
                    estado["metal"] += 1

            else:
                with camara_lock:
                    ret, frame = cap.read()

                if ret:
                    peso_actual = leer_peso()
                    material = detectar_material_ia(frame)

                    with estado_lock:
                        estado["material"] = material
                        estado["peso"] = round(peso_actual, 2)

                    if material == "plastico":
                        with estado_lock:
                            estado["plastico"] += 1
                        mover_servo(SERVO_PLASTICO, 1500)

                    elif material == "vidrio":
                        with estado_lock:
                            estado["vidrio"] += 1
                        mover_servo(SERVO_VIDRIO, 1500)
                else:
                    logger.warning("No se pudo leer frame para clasificación.")

            mover_servo(SERVO_SALIDA, 1500)
            time.sleep(1)

        time.sleep(0.02)

# ================= VIDEO STREAM =================
def generar_frames():
    while True:
        with camara_lock:
            success, frame = cap.read()

        if not success:
            time.sleep(0.1)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ================= RUTAS =================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generar_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/estado')
def estado():
    with estado_lock:
        snapshot = dict(estado)
    return jsonify(snapshot)

@app.route('/toggle', methods=['POST'])
def toggle():
    with estado_lock:
        estado["activo"] = not estado["activo"]
        activo = estado["activo"]
    return jsonify({"activo": activo})

def cleanup_resources():
    if cap.isOpened():
        cap.release()
    cleanup_hardware()

atexit.register(cleanup_resources)

# ================= MAIN =================
if __name__ == '__main__':
    hilo = threading.Thread(target=loop_clasificacion)
    hilo.daemon = True
    hilo.start()

    app.run(host='0.0.0.0', port=5000)
