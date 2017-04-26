import unittest
import converter
import json


class ConverterTestInit(unittest.TestCase):

    def test_init_day_invalid(self):
        """Day should be between 01 and 31."""

        new_converter = converter.Converter("00/04/2017")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("32/03/2017")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("01/1/2017")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("31/04/2016")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("29/02/2014")
        self.assertEqual(new_converter.date, "latest")

    def test_init_month_invalid(self):
        """Month should be between 01 and 12."""

        new_converter = converter.Converter("01/00/2017")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("01/13/2017")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("01/1/2017")
        self.assertEqual(new_converter.date, "latest")

    def test_init_year_invalid(self):
        """Year should be between 2000 and current year."""

        new_converter = converter.Converter("01/04/2100")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("01/04/1999")
        self.assertEqual(new_converter.date, "latest")

    def test_init_delimiter_invalid(self):
        """Date has to be in DD/MM/YYYY format."""

        new_converter = converter.Converter("01-04-2100")
        self.assertEqual(new_converter.date, "latest")

        new_converter = converter.Converter("2017/01/01")
        self.assertEqual(new_converter.date, "latest")

    def test_init_valid(self):
        """Internal date YYYY-MM-DD should user input date format DD/MM/YY."""

        new_converter = converter.Converter("01/04/2017")
        self.assertEqual(new_converter.date, "2017-04-01")

        new_converter = converter.Converter("01/01/2000")
        self.assertEqual(new_converter.date, "2000-01-01")


class ConverterTestTranslate(unittest.TestCase):

    def test_translate_valid(self):
        """Known currency symbol should be translated into corresponding
        currency codes and unknown symbol should return empty list."""

        new_converter = converter.Converter()

        currencies = ["EGP", "FKP", "GIP", "GGP", "IMP", "JEP", "LBP", "SHP",
                      "SYP", "GBP"]
        output_currency = "£"

        # Test that known symbol is correctly translated to known currency codes
        translated_currencies = new_converter.translate_symbol(output_currency)
        self.assertCountEqual(currencies, translated_currencies)

        currencies = list()
        output_currency = "?"

        # Test that unknown symbol returns empty list
        translated_currencies = new_converter.translate_symbol(output_currency)
        self.assertCountEqual(currencies, translated_currencies)


class ConverterTestSaveConvertedCurrency(unittest.TestCase):

    def test_save_converted_currency_valid(self):
        """Saved data should match predefined .json format."""

        new_converter = converter.Converter()

        # Prepare data in expected format that will be saved
        data = dict()
        data["input"] = dict()
        data["input"]["amount"] = 200
        data["input"]["currency"] = "USD"

        data["output"] = dict()
        data["output"]["amount"] = 5200
        data["output"]["currency"] = "CZK"

        # Save data by calling tested function
        new_converter.save_converted_currency(data)
        file = new_converter.config.get("Output_file", "file")

        # Load saved data and verify they were saved properly
        try:
            with open(file) as data_file:
                loaded_data = json.load(data_file)
            self.assertEqual(loaded_data, data)
        except (IOError, ValueError) as err:
            print("Error running test", err)


class ConverterTestConvertCurrency(unittest.TestCase):

    def test_convert_currency_valid(self):
        """Proper rates should be used for currency conversion"""

        new_converter = converter.Converter()

        # Build currency rates that will be used for conversion
        data = dict()
        data["USD"] = 1.5
        data["CZK"] = 25
        data["CAD"] = 1.3
        new_converter.currency_rates = data

        amount = 300.0

        # Build expected output of tested function for comparison
        converted_data = dict()
        converted_data["input"] = dict()
        converted_data["input"]["amount"] = amount
        converted_data["input"]["currency"] = "USD"
        converted_data["output"] = dict()
        converted_data["output"]["CZK"] = 5000.0

        # Convert data and test they match to expected output
        converted = new_converter.convert_currency(amount, "USD", ["CZK", ])
        self.assertEqual(converted, converted_data)

        # Test conversion into multiple output_currencies
        converted_data["output"]["CAD"] = 260.0
        converted = new_converter.convert_currency(amount,
                                                   "USD", ["CZK", "CAD"])
        self.assertEqual(converted, converted_data)

    def test_convert_currency_invalid(self):
        """Conversion of negative and non-float amount should fail"""

        new_converter = converter.Converter()

        # Build known currencies
        data = dict()
        data["USD"] = 1.5
        data["CZK"] = 25
        data["CAD"] = 1.3
        new_converter.currency_rates = data

        self.assertRaises(ValueError, new_converter.convert_currency,
                          200, "USD", "CZK")
        self.assertRaises(ValueError, new_converter.convert_currency,
                          -200.0, "USD", "CZK")


class ConverterTestGetTargetCurrencies(unittest.TestCase):

    def test_get_target_currencies_valid(self):
        """Currency symbol should be translated into matching currency code"""

        new_converter = converter.Converter()

        # Build known currencies
        data = dict()
        data["USD"] = 1.5
        data["CZK"] = 25
        data["CAD"] = 1.3
        new_converter.currency_rates = data

        # Test getting target currency from currency code
        target_currencies = new_converter.get_target_currencies("USD", "CZK")
        self.assertEqual(target_currencies, ["CZK", ])

        # Test getting target currencies from currency symbol
        target_currencies = new_converter.get_target_currencies("USD", "£")
        self.assertEqual(target_currencies,
                         ["EGP", "FKP", "GIP", "GGP", "IMP", "JEP", "LBP",
                          "SHP", "SYP", "GBP"])

        # Test getting target currencies from unknown output_currency
        target_currencies = new_converter.get_target_currencies("USD", "XXX")
        self.assertIn("USD", target_currencies)
        self.assertIn("CZK", target_currencies)
        self.assertIn("CAD", target_currencies)
        self.assertEqual(len(target_currencies), 3)

        # Test getting target currencies from missing output_currency
        target_currencies = new_converter.get_target_currencies("USD", None)
        self.assertIn("USD", target_currencies)
        self.assertIn("CZK", target_currencies)
        self.assertIn("CAD", target_currencies)
        self.assertEqual(len(target_currencies), 3)

    def test_get_target_currencies_invalid(self):
        """Unknown or missing input_currency should fail"""

        new_converter = converter.Converter()

        # Build known currencies
        data = dict()
        data["USD"] = 1.5
        data["CZK"] = 25
        data["CAD"] = 1.3
        new_converter.currency_rates = data

        # Use unknown input_currency
        self.assertRaises(ValueError, new_converter.get_target_currencies,
                          "XXX", "CZK")
        # Use missing input_currency
        self.assertRaises(ValueError, new_converter.get_target_currencies,
                          None, "CZK")


class ConverterTestDownloadRates(unittest.TestCase):

    def test_download_rates_valid(self):
        """Latest rates should be downloaded, if no date is specified."""

        new_converter = converter.Converter()

        # Download latest currency rates
        latest_rates = new_converter.download_rates()
        latest_timestamp = latest_rates["timestamp"]
        self.assertIn("rates", latest_rates)

        # Download historical currency rates
        historical_converter = converter.Converter("01/01/2010")
        historical_rates = historical_converter.download_rates()
        historical_timestamp = historical_rates["timestamp"]
        self.assertIn("rates", historical_rates)

        # Historical and latest rates should be different
        self.assertNotEqual(latest_timestamp, historical_timestamp)


if __name__ == '__main__':
    unittest.main()
