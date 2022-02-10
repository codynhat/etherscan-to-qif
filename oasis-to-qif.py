import qifparse.qif as qif
import datetime
import csv
import os
import requests
import json

ADDRESS=os.environ['ADDRESS']
INFURA_ID=os.environ['INFURA_ID']

with open('oasis.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='Oasis', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        buyAmount = float(row[1])
        buyCurrency = row[2]
        sellAmount = float(row[3])
        sellCurrency = row[4]

        timestamp = datetime.datetime.strptime(row[10], "%Y-%m-%d %H:%M")

        txhash = row[9]

        block_number = requests.post('https://mainnet.infura.io/v3/' + INFURA_ID, data=json.dumps({
            "id": 1337,
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [txhash]
        })).json()['result']['blockNumber']
        memo = str(int(block_number, 16)) + ';' + txhash + ';Oasis'

        sellPrice = buyAmount / sellAmount
        if sellCurrency == "USDC":
            sellPrice = 1.00
        elif sellCurrency == "DAI" and buyCurrency != "USDC":
            sellPrice = 1.00

        buyPrice = sellAmount / buyAmount
        if buyCurrency == "USDC":
            buyPrice = 1.00
        elif buyCurrency == "DAI" and sellCurrency != "USDC":
            buyPrice = 1.00

        tr1 = qif.Investment(date=timestamp, action="Sell", quantity=sellAmount, price=sellPrice, memo=memo, security=(sellCurrency+'-USD'))
        tr2 = qif.Investment(date=timestamp, action="Buy", quantity=buyAmount, price=buyPrice, memo=memo, security=(buyCurrency+'-USD'))

        tr1._fields[4].custom_print_format='%s%.18f'
        tr2._fields[4].custom_print_format='%s%.18f'

        acc.add_transaction(tr1, header='!Type:Invst')
        acc.add_transaction(tr2, header='!Type:Invst')

    print(str(qif_obj))
