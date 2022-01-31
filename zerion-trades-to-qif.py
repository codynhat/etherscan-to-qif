import qifparse.qif as qif
import datetime
import csv
import os
import requests
import json

ADDRESS=os.environ['ADDRESS']
INFURA_ID=os.environ['INFURA_ID']

with open('zerion.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='Zerion', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        if row[2] != "Trade":
            continue

        buyAmount = float(row[6])
        fiatAmount = float(row[9]) if len(row[9]) > 0 else float(row[14])
        buyCurrency = row[7]
        sellAmount = float(row[11])
        sellCurrency = row[12]

        timestamp = datetime.datetime.strptime(row[24], "%Y-%m-%dT%H:%M:%S.000Z")

        txhash = row[22]

        block_number = requests.post('https://mainnet.infura.io/v3/' + INFURA_ID, data=json.dumps({
            "id": 1337,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [txhash]
        })).json()['result']['blockNumber']
        memo = str(int(block_number, 16)) + ';' + txhash + ';Zerion'

        tr1 = qif.Investment(date=timestamp, action="Sell", quantity=sellAmount, price=(fiatAmount/sellAmount), memo=memo, security=(sellCurrency+'-USD'))
        tr2 = qif.Investment(date=timestamp, action="Buy", quantity=buyAmount, price=(fiatAmount/buyAmount), memo=memo, security=(buyCurrency+'-USD'))

        tr1._fields[4].custom_print_format='%s%.18f'
        tr2._fields[4].custom_print_format='%s%.18f'

        acc.add_transaction(tr1, header='!Type:Invst')
        acc.add_transaction(tr2, header='!Type:Invst')

    print(str(qif_obj))
