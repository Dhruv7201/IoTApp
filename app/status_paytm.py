import requests
import json
import PaytmChecksum
import sqlite3

DB_FILE = 'db/iot_db'


def connection():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    return cursor, conn


paytmParams = dict()

# body parameters
paytmParams["body"] = {
    "mid": "KRYOTE87616666858008",
    "orderId": "ORDERID1688019682510",
}
checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), "@43jPcfA_lR3FpJD")
paytmParams["head"] = {
    "signature": checksum
}

post_data = json.dumps(paytmParams)

url = "https://securegw-stage.paytm.in/v3/order/status"

response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
print(response)
cursor, conn = connection()
tid = response['body']['txnId']
tid_db = conn.execute("SELECT txnId FROM paytm WHERE txnId = ?", (tid,)).fetchone()
tid_db = tid_db[0]
if tid == tid_db:
    print("Record already exists")
else:

    cursor.execute("""
        INSERT INTO paytm (
            signature,
            resultStatus,
            txnId,
            bankTxnId,
            orderId,
            txnAmount,
            txnType,
            gatewayName,
            bankName,
            mid,
            paymentMode,
            refundAmt,
            txnDate,
            merchantUniqueReference,
            posId,
            udf1
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        response['head']['signature'],
        response['body']['resultInfo']['resultStatus'],
        response['body']['txnId'],
        response['body']['bankTxnId'],
        response['body']['orderId'],
        response['body']['txnAmount'],
        response['body']['txnType'],
        response['body']['gatewayName'],
        response['body']['bankName'],
        response['body']['mid'],
        response['body']['paymentMode'],
        response['body']['refundAmt'],
        response['body']['txnDate'],
        response['body']['merchantUniqueReference'],
        response['body']['posId'],
        response['body']['udf1']
    ))
    # commit
    conn.commit()
    print("Record created successfully")
