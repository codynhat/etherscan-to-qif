import qifparse.qif as qif
import datetime
import csv
import os

ADDRESS=os.environ['ADDRESS']

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

        tr1 = qif.Investment(date=timestamp, action="SellX", quantity=sellAmount, price=(1.00 if sellCurrency == "USDC" else (sellAmount / buyAmount)), memo=txhash, security=sellCurrency)
        tr2 = qif.Investment(date=timestamp, action="BuyX", quantity=buyAmount, price=(1.00 if buyCurrency == "USDC" else (buyAmount / sellAmount)), memo=txhash, security=buyCurrency)

        tr1._fields[4].custom_print_format='%s%.18f'
        tr2._fields[4].custom_print_format='%s%.18f'

        acc.add_transaction(tr1, header='!Type:Invst')
        acc.add_transaction(tr2, header='!Type:Invst')

    print(str(qif_obj))
