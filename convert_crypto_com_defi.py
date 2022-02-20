#!/usr/bin/env python

import csv
import re
import locale
import argparse
import datetime
import dateparser
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
DEPOT_DEFII = config.get('depots', {}).get('crypto_com_defi_crypto', 'Crypto.com DeFi Wallet')
DEPOT_APP = config.get('depots', {}).get('crypto_com_app_crypto', 'Crypto.com App Wallet')
LOCALE_HISTORY = config.get('locales', {}).get('history', 'en_US.UTF-8')
LOCALE_PP = config.get('locales', {}).get('pp', 'de_DE.UTF-8')
LOCALE_CRYPTO_COM = config.get('locales', {}).get('crypto_com', 'en_US.UTF-8')

print ("Crypto.com Defi Transaction Parser")

parsed_res = []
history = {}
history_filename = 'history/CRO.csv'


print ("Reading history: {}".format(history_filename))
locale.setlocale(locale.LC_ALL, LOCALE_HISTORY)
with open(history_filename) as csv_file:

    csv_reader = csv.reader(csv_file, delimiter='\t')
    next(csv_reader) # skip header
    line_count = 0
    for row in csv_reader:

        history_date = row[0].strip()
        history_date_obj = datetime.datetime.strptime(history_date, '%b %d, %Y')
        history_value_converted = row[4].replace('€', '')
        history_symbol = 'CRO-EUR'

        if history_symbol not in history:
            history[history_symbol] = {}

        history[history_symbol][history_date_obj.date()] = history_value_converted

print ("Reading transactions: {}".format(in_filename))
with open(in_filename) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        locale.setlocale(locale.LC_ALL, LOCALE_CRYPTO_COM)

        # normalize data
        for keyname in row.keys():
            if (row[keyname] == ''):
                row[keyname] = None
            elif keyname in ['Amount', 'Fee']:
                row[keyname] = locale.atof(row[keyname])

        transaction_date = row['Time']
        transaction_symbol = 'CRO-EUR'
        transaction_type  = None
        transaction_extra = None
        transaction_depot = DEPOT_DEFII
        transaction_konto = KONTO_FIAT
        transaction_amount = row['Amount']
        # Jan 15th 2022 2:49pm
        transaction_date_obj = dateparser.parse(transaction_date)

        # calculate fiat value
        if transaction_date_obj.date() in history[history_symbol]:
            transaction_value = float(history[history_symbol][transaction_date_obj.date()]) * transaction_amount

        if row['Type'] == "Send" and row['Direction'] == 'In':
            transaction_type = "Einlieferung"

        if row['Type'] == "Seed" and row['Direction'] == 'Out':
            transaction_type = "Auslieferung"

        if row['Type'] == "Delegate":
            continue

        if row['Type'] == "Withdraw Delegator Reward":
            transaction_type = "Einlieferung"

        locale.setlocale(locale.LC_ALL, LOCALE_PP)

        dict = {
            'Datum': transaction_date_obj.strftime('%Y-%m-%d'),
            'Uhrzeit': transaction_date_obj.strftime('%H:%M:%S'),
            'Typ': transaction_type,
            'Wert': locale.str(transaction_value),
            'Zusatz': transaction_extra,
            'Notiz': row['Type'],
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