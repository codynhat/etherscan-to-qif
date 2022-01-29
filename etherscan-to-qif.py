import qifparse.qif as qif
import datetime
import csv
import os

ADDRESS=os.environ['ADDRESS']

with open('transactions.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    qif_obj = qif.Qif()

    acc = qif.Account(name='ETH Wallet', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        if row[4] != ADDRESS:
            continue

        memo = row[1] + ';' + row[0]
        timestamp = datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
        txnFeeETH = float(row[10])
        price = float(row[12])

        tr1 = qif.Investment(date=timestamp, action="SellX", quantity=txnFeeETH, price=price, memo=memo, security="ETH-USD")

        tr1._fields[4].custom_print_format='%s%.18f'

        acc.add_transaction(tr1, header='!Type:Invst')

    print(str(qif_obj))
