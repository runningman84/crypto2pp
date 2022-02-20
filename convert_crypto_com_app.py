#!/usr/bin/env python

import csv
import re
import locale
import argparse
import datetime
import yaml
# required arg
parser = argparse.ArgumentParser()
parser.add_argument('in_filename')
parser.add_argument('out_filename')
parser.add_argument('config_filename')

args = parser.parse_args()

in_filename = args.in_filename
out_filename = args.out_filename
config_filename = args.config_filename

with open(config_filename, "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

KONTO_FIAT = config.get('konten', {}).get('crypto_com_app_fiat', 'Crypto.com FIAT')
KONTO_EXTERNAL_VISA = config.get('konten', {}).get('crypto_com_external_visa', 'External VISA')
DEPOT_DEFII = config.get('depots', {}).get('crypto_com_defi_crypto', 'Crypto.com DeFi Wallet')
DEPOT_APP = config.get('depots', {}).get('crypto_com_app_crypto', 'Crypto.com App Wallet')
LOCALE_HISTORY = config.get('locales', {}).get('history', 'en_US.UTF-8')
LOCALE_PP = config.get('locales', {}).get('pp', 'de_DE.UTF-8')
LOCALE_CRYPTO_COM = config.get('locales', {}).get('crypto_com', 'en_US.UTF-8')

print ("Crypto.com App Transaction Parser")
print ("Reading: {}".format(in_filename))

parsed_res = []

with open(in_filename) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        locale.setlocale(locale.LC_ALL, LOCALE_CRYPTO_COM)

        for keyname in row.keys():
            if (row[keyname] == ''):
                row[keyname] = None
            elif keyname in ['Amount', 'To Amount', 'Native Amount', 'Native Amount (in USD)']:
                row[keyname] = locale.atof(row[keyname])

        transaction_date = row['Timestamp (UTC)']
        transaction_symbol = None
        transaction_type  = None
        transaction_value = row['Native Amount']
        transaction_extra = None
        transaction_depot = DEPOT_APP
        transaction_konto = KONTO_FIAT
        transaction_amount = row['Amount']
        transaction_date_obj = datetime.datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S')

        if(row['Currency'] == 'CRO'):
            transaction_symbol = 'CRO-EUR'

        if(row['Currency'] == 'EUR'):
            transaction_symbol = row['To Currency'] + '-EUR'

        if(row['To Amount'] is not None):
            transaction_amount = row['To Amount']

        cat_rein = [
            "referral_gift",
            "referral_bonus",
            "rewards_platform_deposit_credited",
            "referral_card_cashback",
            "reimbursement",
            "viban_deposit"
        ]

        cat_raus = [
            "card_cashback_reverted",
            "crypto_withdrawal",
            "viban_card_top_up"
        ]

        cat_kauf = [
            "viban_purchase",
            "crypto_purchase"
        ]

        # mode konto umsätze
        m = re.search("fiat_transactions",in_filename)
        if m is not None:
            if row['Transaction Kind'] in cat_rein:
                transaction_type = "Einlage"

            if row['Transaction Kind'] in cat_raus:
                transaction_type = "Entnahme"

        # mode depot umsätze
        m = re.search("crypto_transactions",in_filename)
        if m is not None:
            if row['Transaction Kind'] in cat_rein:
                transaction_type = "Einlieferung"

            if row['Transaction Kind'] in cat_raus:
                transaction_type = "Auslieferung"

        if row['Transaction Kind'] in cat_kauf:
            transaction_type = "Kauf"

        if row['Transaction Kind'] == 'crypto_purchase':
            transaction_konto = KONTO_EXTERNAL_VISA

        if transaction_value == 0 and transaction_type is None:
                continue

        if row['Transaction Kind'] == 'lockup_lock':
            continue

        locale.setlocale(locale.LC_ALL, LOCALE_PP)

        dict = {
            'Datum': transaction_date_obj.strftime('%Y-%m-%d'),
            'Uhrzeit': transaction_date_obj.strftime('%H:%M:%S'),
            'Typ': transaction_type,
            'Wert': locale.str(transaction_value),
            'Zusatz': transaction_extra,
            'Notiz': row['Transaction Description'],
            'Depot': transaction_depot,
            'Konto': transaction_konto,
            'Stück': locale.str(transaction_amount),
            'Ticker-Symbol': transaction_symbol
        }

        parsed_res.append(dict)
        print(dict)
        line_count = line_count + 1

    print(f'Processed {line_count} lines.')

print ("Writing export: {}".format(out_filename))

with open(out_filename, mode='w') as out_file:
    fieldnames = parsed_res[0].keys()
    writer = csv.DictWriter(out_file, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()

    for dataset in parsed_res:
        writer.writerow(dataset)

print("")