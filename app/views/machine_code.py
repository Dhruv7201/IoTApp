from flask import Blueprint, request, jsonify
from app import app, create_connection, generate_order_id, machine_id, item_id, order_id, transaction_id
import json
from app.models import VendModels
from app.methods import insert_order, update_order, update_partition, update_product
import RPi.GPIO as GPIO
from app import spiral_vend


machine_code = Blueprint('machine_code', __name__)

@machine_code.route('/machine_code', methods=['GET'])
def machine_code():
    global item_id
    global order_id
    global transaction_id
    try:
        form_data = request.args.get('dataJson')
        json_data = request.args.get('product_key')
        log_message = 'Data of Ajex call = {}'.format(form_data)
        app.logger.info(log_message)
        form_data = json.loads(form_data)
        partition_no = form_data['partition_no']
        tray_no = form_data['tray_no']
        ltpartition = form_data['partition_no']
        lttray = form_data['tray_no']
        vend_qty = form_data['quantity']
        failed_list = []
        success_list = []
        failed_count = 0
        success_count = 0
        connection = create_connection()
        cursor = connection.cursor()
        if json_data == 'product_1':
            item_id = 1
        elif json_data == 'product_2':
            item_id = 2
        elif json_data == 'product_3':
            item_id = 3
        elif json_data == 'product_4':
            item_id = 4
        elif json_data == 'product_5':
            item_id = 5
        GUID = 1
        product_price = "SELECT price_per_quantity from product WHERE name =%s and machine_id= %s;"
        cursor.execute(product_price, (item_id, machine_id))
        product_price = cursor.fetchone()
        product_price = product_price[0]
        list_main = [lttray, ltpartition, vend_qty, GUID]
        log_message = 'Data of Ajax call = {}'.format(list_main)
        app.logger.info(log_message)
        if len(list_main) == 3:
            lttray_list = [lttray for lttray in range(1, 5)]
            ltpartition = list_main[1]
            # vend_qty = int(item.get('vend_qty'))
        elif len(list_main) == 4:

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(3, GPIO.OUT)
            GPIO.output(3, GPIO.LOW)
            GPIO.setup(2, GPIO.OUT)
            GPIO.output(2, GPIO.LOW)
            GPIO.setup(21, GPIO.IN)

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

            ltpartition = list_main[0]
            lttray = list_main[1]
            GUID = list_main[3]
            count = 0
            for i in range(0, vend_qty):
                cursor = connection.cursor()
                insert_order(cursor, order_id, transaction_id, item_id, tray_no, partition_no, product_price, machine_id)
                connection.commit()
                last_row_id = cursor.lastrowid
                last_row_id = int(last_row_id)

                param = VendModels.SpiralVend(int(ltpartition), int(lttray), int(vend_qty), GUID)
                GPIO.setwarnings(False)  # Ignore warning for now
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                data = spiral_vend.MultiVend(vend_param=param).vend()
                dwnSensorFlag = data['detection_sensor_data']
                vending_info = data['vending_info']
                app.logger.info('vending_info = {}'.format(vending_info))
                app.logger.info('sensor data = {}'.format(dwnSensorFlag))
                # dwnSensorFlag = True

                if dwnSensorFlag is False:  # response from down sensor = dwnSensorFlag
                    failed_count += 1
                    failed_json = {'product_id': item_id, 'order_id': order_id, 'tray_no': lttray,
                                   'partition_no': ltpartition}
                    count = count + 1
                    failed_list.append(failed_json)
                else:
                    success_count += 1
                    success_json = {'product_id': item_id, 'order_id': order_id, 'tray_no': lttray,
                                    'partition_no': ltpartition}
                    update_order(last_row_id, machine_id, cursor)
                    connection.commit()
                    update_partition(item_id, partition_no, tray_no, machine_id, cursor)
                    connection.commit()
                    count = count + 1
                    update_product(item_id, machine_id, cursor)
                    connection.commit()
                    success_list.append(success_json)

        data = {"success": "success", 'failed_count': failed_count, 'success_count': success_count, 'item_id': item_id}
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(data)
    except Exception as e:
        print(e)
        data = {"success": "fail"}
        return jsonify(data)