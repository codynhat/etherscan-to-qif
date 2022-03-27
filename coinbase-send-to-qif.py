import qifparse.qif as qif
import datetime
import csv
import os
import re

ADDRESS=os.environ['ADDRESS']
START_DATE=datetime.date(2020, 2, 27)
END_DATE=datetime.date(2022, 9, 19)

with open('coinbase.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='Coinbase', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        memo = row[9]
        timestamp = datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ")

        if timestamp.date() <= START_DATE or timestamp.date() > END_DATE:
            continue

        if row[1] != "Send":
            continue

        amount = float(row[3])
        currency = row[2]
        spotPrice = float(row[5])

        tr1 = qif.Investment(date=timestamp, action="SellX", quantity=0, price=spotPrice, memo=memo, security=(currency+'-USD'))

        tr1._fields[4].custom_print_format='%s%.18f'

        acc.add_transaction(tr1, header='!Type:Invst')


    print(str(qif_obj))
