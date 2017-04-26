import sys
import getopt
import converter


def print_usage():
    print("Usage:\n",
          "./currency_converter.py --amount <float>",
          "--input_currency <currency>",
          "[--output_currency <currency>]",
          "[date <DD/MM/YYYY>]\n\n",
          "Where:\n",
          "\t<float> is a float number > 0\n",
          "\t<currency> is 3 letter currency code (USD, EUR...),",
          " or currency symbol ($, £...)\n",
          "\t<DD/MM/YYYY> is format to specify date,",
          "no earlier than 01/01/2000\n",
          "Example:\n",
          "\t./currency_converter.py --amount 200 --input_currency EUR",
          "--output_currency CZK --date 01/11/2015")
    exit(1)


def get_input():
    """Get user input arguments.

    Returns:
        str: User input arguments

    """

    arg_currency_from, arg_currency_to = (None, None)
    arg_amount, arg_date = (None, None)

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'a:o:i:d:',
                                   ["amount=", "output_currency=",
                                    "input_currency=", "date="])
    except getopt.GetoptError:
        print("Error: Parsing of arguments failed.")
        print_usage()

    for opt, arg in opts:
        if opt in ('-i', '--input_currency'):
            arg_currency_from = arg
        elif opt in ('-d', '--date'):
            arg_date = arg
        elif opt in ('-o', '--output_currency'):
            arg_currency_to = arg
        elif opt in ('-a', '--amount'):
            arg_amount = arg
        else:
            print("Error: Unknown argument.")
            print_usage()

    if None in (arg_currency_from, arg_amount):
        print("Error: Missing required argument.\n")
        print_usage()

    try:
        arg_amount = float(arg_amount)
    except ValueError:
        print("Error: Parsing amount argument failed. Amount has to be float.")
        print_usage()

    return arg_currency_from, arg_currency_to, arg_amount, arg_date


if __name__ == "__main__":

    target_currencies = None
    output_data = None

    # Parse user inputs.
    currency_from, currency_to, amount, date = get_input()

    # Create converter.
    currency_converter = converter.Converter(date)

    # Get output_currencies.
    try:
        target_currencies = currency_converter\
            .get_target_currencies(currency_from, currency_to)
    except ValueError as err:
        print("Acquiring input/output currencies failed: ", err)
        print("Program will terminate.")
        exit(1)

    # Convert input_currency to output_currency.
    try:
        output_data = currency_converter\
            .convert_currency(amount, currency_from, target_currencies)
    except ValueError as err:
        print("Conversion failed:", err)
        print("Program will terminate.")
        exit(1)

    # Save results.
    try:
        currency_converter.save_converted_currency(output_data)
    except (IOError, ValueError) as err:
        print("Saving of conversion results failed:", err)
        print("Program will terminate.")
        exit(1)
