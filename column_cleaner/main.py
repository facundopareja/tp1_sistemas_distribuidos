from column_cleaner import ColumnCleaner
from configparser import ConfigParser


def initialize_config():

    config = ConfigParser(allow_no_value=True)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")
    config_params = {}
    try:
        config_params["input_exchange"] = config["DEFAULT"]["INPUT_EXCHANGE"]
        config_params["input_queue"] = config["DEFAULT"]["INPUT_QUEUE"]
        config_params["logging_level"] = config["DEFAULT"]["LOGGING_LEVEL"]
        config_params["output_exchange"] = config["DEFAULT"]["OUTPUT_EXCHANGE"]
        config_params["output_queue"] = config["DEFAULT"]["OUTPUT_QUEUE"]
        config_params["required_columns_flights"] = config["DEFAULT"]["REQUIRED_COLUMNS_FLIGHTS"].split(",")
        config_params["required_columns_airports"] = config["DEFAULT"]["REQUIRED_COLUMNS_AIRPORTS"].split(",")
        config_params["routing_key"] = config["DEFAULT"]["ROUTING_KEY"]
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting client".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting client".format(e))
    return config_params


def main():
    config_params = initialize_config()
    input_queue = config_params["input_queue"]
    input_exchange = config_params["input_exchange"]
    output_exchange = config_params["output_exchange"]
    output_queue = config_params["output_queue"]
    required_columns_flights = config_params["required_columns_flights"]
    required_columns_airports = config_params["required_columns_airports"]
    routing_key = config_params["routing_key"]
    cleaner = ColumnCleaner(output_queue, output_exchange,
                            required_columns_flights,
                            required_columns_airports,
                            routing_key)
    cleaner.run(input_exchange, input_queue)


if __name__ == '__main__':
    main()
