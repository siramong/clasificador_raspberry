# Sistema Inteligente de Clasificación de Materiales

## Descripción

Sistema automático desarrollado en Raspberry Pi para la clasificación de envases utilizando:

- Sensores infrarrojos
- Sensor inductivo
- Celda de carga HX711
- Servomotores
- Visión artificial con OpenCV
- Modelo de Machine Learning (scikit-learn)
- Panel web en tiempo real con Flask

---

## Requisitos de Hardware

- Raspberry Pi 4B
- Cámara USB
- Sensor IR x2
- Sensor inductivo
- Celda de carga HX711
- Servomotores
- Fuente de alimentación adecuada

---

## Instalación

1. Clonar o copiar el proyecto en la Raspberry Pi.

2. Instalar dependencias:

```bash
pip3 install -r requirements.txt
````

3. Activar servicio pigpio:

```bash
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

---

## Ejecución

```bash
python3 app.py
```

Acceder desde navegador en:

```
http://IP_RASPBERRY:5000
```

---

## Estructura del Proyecto

* `app.py` → servidor web + lógica principal
* `services/hardware.py` → control de sensores y actuadores
* `templates/index.html` → panel web
* `modelo_plastico_vidrio.pkl` → modelo entrenado
* `requirements.txt` → dependencias

---

## Funcionamiento General

1. Sensor IR detecta ingreso de objeto.
2. Servo de entrada posiciona envase.
3. Sensor inductivo detecta metal.
4. Si no es metal:

   * Se captura imagen.
   * Se extraen características (brillo y bordes).
   * Se clasifica con modelo ML.
5. Se activa servo correspondiente.
6. Panel web muestra estado en tiempo real.

---

## Notas

* El modelo `.pkl` debe estar entrenado previamente.
* Asegurarse de que los pines GPIO coincidan con la configuración física.
* Sistema diseñado para uso académico / prototipo.