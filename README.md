# Currency converter

## Usage:
```
 ./currency_converter.py --amount <float> --input_currency <currency_code> [--output_currency {<currency_code>, <currency_symbol>} ] [--date <DD/MM/YYYY>]
```
### Where:
```
 <float> is a float number > 0
 <currency_code> is 3 letter currency code (USD, EUR...)
 <currency_symbol> is currency symbol ($, £...)
 <DD/MM/YYYY> is format to specify date, no earlier than 01/01/2000
```
  
### Example:
 	./currency_converter.py --amount 200 --input_currency EUR --output_currency CZK --date 01/11/2015
  
## Notes:
- Input_currency parameter supports currency codes (USD, EUR...)
- Output_currency parameter supports both currency codes and currency symbols
- If currency symbol ($, £...) is used as output_currency, the input_currency is converted to all currency codes that share the currency symbol
- If date argument is not used, the latest currency rates are downloaded/used 
- Each time currency rates are downloaded, they are archived into .json file. When the program runs, it looks into this archive file first, if currency rates for that given (or latest) date are already archived. If yes, those currency rates are used, instead of being downloaded again
- Result of conversion is saved into .json file

## Config file:
- The program uses config.ini file
- It allows customizing names of output file, archive file and currency symbols table
- It contains ID required by API to download currency rates

## API
- openexchangerates.org
- Used to download latest/historical currency rates
- Free account allows 1000 requests a month
- ID is saved in config.ini
