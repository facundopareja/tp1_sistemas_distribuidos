import ast
import json
import signal

from util.file_manager import save_to_file
from util.initialization import initialize_queues
from util.queue_middleware import QueueMiddleware
from util.utils_query_3 import handle_query_3_register
from util.utils_query_4 import handle_query_4_register, handle_query_4
from util.utils_query_5 import handle_query_5
from util.constants import BATCH_SIZE, EOF_FLIGHTS_FILE


class ReducerGroupBy():

    def __init__(self, field_group_by, input_queue,
                 output_queue, query_number):
        self.queue_middleware = QueueMiddleware()
        self.field_group_by = field_group_by
        self.output_queue = output_queue
        self.grouped = {}
        self.input_queue = input_queue
        self.query_number = query_number
        self.operations_map = {4: handle_query_4,
                               5: handle_query_5}
        self.handlers_map = {3: handle_query_3_register,
                             4: handle_query_4_register}
        self.__filename = "stored_flights.txt"
        self.__tmp_flights = []

    def run(self):
        signal.signal(signal.SIGTERM, self.queue_middleware.handle_sigterm)
        initialize_queues([self.output_queue, self.input_queue],
                          self.queue_middleware)
        self.queue_middleware.listen_on(self.input_queue, self.__callback)

    def __callback(self, body):
        flight = json.loads(body)
        op_code = flight.get("op_code")
        if len(self.__tmp_flights) >= BATCH_SIZE:
            save_to_file(self.__tmp_flights, self.__filename)
            self.__tmp_flights = []
        if op_code == EOF_FLIGHTS_FILE:
            if (self.query_number != 3):
                save_to_file(self.__tmp_flights, self.__filename)
                self.__read_file()
            self.__handle_eof()
            self.queue_middleware.send_message(self.output_queue, body)
            self.queue_middleware.finish()
            return
        if (self.query_number == 5):
            self.__tmp_flights.append(flight)
            return

        self.handlers_map[self.query_number](flight, self.grouped)

    def __handle_eof(self):
        for route, flights in self.grouped.items():
            if (self.query_number == 3):
                for flight in flights:
                    self.queue_middleware.send_message(self.output_queue,
                                                       json.dumps(flight))
            else:
                msg = self.operations_map.get(self.query_number,
                                              lambda _: None)(flights)
                self.queue_middleware.send_message(self.output_queue,
                                                   json.dumps(msg))

    def __read_file(self):
        with open(self.__filename, "r") as file:
            for line in file:
                flight = ast.literal_eval(line)
                flight_group_by_field = flight[self.field_group_by]
                self.grouped[flight_group_by_field] = self.grouped.get(
                    flight_group_by_field, [])
                self.grouped[flight_group_by_field].append(flight)
