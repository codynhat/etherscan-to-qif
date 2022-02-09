import qifparse.qif as qif
import datetime
import csv
import os

ADDRESS=os.environ['ADDRESS']

with open('tokentax.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='TokenTax', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        memo = row[8]
        timestamp = datetime.datetime.strptime(row[12], "%Y-%m-%dT%H:%M:%S.000Z")
        buyAmount = float(row[1])
        buyCurrency = row[2]
        sellAmount = float(row[3])
        sellCurrency = row[4]
        feeAmount = float(row[5])
        feeCurrency = row[6]
        fiatAmount = float(row[13].split("$")[1])

        if row[0] == "Mining":
            # Add income
            tr0 = qif.Transaction(date=timestamp, amount=fiatAmount, memo=memo)
            acc.add_transaction(tr0, header='!Type:Invst')


        tr1 = qif.Investment(date=timestamp, action="Sell", quantity=sellAmount, price=(fiatAmount/sellAmount), memo=memo, security=(sellCurrency+'-USD'))
        tr2 = qif.Investment(date=timestamp, action="Buy", quantity=buyAmount, price=(fiatAmount/buyAmount), memo=memo, security=(buyCurrency+'-USD'))
        tr3 = qif.Investment(date=timestamp, action="SellX", quantity=feeAmount, price=(fiatAmount/sellAmount), memo=memo, security=(feeCurrency+'-USD'))

        tr1._fields[4].custom_print_format='%s%.18f'
        tr2._fields[4].custom_print_format='%s%.18f'
        tr3._fields[4].custom_print_format='%s%.18f'

        if sellCurrency != "USD":
            acc.add_transaction(tr1, header='!Type:Invst')

        acc.add_transaction(tr2, header='!Type:Invst')

        if row[0] != "Mining":
            acc.add_transaction(tr3, header='!Type:Invst')


    print(str(qif_obj))
