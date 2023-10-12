from reducer_group_by import ReducerGroupBy
import os
import pika


def initialize_config():
    config_params = {}
    try:
        config_params["field_group_by"] = os.environ['FIELD_GROUP_BY']
        config_params["output_queue"] = os.environ['OUTPUT_QUEUE']
        config_params["input_queue"] = os.environ['INPUT_QUEUE']
        config_params["query_number"] = int(os.environ['QUERY_NUMBER'])
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting client".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting client".format(e))

    return config_params


def main():

    config_params = initialize_config()
    field_group_by = config_params["field_group_by"]
    output_queue = config_params["output_queue"]
    input_queue = config_params["input_queue"]
    query_number = config_params["query_number"]

    reducer_group_by = ReducerGroupBy(field_group_by, input_queue,
                                      output_queue, query_number)

    try:
        reducer_group_by.run()
    except pika.exceptions.ChannelWrongStateError:
        pass


if __name__ == '__main__':
    main()
