# Sistema Inteligente de Clasificación de Materiales

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Raspberry Pi](https://img.shields.io/badge/Hardware-RaspberryPi-red)
![License](https://img.shields.io/badge/License-MIT-green)

Sistema automático para clasificación de envases en Raspberry Pi usando sensores, visión artificial y un modelo de Machine Learning, con panel web en tiempo real.

## Características

- Detección de presencia con sensores infrarrojos
- Detección de metal con sensor inductivo
- Medición de peso con HX711
- Clasificación plástico/vidrio con OpenCV + modelo scikit-learn
- Accionamiento de servomotores para desvío de material
- Panel web de monitoreo y control (`/`)

## Requisitos

### Hardware (producción)

- Raspberry Pi (recomendado: 4B)
- Cámara USB
- 2 sensores IR
- 1 sensor inductivo
- Celda de carga + módulo HX711
- Servomotores
- Fuente de alimentación adecuada

### Software

- Python 3.9+
- `pip`
- `pigpiod` habilitado en Raspberry Pi

## Instalación

1. Clona o copia este proyecto en la Raspberry Pi.
2. (Opcional) Crea un entorno virtual.
3. Instala dependencias:

```bash
pip3 install -r requirements.txt
```

4. Habilita y levanta `pigpiod`:

```bash
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

## Ejecución

```bash
python3 app.py
```

Luego abre en el navegador:

```text
http://IP_RASPBERRY:5000
```

## Variables de entorno

Permiten ajustar cámara y modelo sin tocar código:

- `CAMERA_INDEX`: índice de cámara OpenCV (por defecto `0`)
- `MODEL_PATH`: ruta al archivo `.pkl` (por defecto `modelo_plastico_vidrio.pkl`)

### Linux/macOS

```bash
export CAMERA_INDEX=0
export MODEL_PATH=modelo_plastico_vidrio.pkl
python3 app.py
```

### Windows PowerShell

```powershell
$env:CAMERA_INDEX = "0"
$env:MODEL_PATH = "modelo_plastico_vidrio.pkl"
python app.py
```

## Modo desarrollo (sin hardware)

El proyecto puede ejecutarse fuera de Raspberry Pi en modo simulado:

- Si no están disponibles `RPi.GPIO`, `pigpio` o `hx711`, no se detiene la app.
- Si no se encuentra el modelo, se aplica un fallback de clasificación.
- Es útil para validar interfaz web y endpoints.

## Endpoints

- `GET /` → panel principal
- `GET /video` → stream MJPEG
- `GET /estado` → estado actual del sistema (JSON)
- `POST /toggle` → activa/desactiva la clasificación

## Estructura del proyecto

- `app.py` → servidor Flask y lógica principal
- `services/hardware.py` → integración de sensores/actuadores
- `templates/index.html` → panel web
- `requirements.txt` → dependencias
- `modelo_plastico_vidrio.pkl` → modelo entrenado (no incluido por defecto)

## Flujo general

1. Sensor IR de entrada detecta objeto.
2. Servo de entrada posiciona envase.
3. Sensor inductivo verifica si es metal.
4. Si no es metal, se captura imagen y se clasifica (plástico/vidrio).
5. Se acciona el servo correspondiente.
6. Se actualiza el panel con contadores, material y peso.

## Solución de problemas rápida

- Cámara no abre: revisa `CAMERA_INDEX` y permisos de dispositivo.
- Error con servos: confirma `pigpiod` activo (`systemctl status pigpiod`).
- Peso incorrecto: recalibra HX711 (`set_reference_unit`) según tu celda.
- No carga el modelo: verifica `MODEL_PATH` y compatibilidad de `joblib/scikit-learn`.

## Notas

- Proyecto orientado a prototipo/uso académico.
- Verifica que el pinout GPIO coincida con tu cableado real.