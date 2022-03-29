import qifparse.qif as qif
import datetime
import csv
import os

CHAIN="zkSync"

with open('zksync.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='zkSync Wallet', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        memo = CHAIN + ";" + row[12]
        timestamp = datetime.datetime.strptime(row[11], "%d/%m/%Y %H:%M:%S")
        
        txn_type = row[0]

        if txn_type == "Spend":
            sellAmount = float(row[4])
            sellCurrency = row[5]

            feeAmount = float(row[7])
            feeCurrency = row[8]

            if sellAmount > 0:
                tr1 = qif.Investment(date=timestamp, action="SellX", quantity=sellAmount, price=1.0, memo=memo, security=(sellCurrency+'-USD'))

                tr1._fields[3].custom_print_format='%s%.10f'
                tr1._fields[4].custom_print_format='%s%.18f'

                acc.add_transaction(tr1, header='!Type:Invst')

            if feeAmount > 0:
                tr2 = qif.Investment(date=timestamp, action="SellX", quantity=feeAmount, price=1.0, memo=memo, security=(feeCurrency+'-USD'))

                tr2._fields[3].custom_print_format='%s%.10f'
                tr2._fields[4].custom_print_format='%s%.18f'

                acc.add_transaction(tr2, header='!Type:Invst')


        elif txn_type == "Income":
            buyAmount = float(row[1])
            buyCurrency = row[2]
            spotPrice = 1.0

            tr1 = qif.Transaction(date=timestamp, amount=(buyAmount*spotPrice), memo=memo)
            tr2 = qif.Investment(date=timestamp, action="Buy", quantity=buyAmount, price=spotPrice, memo=memo, security=(buyCurrency+'-USD'))

            tr1._fields[4].custom_print_format='%s%.18f'
            tr2._fields[4].custom_print_format='%s%.18f'

            acc.add_transaction(tr1, header='!Type:Invst')
            acc.add_transaction(tr2, header='!Type:Invst')

    print(str(qif_obj))
