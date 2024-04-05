from flask import render_template, request, redirect, make_response, jsonify, Blueprint
from app import app, machine_id, create_connection
from app.methods import update_inventory, get_inventory
import time


admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET'])
def login_form():
    return render_template('lock.html')


@admin.route('/admin_view', methods=['GET'])
def admin_activity():
    return redirect('/admin_list')


@app.route('/admin_list', methods=['GET'])
def admin_list():
    total_attempt = time.time() + 30
    retry_interval = 5
    while time.time() < total_attempt:
        try:
            conn = create_connection()
            cursor = conn.cursor()
            tray_partition_info = [
                (5, 8),  # Tray 5, 8 slots
                (4, 5),  # Tray 4, 7 slots
                (3, 3),  # Tray 3, 4 slots
                (2, 3),  # Tray 2, 4 slots
                (1, 3)  # Tray 1, 4 slots
            ]

            qty_in_machine = []
            qty_to_fill = []
            for tray_id, partition_count in tray_partition_info:
                for partition_no in range(1, partition_count + 1):
                    query = f"SELECT sum(status) FROM partition_table WHERE partition_no=%s AND tray_id=%s AND status=1 AND machine_id=%s;"
                    cursor.execute(query, (partition_no, tray_id, machine_id))
                    result = cursor.fetchone()[0] or 0
                    qty_in_machine.append(result)
            qty_in_machine =[int(qty) for qty in qty_in_machine]
            log_message = 'qty_in_machine by partition = {}'.format(qty_in_machine)
            app.logger.info(log_message)
            for i in range(0, 8):
                qty_to_fill.append(8 - qty_in_machine[i])
            for i in range(8, 13):
                qty_to_fill.append(7 - qty_in_machine[i])
            for i in range(13, 22):
                qty_to_fill.append(4 - qty_in_machine[i])
            qty_to_fill= [int(qty) for qty in qty_to_fill]
            log_massage = 'qty_to_fill by partition = {}'.format(qty_to_fill)
            app.logger.info(log_massage)
            return render_template('admin_activity.html', qty_in_machine=qty_in_machine, qty_to_fill=qty_to_fill)
        except Exception as e:
            time.sleep(retry_interval)

    response = make_response(render_template('process_failed.html', response='Network error',
                                             error='Failed to establish internet connection please check internet'))
    response.status_code = 500

    return response


@app.route('/insert_product', methods=['POST'])
def insert_product():
    try:
        temp_1 = [int(request.form.get(f'partition{i}') or 0) for i in range(1, 5)]
        temp_2 = [int(request.form.get(f'partition{i}') or 0) for i in range(5, 9)]
        temp_3 = [int(request.form.get(f'partition{i}') or 0) for i in range(9, 11)]
        temp_4 = [int(request.form.get(f'partition{i}') or 0) for i in range(11, 14)]
        temp_5 = [int(request.form.get(f'partition{i}') or 0) for i in range(14, 17)]
        temp_6 = [int(request.form.get(f'partition{i}') or 0) for i in range(17, 20)]
        temp_7 = [int(request.form.get(f'partition{i}') or 0) for i in range(20, 23)]
        update_inventory(temp_1, temp_2, temp_3, temp_4, temp_5, temp_6, temp_7, machine_id)
        log_message_ = 'Product inserted successfully'
        app.logger.info(log_message_)
        qty_to_fill, qty_in_machine = get_inventory(machine_id)
        return redirect('/admin_list')
    except Exception as e:
        response = make_response(render_template('process_failed.html', response='Network error',
                                                 error='Failed to establish internet connection please check internet'))
        response.status_code = 500

        return response


@app.route('/order_view', methods=['GET'])
def admin_inventory():
    try:
        connection = create_connection()
        if connection:
            start = int(request.args.get('start'))
            length = int(request.args.get('length'))
            draw = int(request.args.get('draw'))
            searchValue = request.args.get('search[value]')
            columns = request.args.getlist('columns')
            orderByIndex = int(request.args.get('order[0][column]'))
            orderBy = 'id'
            orderDir = request.args.get('order[0][dir]')
            cursor = connection.cursor()
            query = "SELECT DISTINCT oi.*, ol.transaction_date_time FROM order_items oi JOIN order_logs ol ON oi.txnId = ol.transaction_id WHERE oi.delivered_status = '1' AND oi.machine_id = %s"
            queryTotal = "SELECT COUNT(*) as total FROM order_items WHERE delivered_status='1' AND machine_id= %s"
            if searchValue:
                query += f" AND order_id LIKE '%{searchValue}%'"
                queryTotal += f" AND order_id LIKE '%{searchValue}%'"
            query += f" ORDER BY order_id DESC LIMIT {start}, {length}"
            cursor.execute(query, (machine_id,))
            result = cursor.fetchall()
            data = []
            count = start + 1
            product_names = {
                '1': "POMEGRANATE ARILS 100 GMS",
                '2': "POMEGRANATE ARILS 100 GMS",
                '3': "POMEGRANATE JUICE 200 ML",
                '4': "PINEAPPLE JUICE 200 ML",
                '5': "TRIMMED TENDER COCONUT"
            }
            for row in result:
                product_id = row[4]  # Assuming product_id is in the second column
                product_name = product_names.get(product_id)

                data.append({
                    'id': count,
                    'order_id': row[2],
                    'txnId': row[3],
                    'product_name': product_name,
                    'tray_no': row[5],
                    'partition_no': row[6],
                    'price_per_qty': row[7],
                    'transaction_date_time': row[9],
                })
                count += 1

            # Get the total count of records
            cursor.execute(queryTotal, (machine_id,))
            totalResult = cursor.fetchone()
            totalRecords = totalResult[0]

            response = {
                'draw': draw,
                'recordsTotal': totalRecords,
                'recordsFiltered': totalRecords,
                'data': data
            }
            # Close the database connection
            connection.close()
            # Send the JSON response
            return jsonify(response)

        else:
            return "Failed to connect to the database"
    except Exception as e:
        response = make_response(render_template('process_failed.html', response='Network error',
                                                 error='Failed to establish internet connection please check internet'))
        response.status_code = 500

        return response


@app.route('/fail_order', methods=['GET'])
def fail_inventory():
    try:
        connection = create_connection()
        if connection:
            start = int(request.args.get('start'))
            length = int(request.args.get('length'))
            draw = int(request.args.get('draw'))
            searchValue = request.args.get('search[value]')
            columns = request.args.getlist('columns')
            orderByIndex = int(request.args.get('order[0][column]'))
            orderBy = 'id'
            orderDir = request.args.get('order[0][dir]')
            cursor = connection.cursor()
            query = "SELECT DISTINCT oi.*, ol.transaction_date_time FROM order_items oi JOIN order_logs ol ON oi.txnId = ol.transaction_id WHERE oi.delivered_status = '0' AND oi.machine_id = %s"
            queryTotal = "SELECT COUNT(*) as total FROM order_items WHERE delivered_status='0' AND machine_id= %s"
            if searchValue:
                query += f" AND order_id LIKE '%{searchValue}%'"
                queryTotal += f" AND order_id LIKE '%{searchValue}%'"
            query += f" ORDER BY order_id DESC LIMIT {start}, {length}"

            cursor.execute(query, (machine_id,))
            result1 = cursor.fetchall()
            data1 = []
            count = start + 1
            product_names = {
                '1': "POMEGRANATE ARILS 100 GMS",
                '2': "POMEGRANATE ARILS 100 GMS",
                '3': "POMEGRANATE JUICE 200 ML",
                '4': "PINEAPPLE JUICE 200 ML",
                '5': "TRIMMED TENDER COCONUT"
            }

            for row1 in result1:
                product_id = row1[4]  # Assuming product_id is in the second column
                product_name = product_names.get(product_id)
                data1.append({
                    'id': count,
                    'order_id': row1[2],
                    'txnId': row1[3],
                    'product_name': product_name,
                    'tray_no': row1[5],
                    'partition_no': row1[6],
                    'price_per_qty': row1[7],
                    'transaction_date_time': row1[9],
                })

                count += 1

            # Get the total count of records
            cursor.execute(queryTotal, (machine_id,))
            totalResult = cursor.fetchone()
            totalRecords = totalResult[0]

            response = {
                'draw': draw,
                'recordsTotal': totalRecords,
                'recordsFiltered': totalRecords,
                'data': data1
            }
            # Close the database connection
            connection.close()
            # Send the JSON response
            return jsonify(response)

        else:
            return "Failed to connect to the database"
    except Exception as e:
        response = make_response(render_template('process_failed.html', response='Network error',
                                                 error='Failed to establish internet connection please check internet'))
        response.status_code = 500

        return response
