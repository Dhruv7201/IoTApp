from flask import Blueprint
from flask import render_template, make_response
import time
from app import create_connection
from app import app, get_machine_id


home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def index():
    total_attempt = time.time() + 30
    retry_interval = 5
    machine_id = get_machine_id()
    while time.time() < total_attempt:
        try:
            filtered_result = []
            price_result = []
            connection = create_connection()
            cursor = connection.cursor()
            print('000000000000000000000000',machine_id)
            query = "SELECT quantity FROM product WHERE machine_id=%s;"
            cursor.execute(query, (machine_id,))
            result = cursor.fetchall()
            filtered_result = []
            print('111111111111111111111111',result)
            for row in result:
                filtered_result.append(row[0])
            log_message = 'Total quantity of each product = {}'.format(filtered_result)
            app.logger.info(log_message)
            price_query = "SELECT price_per_quantity FROM product WHERE machine_id=%s;"
            cursor.execute(price_query, (machine_id,))
            price_result = cursor.fetchall()
            price = []
            print('2222222222222222222222222',price_result)
            for row in price_result:
                price.append(row[0])
            heading_query = "SELECT heading FROM machine_details WHERE machine_id=%s;"
            cursor.execute(heading_query, (machine_id,))
            heading = cursor.fetchone()[0]
            return render_template('main_page.html', result=filtered_result, price_list=price, heading=heading)
        except Exception as e:
            time.sleep(retry_interval)
    response = make_response(render_template('process_failed.html', response='Network error',
                                             error='Failed to establish internet connection please check internet1111'))
    response.status_code = 500

    return response