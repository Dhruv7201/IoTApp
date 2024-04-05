import json
import time
import mysql.connector
import os
import argparse


mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_database = os.getenv('MYSQL_DATABASE')
mysql_host = os.getenv('MYSQL_HOST')
ssl_ca = os.getenv('MYSQL_SSL_CA')
ssl_cert = os.getenv('MYSQL_SSL_CERT')
ssl_key = os.getenv('MYSQL_SSL_KEY')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Flask App')
    parser.add_argument('--dev', action='store_true', help='Enable debug mode')
    parser.add_argument('posId', help='Position ID')
    args = parser.parse_args()
    posId = args.posId
    dev = args.dev
    return posId, dev



def get_machine_id():
    posId, dev = parse_arguments()
    if posId == 'EVK01_001':
        machine_id = 1
    elif posId == 'EVK01_002':
        machine_id = 2
    elif posId == 'EVK01_003':
        machine_id = 3
    else:
        machine_id = None
    return machine_id

def generate_order_id():
    prefix = "ORDERID"
    timestamp = str(int(time.time()))
    order_id = prefix + timestamp
    return order_id


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            ssl_ca=ssl_ca,
            ssl_cert=ssl_cert,
            ssl_key=ssl_key
        )
        return connection
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred while connecting to the Mysql database")
        return None


def vend_process(item_id, quantity, machine_id):
    quantity = str(quantity)
    if item_id is None:
        return []
    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            query = """
            SELECT subquery.partition_no, subquery.tray_no,
            SUM(subquery.quantity) AS quantity FROM (SELECT partition_table.id, tray.tray_no,
            partition_table.partition_no,
            partition_table.product_id, 1 AS quantity FROM partition_table INNER JOIN tray ON tray.id = 
            partition_table.tray_id WHERE partition_table.product_id = %s AND partition_table.status = 1 AND machine_id= %s LIMIT %s) AS subquery 
            GROUP BY subquery.tray_no, subquery.partition_no;
            """
            cursor.execute(query, (item_id, machine_id, int(quantity)))
            vend_start = cursor.fetchall()
            json_list = []
            for row in vend_start:
                result_dict = {
                    'partition_no': int(row[0]),
                    'tray_no': int(row[1]),
                    'quantity': int(row[2])
                }
                json_list.append(json.dumps(result_dict))
            return json_list
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred while executing the SQL statement")
        return None


def save_paytm_response(response, machine_id):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        if response['body']['resultInfo']['resultStatus'] == 'TXN_SUCCESS':
            print("Order placed successfully")
            query = "INSERT INTO order_logs (order_id, transaction_id, transaction_amount, status, " \
                    "transaction_response_msg, transaction_response_code, transaction_date_time, machine_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(query,
                           (response['body']['orderId'], response['body']['txnId'], response['body']['txnAmount'],
                            response['body']['resultInfo']['resultStatus'],
                            response['body']['resultInfo']['resultMsg'],
                            response['body']['resultInfo']['resultCode'], response['body']['txnDate'], machine_id))
        elif response['body']['resultInfo']['resultStatus'] == 'PENDING':
            pending_check_query = "SELECT * FROM order_logs WHERE order_id = %s AND status = 'PENDING' AND machine_id = %s;"
            cursor.execute(pending_check_query, (response['body']['orderId'], machine_id))
            result = cursor.fetchall()
            if result:
                print("Order already exists")
                return False
            else:
                print("Order does not exist")
                query = "INSERT INTO order_logs (order_id, transaction_id, transaction_amount, status, " \
                        "transaction_response_msg, transaction_response_code, transaction_date_time, machine_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(query,
                               (response['body']['orderId'], response['body']['txnId'], response['body']['txnAmount'],
                                response['body']['resultInfo']['resultStatus'],
                                response['body']['resultInfo']['resultMsg'],
                                response['body']['resultInfo']['resultCode'], response['body']['txnDate'], machine_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    else:
        return False


def is_exist(item, quantity, machine_id):
    global cursor
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            select_query = "SELECT * FROM product WHERE name = %s AND quantity >= %s AND machine_id=%s;"
            print(f"item : {item}, quantity : {quantity}")
            cursor.execute(select_query, (item, quantity, machine_id))
            result = cursor.fetchone()
            if result:
                return True
            else:
                print("We don't have enough stock")
                return False
        except mysql.connector.Error as e:
            print(f"The error '{e}' occurred while executing the SQL query")
            return False
        finally:
            cursor.close()
            connection.close()


def get_inventory(machine_id):
    global qty_to_fill, qty_in_machine
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        tray_partition_info = [
            (5, 8),  # Tray 5, 8 partitions
            (4, 5),  # Tray 4, 7 partitions
            (3, 3),  # Tray 3, 4 partitions
            (2, 3),  # Tray 2, 4 partitions
            (1, 3)  # Tray 1, 4 partitions
        ]

        qty_in_machine = []
        qty_to_fill = []
        for tray_id, partition_count in tray_partition_info:
            for partition_no in range(1, partition_count + 1):
                query = f"SELECT sum(status) FROM partition_table WHERE partition_no={partition_no} AND tray_id={tray_id} AND status=1 AND machine_id={machine_id};"
                cursor.execute(query)
                result = cursor.fetchone()[0] or 0
                qty_in_machine.append(result)
        print('qty_in_machine:', qty_in_machine)
        for i in range(0, 8):
            qty_to_fill.append(8 - qty_in_machine[i])
        for i in range(8, 13):
            qty_to_fill.append(7 - qty_in_machine[i])
        for i in range(13, 22):
            qty_to_fill.append(4 - qty_in_machine[i])
        print('qty_to_fill:', qty_to_fill)
    return qty_to_fill, qty_in_machine


def update_inventory(temp_1, temp_2, temp_3, temp_4, temp_5, temp_6, temp_7, machine_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        if temp_1:
            for i in range(len(temp_1)):
                a = i + 1
                cursor.execute("UPDATE partition_table SET status=1 WHERE product_id=1 AND tray_id=5 AND partition_no=%s "
                               "AND status=0 AND machine_id=%s LIMIT %s", (a, machine_id, temp_1[i]))
                connection.commit()
            sum = temp_1[0] + temp_1[1] + temp_1[2] + temp_1[3]
            cursor.execute("UPDATE product SET quantity=quantity+%s WHERE name=%s AND machine_id=%s", (sum, "1", machine_id))
            connection.commit()
        if temp_2:
            for i in range(len(temp_2)):
                a = i + 5
                cursor.execute("UPDATE partition_table SET status=1 WHERE product_id=2 AND tray_id=5 AND partition_no=%s "
                               "AND status=0 AND machine_id=%s LIMIT %s", (a, machine_id, temp_2[i]))
                connection.commit()
            sum = temp_2[0] + temp_2[1] + temp_2[2] + temp_2[3]
            cursor.execute("UPDATE product SET quantity=quantity+%s WHERE name=%s AND machine_id=%s", (sum, "2", machine_id))
            connection.commit()
        if temp_3:
            for i in range(len(temp_3)):
                a = i + 1
                cursor.execute("UPDATE partition_table SET status=1 WHERE product_id=3 AND tray_id=4 AND partition_no=%s "
                               "AND status=0 AND machine_id=%s LIMIT %s", (a, machine_id, temp_3[i]))
                connection.commit()
            sum = temp_3[0] + temp_3[1]
            cursor.execute("UPDATE product SET quantity=quantity+%s WHERE name=%s AND machine_id=%s", (sum, "3", machine_id))
            connection.commit()
        if temp_4:
            for i in range(len(temp_4)):
                a = i + 3
                cursor.execute("UPDATE partition_table SET status=1 WHERE product_id=4 AND tray_id=4 AND partition_no=%s "
                               "AND status=0 AND machine_id=%s LIMIT %s", (a, machine_id, temp_4[i]))
                connection.commit()
            sum = temp_4[0] + temp_4[1] + temp_4[2]
            cursor.execute("UPDATE product SET quantity=quantity+%s WHERE name=%s AND machine_id=%s", (sum, "4", machine_id))
            connection.commit()
        if temp_5:
            for i in range(len(temp_5)):
                a = i + 1
                cursor.execute("UPDATE partition_table SET status=1 WHERE product_id=5 AND tray_id=3 AND partition_no=%s "
                               "AND status=0 AND machine_id=%s LIMIT %s", (a, machine_id, temp_5[i]))
                connection.commit()
            sum = temp_5[0] + temp_5[1] + temp_5[2]
            cursor.execute("UPDATE product SET quantity=quantity+%s WHERE name=%s AND machine_id=%s", (sum, "5", machine_id))
            connection.commit()
        if temp_6:
            for i in range(len(temp_6)):
                a = i + 1
                cursor.execute("UPDATE partition_table SET status=1 WHERE product_id=5 AND tray_id=2 AND partition_no=%s "
                               "AND status=0 AND machine_id=%s LIMIT %s", (a, machine_id, temp_6[i]))
                connection.commit()
            sum = temp_6[0] + temp_6[1] + temp_6[2]
            cursor.execute("UPDATE product SET quantity=quantity+%s WHERE name=%s AND machine_id=%s", (sum, "5", machine_id))
            connection.commit()
        if temp_7:
            for i in range(len(temp_7)):
                a = i + 1
                cursor.execute("UPDATE partition_table SET status=1 WHERE product_id=5 AND tray_id=1 AND partition_no=%s "
                               "AND status=0 AND machine_id=%s LIMIT %s", (a, machine_id, temp_7[i]))
                connection.commit()
            sum = temp_7[0] + temp_7[1] + temp_7[2]
            cursor.execute("UPDATE product SET quantity=quantity+%s WHERE name=%s AND machine_id=%s", (sum, "5", machine_id))
            connection.commit()
    return True




def insert_order(cursor, order_id, transaction_id, item_id, tray_no, partition_no, product_price, machine_id):
    insert_order_items = "INSERT INTO order_items " \
                         "(order_id,txnId,product_id,tray_no,partition_no,price_per_qty,delivered_status,machine_id) " \
                         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s );"
    cursor.execute(insert_order_items, (order_id, transaction_id, item_id, tray_no, partition_no,
                                        product_price, 0, machine_id))


def update_order(last_row_id, machine_id, cursor):
    update_order_item = "UPDATE order_items SET delivered_status = 1 WHERE id=%s AND machine_id=%s;"
    cursor.execute(update_order_item, (last_row_id, machine_id))


def update_partition(item_id, partition_no, tray_no, machine_id, cursor):
    update_query = "UPDATE partition_table SET status = 0 WHERE product_id=%s AND partition_no=%s AND tray_id=%s AND status=1 AND machine_id=%s LIMIT %s;"
    cursor.execute(update_query, (item_id, partition_no, tray_no, machine_id, 1))


def update_product(item_id, machine_id, connection):
    connection.close()
    connection = create_connection()
    cursor = connection.cursor()
    update_product = "UPDATE product SET quantity = quantity-%s where name = %s AND machine_id=%s;"
    cursor.execute(update_product, (1, item_id, machine_id))
    connection.commit()
    cursor.close()