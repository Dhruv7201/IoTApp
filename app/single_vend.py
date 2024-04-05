import RPi.GPIO as GPIO
import sys
from vend_logic import spiral_vend
from vend_logic import stepper_fow
from vend_logic import stepper_rev
#from vend_logic import stepper_vert
from boards import RPI3B
from models import VendModels
GPIO.setmode(GPIO.BCM)
import time
sensed = True
#GPIO.setwarnings(False)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.OUT)
GPIO.output(3, GPIO.LOW)
GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.LOW)
GPIO.setup(21, GPIO.IN)
GPIO.output(21, GPIO.LOW)
GPIO.setup(19, GPIO.OUT)
GPIO.output(19, GPIO.LOW)
GPIO.setup(13, GPIO.OUT)
GPIO.output(13, GPIO.LOW)
GPIO.setup(6, GPIO.OUT)
GPIO.output(6, GPIO.LOW)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, GPIO.LOW)
GPIO.setup(0, GPIO.OUT)
GPIO.output(0, GPIO.LOW)
GPIO.setup(9, GPIO.OUT)
GPIO.output(9, GPIO.LOW)
GPIO.setup(10, GPIO.OUT)
GPIO.output(10, GPIO.LOW)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, GPIO.LOW)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.LOW)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, GPIO.LOW)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)




def is_integer(value):
    if isinstance(value, int):
        return True
def set_sensor_value(channel):
    global sensed
    sensed = False


if len(sys.argv) == 3:
    lttray_list = [lttray for lttray in range(1, 5)]
    ltpartition = sys.argv[1]
    vend_qty = int(item.get('vend_qty'))
#     print(f"L&T partition :{ltpartition}")
#     print("##########################################")
#     for lttray in lttray_list:
# #         print(f"ltpartition : {ltpartition} , lttray : {lttray}")
#         param = VendModels.SpiralVend(int(ltpartition), int(lttray))
#         spiral_vend.MultiVend(vend_param=param).vend()
elif len(sys.argv) == 5:
    ltpartition = sys.argv[1]
#     print(f"{ltpartition}")
    lttray = sys.argv[2]
#     print(f"{lttray}")
    vend_qty = int(sys.argv[3])
    GUID = sys.argv[4]

    #log_file = open("/home/lt/IoTApp/logs/logs.txt", "w") 
    for i in range(0, vend_qty):
#         print(f"L&T partition : {ltpartition}, L&T tray {lttray}.")
#         print("##########################################")
        param = VendModels.SpiralVend(int(ltpartition), int(lttray), int(vend_qty), GUID)
        #logCommand = "Partition:"+str(ltpartition)+ "Tray:"+str(lttray)+"Qty:"+str(vend_qty)+"GUID:"+str(GUID)
        #log_file.write(logCommand)
        #log_file.close()
#         stepper_fow.Forward1().mov()
    
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(11, GPIO.OUT)
#         print('\nwhile before===',GPIO.input(11))
#         while(1):
#             GPIO.setmode(GPIO.BCM)
#             GPIO.setup(11, GPIO.OUT)
#             if (GPIO.input(11) == 0):
#                  break
#             time.sleep(0.01)
#             #print('\nwhile after===',GPIO.input(13))
#             
        param = VendModels.SpiralVend(int(ltpartition), int(lttray), int(vend_qty), GUID)
        
        spiral_vend.MultiVend(vend_param=param).vend()
                
        
        param = VendModels.SpiralVend(int(ltpartition), int(lttray), int(vend_qty), GUID)
#         stepper_rev.Reverse1().mov()


        def set_sensor_value(channel):
                self.sensed = True
        if sensed:
                print(f"reqid:{GUID}, status:sucess")
        else:
            print(f"reqid:{GUID}, status:failed")
        
            
else:
    print("max 2 arguments")
