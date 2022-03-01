import qifparse.qif as qif
import datetime
import csv
import os
import re

ADDRESS=os.environ['ADDRESS']
prices={}
spotPrices={}
START_DATE=datetime.date(2020, 5, 10)

with open('coinbase-pro.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    for row in reader:
        currency = row[5]
        if row[1] == "match":
            if currency == "USD":
                prices[row[7]] = float(row[3])
                spotPrices[row[7]] = {}
            elif currency == "USDC":
                prices[row[7]] = float(row[3])
                spotPrices[row[7]] = {}
            elif currency == "DAI" and not (row[7] in prices):
                prices[row[7]] = float(row[3])
                spotPrices[row[7]] = {}

with open('coinbase-pro.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    next(reader, None)

    qif_obj = qif.Qif()

    acc = qif.Account(name='Coinbase Pro', account_type='Invst')
    qif_obj.add_account(acc)

    for row in reader:
        memo = row[6] + ';' + row[7] + ';' + row[8]
        timestamp = datetime.datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S.%fZ")

        if timestamp.date() <= START_DATE:
            continue

        if row[1] == "match":
            amount = float(row[3])
            currency = row[5]
            
            if not (row[7] in prices):
                print("NOT FOUND")
                exit()
            
            spotPrice = abs(prices[row[7]] / amount)
            spotPrices[row[7]][currency] = spotPrice

            if currency == "USD":
                continue

            if amount > 0:
                tr1 = qif.Investment(date=timestamp, action="Buy", price=spotPrice, quantity=amount, memo=memo, security=(currency+'-USD'))
                tr1._fields[3].custom_print_format='%s%.10f'
                tr1._fields[4].custom_print_format='%s%.18f'
                acc.add_transaction(tr1, header='!Type:Invst')
            else:
                tr1 = qif.Investment(date=timestamp, action="Sell", price=spotPrice, quantity=-amount, memo=memo, security=(currency+'-USD'))
                tr1._fields[3].custom_print_format='%s%.10f'
                tr1._fields[4].custom_print_format='%s%.18f'
                acc.add_transaction(tr1, header='!Type:Invst')
        elif row[1] == "fee":
            amount = float(row[3])
            currency = row[5]

            if not (row[7] in spotPrices):
                print("NOT FOUND")
                exit()
            
            spotPrice = spotPrices[row[7]][currency]

            if currency == "USD":
                tr1 = qif.Transaction(date=timestamp, amount=amount, memo=memo)
                tr1._fields[3].custom_print_format='%s%.10f'
                tr1._fields[4].custom_print_format='%s%.18f'
                acc.add_transaction(tr1, header='!Type:Invst')
            else:
                tr1 = qif.Investment(date=timestamp, action="SellX", price=spotPrice, quantity=-amount, memo=memo, security=(currency+'-USD'))
                tr1._fields[3].custom_print_format='%s%.10f'
                tr1._fields[4].custom_print_format='%s%.18f'
                acc.add_transaction(tr1, header='!Type:Invst')
        else:
            continue


    print(str(qif_obj))
