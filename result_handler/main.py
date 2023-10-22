import multiprocessing
import os
import pika
import signal

from result_handler import ResultHandler


def main():
    listen_backlog = int(os.environ['LISTEN_BACKLOG'])
    query_handler = ResultHandler(listen_backlog)
    try:
        query_handler.run()
    except pika.exceptions.ChannelWrongStateError:
        pass


if __name__ == '__main__':
    main()