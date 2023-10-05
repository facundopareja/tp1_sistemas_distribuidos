import socket
import logging
import signal

from util.queue_methods import connect_mom, send_message_to
from util import protocol


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.mom_connection = connect_mom()
        self.channel = self.mom_connection.channel()
        self._running = True
        self._reading_file = True
        self._operations_map = {
            0: self.__handle_eof,
            1: self.__read_line
        }

    def run(self):
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        client_sock = self.__accept_new_connection()
        try:
            while self._running and self._reading_file:
                self.__handle_client_connection(client_sock)
        except OSError:
            if not self._running:
                logging.info('action: sigterm received')
            else:
                raise
            return
        finally:
            logging.info(
                'action: done with file | result: success')
            client_sock.close()

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            header = self.__read_exact(2, client_sock)
            payload = self.__read_exact(int.from_bytes(
                header, byteorder='big'), client_sock)
            op_code = protocol.get_opcode(payload)
            data = self._operations_map.get(op_code, lambda _: 0)(payload)
            # TODO: error handling
            if data == 0:
                logging.error(
                    "action: receive_message | result: fail | "
                    f"error: received unknown operation code: {op_code}")
        except OSError as e:
            logging.error(
                f"action: receive_message | result: fail | error: {e}")
            pass

    def __read_exact(self, bytes_to_read, client_sock):
        bytes_read = client_sock.recv(bytes_to_read)

        while len(bytes_read) != bytes_to_read:
            new_bytes_read = client_sock.recv(bytes_to_read - len(bytes_read))
            bytes_read += new_bytes_read

        return bytes_read

    def __send_exact(self, answer, client_sock):
        bytes_sent = 0
        while bytes_sent < len(answer):
            chunk_size = client_sock.send(answer[bytes_sent:])
            bytes_sent += chunk_size

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(
            f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def handle_sigterm(self, signum, frame):
        logging.info(
            f'action: sigterm received | signum: {signum}, frame:{frame}')
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        self._running = False
        logging.info('action: close_server | result: success')
        return

    def __read_line(self, payload):
        msg = protocol.decode_to_str(payload)
        send_message_to(self.channel, "full_flight_registers", msg)

    def __handle_eof(self, payload):
        msg = protocol.encode_eof()
        send_message_to(self.channel, "full_flight_registers", msg)
        self._reading_file = False
