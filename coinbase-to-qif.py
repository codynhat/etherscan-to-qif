import qifparse.qif as qif
import datetime
import csv
import os
import re

ADDRESS=os.environ['ADDRESS']

with open('coinbase.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='Coinbase', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        memo = row[9]
        timestamp = datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ")

        if row[1] == "Buy":
            buyAmount = float(row[3])
            buyCurrency = row[2]
            spotPrice = float(row[5])

            tr1 = qif.Investment(date=timestamp, action="Buy", quantity=buyAmount, price=spotPrice, memo=memo, security=(buyCurrency+'-USD'))

            tr1._fields[4].custom_print_format='%s%.18f'

            acc.add_transaction(tr1, header='!Type:Invst')
        elif row[1] == "Paid for an order":
            amount = float(row[3])
            currency = row[2]
            spotPrice = float(row[5])

            tr1 = qif.Investment(date=timestamp, action="SellX", quantity=amount, price=spotPrice, memo=memo, security=(currency+'-USD'))

            tr1._fields[4].custom_print_format='%s%.18f'

            acc.add_transaction(tr1, header='!Type:Invst')
        elif row[1] == "Convert":
            sellAmount = float(row[3])
            sellCurrency = row[2]
            spotPrice = float(row[5])

            match = re.findall(r".+ (.+) (.+)$", memo)
            buyAmount = float(match[0][0])
            buyCurrency = match[0][1]
            buyPrice = (spotPrice * sellAmount) / buyAmount

            tr1 = qif.Investment(date=timestamp, action="Sell", quantity=sellAmount, price=spotPrice, memo=memo, security=(sellCurrency+'-USD'))
            tr2 = qif.Investment(date=timestamp, action="Buy", quantity=buyAmount, price=buyPrice, memo=memo, security=(buyCurrency+'-USD'))

            tr1._fields[4].custom_print_format='%s%.10f'
            tr2._fields[4].custom_print_format='%s%.10f'

            acc.add_transaction(tr1, header='!Type:Invst')
            acc.add_transaction(tr2, header='!Type:Invst')


    print(str(qif_obj))
