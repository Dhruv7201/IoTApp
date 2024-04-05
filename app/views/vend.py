from flask import Blueprint, render_template, request, redirect, make_response
from app import app, get_machine_id, create_connection, generate_order_id, mid, key, businessType, posId, url, product_1_qty, product_2_qty, product_3_qty, product_4_qty, product_5_qty, clientId
import requests
import json
import pyqrcode
from app import PaytmChecksum


vend = Blueprint('vend', __name__)



@vend.route('/vend', methods=['GET'])
def handle_order():
    global product_1_qty, product_2_qty, product_3_qty, product_4_qty, product_5_qty
    filtered_result = []
    paytmParams = dict()
    machine_id, dev = get_machine_id()
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = "SELECT price_per_quantity FROM product WHERE machine_id=%s;"
        cursor.execute(query, (machine_id,))
        result = cursor.fetchall()
        for row in result:
            filtered_result.append(row[0])
        print(filtered_result)
        filtered_result = list(map(int, filtered_result))
    except Exception as e:
        return render_template('process_failed.html', response='Error while loading product price', error="Please check internet connection")
    product_1_qty = int(request.args.get('product_1_q', 0))
    product_1_amount = filtered_result[0] * product_1_qty
    product_2_qty = int(request.args.get('product_2_q', 0))
    product_2_amount = filtered_result[1] * product_2_qty
    product_3_qty = int(request.args.get('product_3_q', 0))
    product_3_amount = filtered_result[2] * product_3_qty
    product_4_qty = int(request.args.get('product_4_q', 0))
    product_4_amount = filtered_result[3] * product_4_qty
    product_5_qty = int(request.args.get('product_5_q', 0))
    product_5_amount = filtered_result[4] * product_5_qty
    for i in range(0, 5):
        lgo_message = 'Product {} amount ='.format(i + 1) + str(filtered_result[i])
        app.logger.info(lgo_message)
    lgo_message = 'Product 1 quantity = {}'.format(product_1_qty)
    lgo_message2 = 'Product 2 quantity = {}'.format(product_2_qty)
    lgo_message3 = 'Product 3 quantity = {}'.format(product_3_qty)
    lgo_message4 = 'Product 4 quantity = {}'.format(product_4_qty)
    lgo_message5 = 'Product 5 quantity = {}'.format(product_5_qty)
    log_list = [lgo_message, lgo_message2, lgo_message3, lgo_message4, lgo_message5]
    for i in range(0, 5):
        app.logger.info(log_list[i])
    if product_1_qty == 0 and product_2_qty == 0 and product_3_qty == 0 and product_4_qty == 0 and product_5_qty == 0:
        return redirect('/')
    else:
        result = True
    if result:
        try:
            amount = product_1_amount + product_2_amount + product_3_amount + product_4_amount + product_5_amount
            global order_id
            global transaction_id
            order_id = generate_order_id()
            paytmParams["body"] = {
                "mid": mid,
                "orderId": order_id,
                "amount": amount,
                "businessType": businessType,
                "posId": posId,
            }
            checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), key)
            verify = PaytmChecksum.verifySignature(json.dumps(paytmParams["body"]), key, checksum)
            print("Verify: ", verify)
            paytmParams["head"] = {
                "clientId": clientId,
                "version": "v1",
                "signature": checksum
            }
            post_data = json.dumps(paytmParams)
            log_message = 'Request to paytm = {}'.format(post_data)
            app.logger.info(log_message)
            response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
            log_message = 'Response from paytm = {}'.format(response)
            app.logger.info(log_message)
            if response['body']['qrData']:
                log_message = 'QR code generated successfully'
                app.logger.info(log_message)
                paytmData = response['body']['qrData']
                qr_code = pyqrcode.create(paytmData)
                b64 = qr_code.png_as_base64_str(scale=4)
                order_id = paytmParams["body"]["orderId"]
                return render_template('paytm.html', qr_data=b64, order_id=order_id, total_amount=amount)
            else:
                response = make_response(render_template('process_failed.html', response='Network error',
                                                         error='Failed to establish internet connection please check internet'))
                response.status_code = 500

                return response
        except Exception as e:
            # Handle the KeyError exception when the required key is missing
            response = make_response(render_template('process_failed.html', response='Network error',
                                                     error='Failed to establish internet connection please check internet'))
            response.status_code = 500

            return response
    else:
        response = make_response(render_template('process_failed.html', response='Network error',
                                                 error='Failed to establish internet connection please check internet'))
        response.status_code = 500

        return response