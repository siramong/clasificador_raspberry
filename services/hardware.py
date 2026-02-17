import RPi.GPIO as GPIO
import pigpio
from hx711 import HX711
import time

GPIO.setmode(GPIO.BCM)

# ================= PINES =================
SENSOR_IR_1 = 17
SENSOR_IR_2 = 27
SENSOR_INDUCTIVO = 22

SERVO_ENTRADA = 5
SERVO_SALIDA = 6
SERVO_PLASTICO = 13
SERVO_VIDRIO = 19

GPIO.setup(SENSOR_IR_1, GPIO.IN)
GPIO.setup(SENSOR_IR_2, GPIO.IN)
GPIO.setup(SENSOR_INDUCTIVO, GPIO.IN)

pi = pigpio.pi()

hx = HX711(dout_pin=23, pd_sck_pin=24)
hx.set_reference_unit(1)
hx.reset()
hx.tare()

# ================= FUNCIONES =================

def mover_servo(pin, pulso):
    pi.set_servo_pulsewidth(pin, pulso)
    time.sleep(0.5)
    pi.set_servo_pulsewidth(pin, 0)

def leer_peso():
    return hx.get_weight(5)

def leer_inductivo():
    return GPIO.input(SENSOR_INDUCTIVO)

def leer_ir_entrada():
    return GPIO.input(SENSOR_IR_1)

def leer_ir_salida():
    return GPIO.input(SENSOR_IR_2)
