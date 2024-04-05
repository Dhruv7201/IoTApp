import sqlite3
from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
from vend_logic import spiral_vend
from vend_logic import stepper_fow
from vend_logic import stepper_rev
from models import VendModels
# import pyautogui
import time

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
DB_FILE = 'db/iot_db'

sensed = True
GPIO.setwarnings(False)


def create_connection():
    try:
        connection = sqlite3.connect(DB_FILE)
        print("Connection to SQLite DB successful")
        return connection
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred while connecting to the SQLite database")
        return None


def execute_sql(connection, sql):
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        print("SQL executed successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred while executing the SQL statement")


def is_exist(item, quantity):
    print("data = ", item, quantity)
    if item == 'apple':
        item = 1
    elif item == 'pineapple':
        item = 2
    elif item == 'coconut':
        item = 3
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            select_query = "SELECT * FROM product WHERE name = ? AND quantity >=?;"
            cursor.execute(select_query, (item, quantity))
            result = cursor.fetchone()
            print("quantity in db = ", result)
            if result:
                return True
            else:
                print("Item not found in the database")
                return False

        except sqlite3.Error as e:
            print(f"The error '{e}' occurred while executing the SQL query")

        finally:
            cursor.close()
            connection.close()


def is_integer(value):
    if isinstance(value, int):
        return True


def set_sensor_value(channel):
    global sensed
    sensed = False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # pyautogui.press("f11")
        return render_template('main_page.html')
    else:
        return render_template('main_page.html')


@app.route('/vend', methods=['POST'])
def handle_order():
    apple_qty = int(request.form.get('apple'))
    pineapple_qty = int(request.form.get('pineapple'))
    coconut_qty = int(request.form.get('coconut'))

    if apple_qty > 0:
        result = is_exist("apple", apple_qty)
    elif pineapple_qty > 0:
        result = is_exist("pineapple", pineapple_qty)
    elif coconut_qty > 0:
        result = is_exist("coconut", coconut_qty)
    else:
        return render_template('main_page.html')

    if result:
        print("result = ", result)
        return render_template('paytm.html')
    else:
        return render_template('error.html')
    print(button, quantity)
    json_data = {
        "product_id": 0,
        "tray_id": 0,
        "status": 0,
        "partition_no": 0,
        "quantity": 0
    }
    # check the length of jason_data
    if len(json_data) == 4:
        ltpartition = json_data['partition_no']
        lttray = json_data['tray_id']
        vend_qty = json_data['quantity']
        GUID = json_data['status']
        for i in range(0, vend_qty):
            param = VendModels.SpiralVend(int(ltpartition), int(lttray), int(vend_qty), GUID)
            stepper_fow.Forward1().mov()
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(12, GPIO.OUT)
            print('\nwhile before===', GPIO.input(12))
            while (1):
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(12, GPIO.OUT)
                if (GPIO.input(12) == 0):
                    break
                time.sleep(0.01)

            param = VendModels.SpiralVend(int(ltpartition), int(lttray), int(vend_qty), GUID)

            spiral_vend.MultiVend(vend_param=param).vend()

            param = VendModels.SpiralVend(int(ltpartition), int(lttray), int(vend_qty), GUID)
            stepper_rev.Reverse1().mov()

            def set_sensor_value(channel):
                self.sensed = True

            if sensed:
                print(f"reqid:{GUID}, status:sucess")
            else:
                print(f"reqid:{GUID}, status:failed")


    else:
        print("max 2 arguments")

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    port = 5000
    app.run(port=port, debug=True)
