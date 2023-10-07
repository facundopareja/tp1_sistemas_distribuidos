from util.queue_methods import (connect_mom,
                                listen_on,)
import json
from filter_by_average import FilterByAverage
from configparser import ConfigParser
import os

def initialize_config():

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")
    config_params = {}
    try:
        config_params["output_queue"] = os.getenv('OUTPUT_QUEUE', config["DEFAULT"]["OUTPUT_QUEUE"])
        config_params["input_queue"] = os.getenv('INPUT_QUEUE', config["DEFAULT"]["INPUT_QUEUE"])
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting client".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting client".format(e))

    return config_params


def main():

    config_params = initialize_config()
    input_queue = config_params["input_queue"]
    output_queue = config_params["output_queue"]
    logging_level = config_params["logging_level"]
    
    filter_by_average = FilterByAverage(output_queue, input_queue)

    connection = connect_mom()
    listen_on(connection.channel(), input_queue, filter_by_average.callback)
    connection.close()

    print(filter_by_average.avg_recieved)

if __name__ == '__main__':
    main()