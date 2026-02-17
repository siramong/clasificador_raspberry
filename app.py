from flask import Flask, render_template, Response, jsonify
import cv2
import joblib
import threading
import time
from services.hardware import *

app = Flask(__name__)

# ================= VARIABLES =================
ultimo_material = "Ninguno"
contador_plastico = 0
contador_vidrio = 0
contador_metal = 0
peso_actual = 0
sistema_activo = True

cap = cv2.VideoCapture(0)
modelo = joblib.load("modelo_plastico_vidrio.pkl")

# ================= IA =================
def detectar_material_ia(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    brillo = gray.mean()
    bordes = edges.sum()

    X = [[brillo, bordes]]
    resultado = modelo.predict(X)
    return resultado[0]

# ================= LOOP PRINCIPAL =================
def loop_clasificacion():
    global ultimo_material, contador_plastico, contador_vidrio, contador_metal, peso_actual

    while True:
        if sistema_activo and leer_ir_entrada() == 0:

            mover_servo(SERVO_ENTRADA, 1500)

            while leer_ir_salida() == 1:
                time.sleep(0.05)

            mover_servo(SERVO_ENTRADA, 500)

            if leer_inductivo() == 0:
                ultimo_material = "metal"
                contador_metal += 1

            else:
                ret, frame = cap.read()
                if ret:
                    peso_actual = leer_peso()
                    material = detectar_material_ia(frame)
                    ultimo_material = material

                    if material == "plastico":
                        contador_plastico += 1
                        mover_servo(SERVO_PLASTICO, 1500)

                    elif material == "vidrio":
                        contador_vidrio += 1
                        mover_servo(SERVO_VIDRIO, 1500)

            mover_servo(SERVO_SALIDA, 1500)
            time.sleep(1)

# ================= VIDEO STREAM =================
def generar_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
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
    return jsonify({
        "material": ultimo_material,
        "plastico": contador_plastico,
        "vidrio": contador_vidrio,
        "metal": contador_metal,
        "peso": peso_actual,
        "activo": sistema_activo
    })

@app.route('/toggle')
def toggle():
    global sistema_activo
    sistema_activo = not sistema_activo
    return jsonify({"activo": sistema_activo})

# ================= MAIN =================
if __name__ == '__main__':
    hilo = threading.Thread(target=loop_clasificacion)
    hilo.daemon = True
    hilo.start()

    app.run(host='0.0.0.0', port=5000)
