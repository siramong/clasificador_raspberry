import time
import logging

try:
    import RPi.GPIO as GPIO
except Exception:  # pragma: no cover - fallback fuera de Raspberry
    GPIO = None

try:
    import pigpio
except Exception:  # pragma: no cover - fallback fuera de Raspberry
    pigpio = None

try:
    from hx711 import HX711
except Exception:  # pragma: no cover - fallback fuera de Raspberry
    HX711 = None

logger = logging.getLogger(__name__)

HARDWARE_AVAILABLE = GPIO is not None and pigpio is not None and HX711 is not None

# ================= PINES =================
SENSOR_IR_1 = 17
SENSOR_IR_2 = 27
SENSOR_INDUCTIVO = 22

SERVO_ENTRADA = 5
SERVO_SALIDA = 6
SERVO_PLASTICO = 13
SERVO_VIDRIO = 19

if GPIO is not None:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_IR_1, GPIO.IN)
    GPIO.setup(SENSOR_IR_2, GPIO.IN)
    GPIO.setup(SENSOR_INDUCTIVO, GPIO.IN)

if pigpio is not None:
    pi = pigpio.pi()
    if not pi.connected:
        logger.warning("No se pudo conectar con pigpio. Se usará modo simulado.")
        pi = None
else:
    pi = None

if HX711 is not None:
    try:
        hx = HX711(dout_pin=23, pd_sck_pin=24)
        hx.set_reference_unit(1)
        hx.reset()
        hx.tare()
    except Exception:
        logger.exception("Error inicializando HX711. Se usará peso simulado.")
        hx = None
else:
    hx = None

# ================= FUNCIONES =================

def mover_servo(pin, pulso):
    if pi is None:
        return
    pi.set_servo_pulsewidth(pin, pulso)
    time.sleep(0.5)
    pi.set_servo_pulsewidth(pin, 0)

def leer_peso():
    if hx is None:
        return 0.0
    try:
        return float(hx.get_weight(5))
    except Exception:
        logger.exception("Fallo leyendo HX711. Retornando 0.")
        return 0.0

def leer_inductivo():
    if GPIO is None:
        return 1
    return GPIO.input(SENSOR_INDUCTIVO)

def leer_ir_entrada():
    if GPIO is None:
        return 1
    return GPIO.input(SENSOR_IR_1)

def leer_ir_salida():
    if GPIO is None:
        return 1
    return GPIO.input(SENSOR_IR_2)

def cleanup_hardware():
    if pi is not None:
        pi.stop()
    if GPIO is not None:
        GPIO.cleanup()
