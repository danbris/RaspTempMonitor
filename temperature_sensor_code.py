import os
import glob
import time
import datetime
import atexit
import RPi.GPIO as GPIO
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


def led_on():
    print("LED on")
    GPIO.output(18, GPIO.HIGH)


@atexit.register
def led_off():
    print("LED off")
    GPIO.output(18, GPIO.LOW)


with open('temperature_history.csv', mode='w') as csv_file:
    employee_writer = csv.writer(
        csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)


def sendEmail(temp):
    print("Send an email with the exceeded temperature!")


def monitor():
    temp = read_temp()
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(temp, timestamp)
    with open('temperature_history.csv', mode='a') as csv_file:
        employee_writer = csv.writer(
            csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow([temp, timestamp])
    if temp > 26:
        led_on()
    else:
        led_off()
    if temp > 30:
        sendEmail(temp)
    time.sleep(10)


def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)


# execution start
while True:
    monitor()
