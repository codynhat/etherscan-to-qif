import qifparse.qif as qif
import datetime
import csv
import os
import requests
import json
from functools import reduce

ADDRESS=os.environ['ADDRESS']
INFURA_ID=os.environ['INFURA_ID']

with open('zerion.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='Zerion', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        if row[5] != "Income":
            continue

        buyAmounts = row[6].split("\n")
        fiatAmounts = list(map(lambda a: (float(a) if len(a) > 0 else 0), row[9].split("\n") if len(row[9]) > 0 else row[14].split("\n")))
        totalFiatAmount = float(reduce(lambda a, b: a + b, fiatAmounts))
        buyCurrencies = row[7].split("\n")

        timestamp = datetime.datetime.strptime(row[24], "%Y-%m-%dT%H:%M:%S.000Z")

        txhash = row[22]

        block_number = requests.post('https://mainnet.infura.io/v3/' + INFURA_ID, data=json.dumps({
            "id": 1337,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [txhash]
        })).json()['result']['blockNumber']
        memo = str(int(block_number, 16)) + ';' + txhash + ';Zerion'

        for i in range(len(buyAmounts)):
            buyAmount = float(buyAmounts[i])
            fiatAmount = float(fiatAmounts[i]) if len(buyAmounts) > 1 else totalFiatAmount
            if fiatAmount == 0:
                fiatAmount = 1
            buyCurrency = buyCurrencies[i]
            if buyCurrency == "BPT-V1":
                buyCurrency = buyCurrency + "-" + row[8]

            tr1 = qif.Transaction(date=timestamp, amount=fiatAmount, memo=memo)
            tr2 = qif.Investment(date=timestamp, action="Buy", quantity=buyAmount, price=(fiatAmount/buyAmount), memo=memo, security=(buyCurrency+'-USD'))

            tr1._fields[3].custom_print_format='%s%.10f'
            tr1._fields[4].custom_print_format='%s%.18f'
            tr2._fields[3].custom_print_format='%s%.10f'
            tr2._fields[4].custom_print_format='%s%.18f'

            acc.add_transaction(tr1, header='!Type:Invst')
            acc.add_transaction(tr2, header='!Type:Invst')

    print(str(qif_obj))
