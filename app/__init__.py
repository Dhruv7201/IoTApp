from flask import Flask
import logging
from app.methods import create_connection, generate_order_id, vend_process
import os
from app.views import register_blueprints
from app.methods import get_machine_id
import app.PaytmChecksum


app = Flask(__name__, static_folder='static', template_folder='templates')
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logger = logging.basicConfig(level=logging.INFO, format=log_format)


posId = None
dev = False
mid = os.getenv('MID')
key = os.getenv('MKEY')
businessType = os.getenv('BUSINESS_TYPE')
clientId = os.getenv('CLIENT_ID')
url = os.getenv('PAYMENT_URL')
status_url = os.getenv('STATUS_URL')
product_1_qty = 0
product_2_qty = 0
product_3_qty = 0
product_4_qty = 0
product_5_qty = 0
order_id = generate_order_id()
machine_id = get_machine_id()
register_blueprints(app)