# crypto2pp
some tools to convert crypto transaction files in order to use them in Portfolio Performance

Crypto.com
============
* Support for App transactions
* Support for Defi transactions (history files are required)
* Download your crypto.com transactions using the export feature in the app
* Download your defi transactions here https://onlyautomate.com/cro/rewards?
* Use the CSV-Import feature of Portfolio Performance to import the output files
    * Fiat transactions are created as data type "Kontoumsätze"
    * Crypto transactions are created as data type "Depotumsätze"
* Rewards, stakings earns are booked as "Einlieferung"
* Portfolio Performance should have "Konten" and "Depots" according to the config file

History
============
* Please store files like history/CRO.csv
* Data can be obtained here https://coinmarketcap.com/de/currencies/crypto-com-coin/historical-data/

Config
============
* The config_smaple.yaml can be used as a sample for your own config.

Test
============
* Use the test.sh script to create data based on some sample data

Future features
============
* Additonal Inputs
    * CakeDefi
    * BISON
* TAX calculations


