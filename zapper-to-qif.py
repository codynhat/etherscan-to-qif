import qifparse.qif as qif
import datetime
import csv
import os
import requests
import json
from functools import reduce

ADDRESS=os.environ['ADDRESS']
INFURA_ID=os.environ['INFURA_ID']
CHAIN="Polygon"

with open('zapper.csv', 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=";", quotechar='|')

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='Zapper', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        txns = json.loads(row[4][1:-1])
        txhash = row[0][1:-1]

        timestamp = datetime.datetime.fromtimestamp(int(row[1][1:-1]))
        memo = CHAIN + ";" + txhash + ';Zapper'

        for txn in txns:
            tr1 = qif.Investment(date=timestamp, action=("Buy" if txn["type"] == "incoming" else "Sell"), quantity=txn["amount"], price=0, memo=memo, security=(txn["symbol"]+'-USD'))
            tr1._fields[3].custom_print_format='%s%.10f'
            tr1._fields[4].custom_print_format='%s%.18f'
            acc.add_transaction(tr1, header='!Type:Invst')

    print(str(qif_obj))
