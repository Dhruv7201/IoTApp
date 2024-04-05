from RPi import GPIO
import time
from boards import RPI3B
import threading
from datetime import datetime
import logging


class MultiVend(object):
    def __init__(self, vend_param, device_stat=None, final_item=False):
        self.device_stat = device_stat
        self.final_item = final_item
        if device_stat:
            self.device_stat.is_ready = False
            self.device_stat.save()
        self.vend_param = vend_param
        self.sensed = False

    def vend(self):
        GPIO.setmode(GPIO.BCM)
        negative = RPI3B.get_negative_list()[int(self.vend_param.lttray_no) - 1]
        positive = RPI3B.get_positive_list()[int(self.vend_param.ltpartition_no) - 1]
        #         log_file = open("/home/lt/IoTApp/logs/logs.txt", "a")
        #         logCommand = "\nnegative :"+ str(negative) + " positive : " + str(positive) + "===>" + str(datetime.now())
        #         log_file.write(logCommand)
        #         log_file.close()
        print(f"negative : {negative} , positive : {positive}")
        vending_info = f'negative : {negative} , positive : {positive}'
        #         sensor = RPI3B.vendingSensor
        #         push_led = RPI3B.additionalSensor1
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(negative, GPIO.OUT)
        GPIO.setup(positive, GPIO.OUT)
        #        GPIO.setup(push_led, GPIO.OUT)
        #         GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

        if not negative == RPI3B.negative1:
            GPIO.setup(RPI3B.negative1, GPIO.OUT)

        if not negative == RPI3B.negative2:
            GPIO.setup(RPI3B.negative2, GPIO.OUT)

        def set_sensor_value(channel):
            self.sensed = True
            # print(f"Sensed{self.sensed}")

        GPIO.setmode(GPIO.BCM)
        #         GPIO.add_event_detect(sensor, GPIO.RISING, callback=set_sensor_value, bouncetime=40)
        time.sleep(1)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(negative, GPIO.OUT)
        GPIO.output(negative, GPIO.HIGH)
        GPIO.setup(positive, GPIO.OUT)
        GPIO.output(positive, GPIO.HIGH)
        detection_sensor_data = False
        # time.sleep(2.5)
        duration = 2.5
        count = 1
        end_time = time.time() + duration
        while time.time() < end_time:
            # Perform your desired actions inside the loop
            if GPIO.input(21) == 1:
                print("Sensor detected")
                detection_sensor_data = True
                time.sleep(0.1)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(negative, GPIO.OUT)
        GPIO.output(negative, GPIO.LOW)

        # time.sleep(7)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(21, GPIO.IN)
        duration = 7
        count = 1
        end_time = time.time() + duration
        while time.time() < end_time:
            # Perform your desired actions inside the loop
            if GPIO.input(21) == 1:
                print("Sensor detected")
                detection_sensor_data = True
                time.sleep(0.1)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(positive, GPIO.OUT)
        GPIO.output(positive, GPIO.LOW)
        # time.sleep(3)
        duration = 3
        count = 1
        end_time = time.time() + duration
        while time.time() < end_time:
            # Perform your desired actions inside the loop
            if GPIO.input(21) == 1:
                print("Sensor detected")
                detection_sensor_data = True
                time.sleep(0.1)
        data = {
            "vend": True,
            "vending_info": vending_info,
            "sensing": self.sensed,
            "detection_sensor_data": detection_sensor_data
        }
        if self.device_stat:
            self.device_stat.is_ready = True
            self.device_stat.save()

        if self.final_item:
            #             print("final item")
            t = threading.Thread(target=blink_led, args=[push_led, ])
            t.setDaemon(False)
            t.start()
        else:

            return data
