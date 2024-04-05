from flask import request, jsonify, render_template, make_response, Blueprint
from app import vend_process
import requests
import json
from app import PaytmChecksum
from app.methods import save_paytm_response


payment = Blueprint('payment', __name__)
from app import app, product_1_qty, product_2_qty, product_3_qty, product_4_qty, product_5_qty, order_id, machine_id, mid, key, status_url


@payment.route('/status', methods=['GET'])
def status():
    global machine_id
    global transaction_id
    paytmParams = dict()
    try:
        order_id = request.args.get('order_id')
        # body parameters
        paytmParams["body"] = {
            "mid": mid,
            "orderId": order_id,
        }
        checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), key)
        verify = PaytmChecksum.verifySignature(json.dumps(paytmParams["body"]), key, checksum)
        log_message = 'Request to paytm = {}'.format(paytmParams)
        app.logger.info(log_message)
        paytmParams["head"] = {
            "signature": checksum
        }

        post_data = json.dumps(paytmParams)
        response = requests.post(status_url, data=post_data, headers={"Content-type": "application/json"}).json()
        log_message = 'Response from paytm = {}'.format(response)
        app.logger.info(log_message)
        t_status = response['body']['resultInfo']['resultStatus']
        if t_status == "TXN_SUCCESS":
            log_message = 'Payment Success Proceeding to vend'
            app.logger.info(log_message)
            transaction_id = response['body']['txnId']
            result = save_paytm_response(response, machine_id)
            if result:
                data = {"status": "success"}
                return jsonify(data)
            else:
                response = make_response(render_template('process_failed.html', response='Network error',
                                                         error='Failed to establish internet connection please check internet'))
                response.status_code = 500

                return response
        elif t_status == "PENDING":
            log_message = 'Payment status pending'
            app.logger.info(log_message)
            save_paytm_response(response, machine_id)
            data = {"status": "pending"}
            return jsonify(data)
        else:
            save_paytm_response(response, machine_id)
            log_message = 'Payment Failed'
            app.logger.info(log_message)
            data = {"status": "fail"}
            return jsonify(data)
    except Exception as e:
        data = {"status": "network_error"}
        return data


@payment.route('/PaymentSuccess', methods=['GET'])
def payment_success():
    global machine_id
    main_json = {}
    try:
        if product_5_qty > 0:
            product_5 = vend_process("5", product_5_qty, machine_id)
            main_json["product_5"] = product_5
        if product_4_qty > 0:
            product_4 = vend_process("4", product_4_qty, machine_id)
            main_json["product_4"] = product_4
        if product_3_qty > 0:
            product_3 = vend_process("3", product_3_qty, machine_id)
            main_json["product_3"] = product_3
        if product_2_qty > 0:
            product_2 = vend_process("2", product_2_qty, machine_id)
            main_json["product_2"] = product_2
        if product_1_qty > 0:
            product_1 = vend_process("1", product_1_qty, machine_id)
            main_json["product_1"] = product_1
        main_json = json.dumps(main_json)
        log_message = 'Json for Vending process = {}'.format(main_json)
        app.logger.info(log_message)
        return render_template('success.html', main_json=main_json, order_id=order_id)
    except Exception as e:
        response = make_response(render_template('process_failed.html', response='Network error',
                                                 error='Failed to establish internet connection please check internet'))
        response.status_code = 500

        return response


@payment.route('/PaymentFailure', methods=['GET'])
def payment_failure():
    return render_template('payment_fail.html')