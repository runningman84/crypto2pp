#!/bin/sh

python convert_crypto_com_app.py sample/crypto_transactions_record_xxx_yyy.csv out/crypto_com_app_crypto.csv config_sample.yaml
python convert_crypto_com_app.py sample/fiat_transactions_record_xxx_yyy.csv out/crypto_com_app_fiat.csv config_sample.yaml
python convert_crypto_com_defi.py sample/CRO_Transactions_xxx.csv out/crypto_com_defi.csv config_sample.yaml
