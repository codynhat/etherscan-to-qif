import qifparse.qif as qif
import datetime
import csv
import os

ADDRESS=os.environ['ADDRESS']
CURRENCY="XDAI"
CHAIN="Gnosis"

with open('blockscout.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    qif_obj = qif.Qif()

    acc = qif.Account(name='ETH Wallet', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        if row[3] != ADDRESS:
            continue

        memo = CHAIN + ";" + row[1] + ';' + row[0]
        timestamp = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.000000Z")
        txnFeeETH = float(row[8]) / (1e18)
        price = float(row[11])

        tr1 = qif.Investment(date=timestamp, action="SellX", quantity=txnFeeETH, price=price, memo=memo, security=CURRENCY+"-USD")

        tr1._fields[4].custom_print_format='%s%.18f'
        tr1._fields[3].custom_print_format='%s%.10f'

        acc.add_transaction(tr1, header='!Type:Invst')

    print(str(qif_obj))
