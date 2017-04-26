import configparser
import datetime
import collections
import json
import urllib.request


class DateError(Exception):
    pass


class Converter():
    """Converter class.

    The converter class provides attributes and methods to download/archive
    currency rates and to convert them between each other.

    """

    def __init__(self, date="latest"):
        self.date = date
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.currency_rates = self.get_rates()

    def get_config_element(self, section, element):
        """Returns requested element from given section of the config.ini file.

        Args:
            section (str): section of config.ini file to search for.
            element (str): section's element of config.ini file to search for.

        Returns:
            str: Element from config.ini file

        """

        config_element = None

        try:
            config_element = self.config.get(section, element)

        except configparser.NoSectionError as err:
            print("Error parsing config.ini file:", err)
            print("Program will terminate.")
            exit(1)

        return config_element

    def get_rates(self):
        """Acquires and returns currency rates.

        The function first checks if archive file with previously downloaded
        currency rates exists and if it's readable. If not, currency rate for
        requested timestamp are downloaded, archived and returned. If archive
        file already exists, it is searched for required timestamp. If it is
        found, respective currency rates are returned. If the timestamp is not
        found in the file, currency rates are requested timestamp are
        downloaded and archived.

        Returns:
            dict: Dictionary of pairs key - currency code and value - exchange
                  rate

        """

        file = self.get_config_element("Saved_currencies", "file")

        try:
            # Read archive file with already downloaded currency rates.
            with open(file) as data_file:
                data = json.load(data_file)

            if self.date == "latest":
                date = datetime.datetime.now()
            else:
                date = datetime.datetime.strptime(self.date, "%Y-%m-%d")

        # If archive file does not exist/is empty.
        except (IOError, ValueError):
            # Download currency rates and archive them.
            rates = self.download_rates()
            self.archive_rates(rates)
            return rates["rates"]

        # Archive file exists - search it if requested timestamp is archived.
        for key in data:
            saved_date = datetime.datetime.utcfromtimestamp(float(key))
            if date.year == saved_date.year \
                    and date.month == saved_date.month \
                    and date.day == saved_date.day:
                return data[key]

        # Archive file doesn't contain requested timestamp. Do download/archive.
        rates = self.download_rates()
        self.archive_rates(rates)

        return rates["rates"]

    def download_rates(self):
        """Returns converted currencies

        The function converts original_currency to all target_currencies per
        currency rates stored as a instance attribute currency_rates. Converted
        currencies are returned in a dictionary, with 'input' and 'output' keys.

        Returns:
            dict: Currency rates as returned by API

        """
        err_message = "Unknown error"
        error_codes = ({400: "Client requested rates for an unsupported "
                             "base currency",
                        401: "Client did not provide an App ID",
                        403: "Access restricted for repeated over-use "
                             "or other reason.",
                        404: "Client requested a non-existent resource/route",
                        429: "Client doesn’t have permission to access "
                             "requested route/feature"})
        req = None
        app_id = self.get_config_element("App_ID", "id")

        if self.date == "latest":
            url = "https://openexchangerates.org/api/latest.json?app_id="
            url = "".join((url, app_id))
        else:
            url = "https://openexchangerates.org/api/historical/"
            url = "".join((url, self.date, ".json?app_id=", app_id))

        try:
            req = urllib.request.urlopen(url)
        except urllib.request.HTTPError as err:
            if err.code in error_codes:
                err_message = error_codes[err.code]
            print("Error downloading currency rates: ",
                  err, ": ",  err_message)
            print("Program will terminate.")
            exit(1)

        data = json.loads(req.read().decode(req.info()
                                            .get_param('charset') or 'utf-8'))

        return data

    def archive_rates(self, data):
        """Archives conversion rates.

        The function loads archive file to archive recent currency rates in a
        form of dictionary, where key is timestamp of the currency rates and
        value is dictionary of key-value pairs, where key is currency code
        and value is respective currency rate. If the file exists, the current
        rates are added to the file. If the file does not exist, new archive
        file is created.

        Args:
            data (dict): Currency rates with respective timestamp.

        """

        file = self.get_config_element("Saved_currencies", "file")

        try:
            # Read archive file to read data to append new currency rates.
            with open(file, "r") as data_file:
                loaded_data = json.load(data_file)
        except (IOError, ValueError) as err:
            # If archive file doesn't exist/is empty, create new dict().
            loaded_data = dict()

        loaded_data[data["timestamp"]] = data["rates"]

        try:
            # Save archive file.
            with open(file, "w") as data_file:
                json.dump(loaded_data, data_file)
        except (IOError, ValueError) as err:
            print("Saving of archived rates failed:", err)

        return

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        """Converts user's input date from DD/MM/YYYY to YYYY-MM-DD format.

        Args:
            date (str): date in DD/MM/YYYY format.

        Returns:
            str: date in YYYY-MM-DD format if input date was valid, 'latest'
                 otherwise

        """

        new_date = "latest"

        current_date = datetime.datetime.now()
        parsed_date = collections.namedtuple("parsed_date", "day month year")

        if date is None:
            print("Using {0} exchange rates.".format(new_date))
            self.__date = new_date
            return

        try:
            if len(date) != 10:
                raise DateError("Invalid date format: "
                                "Date must be in DD/MM/YYY format.")

            parsed_date = parsed_date(*date.split("/"))

            year = int(parsed_date.year)
            month = int(parsed_date.month)
            day = int(parsed_date.day)

            if not 2000 <= year <= current_date.year:
                raise DateError("Invalid date format: "
                                "Year must be between 2000 and {0}."
                                .format(current_date.year))

            if not 1 <= month <= 12:
                raise DateError("Invalid date format: "
                                "Month must be between 01 and 12.")

            if month == 2 and day > 28:
                if day == 29 and year in [yr for yr in range(2000, year)
                                          if (yr % 4 == 0)]:
                    pass
                else:
                    raise DateError("Invalid date format: Day out of range.")

            if not 1 <= day <= 31:
                raise DateError("Invalid date format: Day out of range.")

            if day == 31 and month not in (1, 3, 5, 7, 8, 10, 12):
                raise DateError("Invalid date format: Day out of range.")

        except (TypeError, ValueError, DateError) as err:
            print(err)
        else:
            # Build parsed date in yyyy-mm-dd that is accepted by currency API.
            new_date = "-".join((parsed_date.year,
                                 parsed_date.month, parsed_date.day))
        finally:
            print("Using {0} exchange rates.".format(new_date))
            self.__date = new_date

        return

    def get_target_currencies(self, original_currency, target_currency):
        """Returns list of currency codes, to which conversion will be made.

        The function parses and validates output_currencies as user's input. It
        builds and returns a list of output_currency codes - 1 currency code, if
        output_currency is known currency code, all currency codes, if
        output_currency is missing or unknown, list of respective currency
        codes, if currency symbol is given.

        Args:
            original_currency (str): input_currency user input.
            target_currency (str): output_currency user input.

        Returns:
            list: List of output_currency codes

        """

        if original_currency and len(original_currency) != 3:
            raise ValueError("Currency symbol as input parameter not supported")

        # Check if input_currency is known.
        if original_currency not in self.currency_rates:
            raise ValueError("Currency {0} invalid or not supported"
                             .format(original_currency))

        # Check if output_currency is a currency symbol.
        target_currencies = self.translate_symbol(target_currency)

        # If output_currency is a symbol, return respective output_currencies.
        if target_currencies:
            return target_currencies

        # Check if output_currency is known currency code.
        if target_currency in self.currency_rates:
            target_currencies = [target_currency, ]
        else:
            # If output_currency is unknown, use all known currencies.
            target_currencies = [key for key in self.currency_rates]

        return target_currencies

    def convert_currency(self, amount, original_currency, target_currencies):
        """Returns converted currencies

        The function converts original_currency to all target_currencies per
        currency rates stored as a instance attribute currency_rates. Converted
        currencies are returned in a dictionary, with 'input' and 'output' keys.

        Args:
            amount (float): amount to be converted
            original_currency (str): currency code.
            target_currencies (list): list of currency codes.

        Returns:
            dict: List of output_currency codes

        """

        if not isinstance(amount, float):
            raise ValueError("Value has to be float type.")

        if amount < 0:
            raise ValueError("Value cannot be negative.")

        data = dict()
        data["input"] = dict()
        data["input"]["amount"] = amount
        data["input"]["currency"] = original_currency

        data["output"] = dict()

        original_rate = self.currency_rates[original_currency]

        # Convert input_currency to all known output_currencies.
        for currency in target_currencies:
            try:
                target_rate = self.currency_rates[currency]
                data["output"][currency] = round((amount/original_rate)
                                                 * target_rate, 2)
            except KeyError:
                print("Currency {0} not supported, skipping.".format(currency))

        return data

    def save_converted_currency(self, data):
        """Saves data into Output_file specified in config.ini

        Args:
            data (dict): data to be saved.

        """

        file = self.get_config_element("Output_file", "file")

        with open(file, 'w') as outfile:
            json.dump(data, outfile)

        print("Results saved into {0} file.".format(file))

        return

    def translate_symbol(self, currency):
        """Translate currency symbol to currency code

        The function takes input and searches for a match with a currency
        symbol in currency table .json file. If match is found, it returns
        list of respective currency codes. If no match is found, it returns a
        list of currency codes per input parameter.

        Args:
            currency (str): currency code/symbol.

        Returns:
            list: List of output_currency codes

        """

        currencies = None
        file = self.get_config_element("Currency_table", "file")

        try:
            with open(file) as data_file:
                data = json.load(data_file)
            currencies = data[currency]
        except IOError as err:
            print("Error loading currency symbols file:", err)
            print("Program will terminate.")
            exit(1)
        except KeyError:
            # Output_currency is not found within known symbols.
            currencies = list()

        return currencies
