import queue
import socket
import threading
from typing import Set, List, Dict

import select


class Server(threading.Thread):
    def __init__(self, port):
        self.socket: socket.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', port))
        self.socket.listen(5)
        self.socket.setblocking(False)
        self.clients_locking: threading.Lock = threading.Lock()
        self.clients: Set[socket.socket] = set()
        self.message_queues: Dict[socket.socket, queue.Queue] = {}
        self.event = threading.Event()
        self.inputs = [self.socket]
        self.outputs = []
        threading.Thread.__init__(self)

    def run(self):
        # Sockets from which we expect to read

        # Sockets to which we expect to write
        while not self.event.is_set():
            # Wait for at least one of the sockets to be ready for processing
            # print('waiting for the next event\n')
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)    # Handle inputs
            for s in readable:

                if s is self.socket and not self.event.is_set():
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    print('new connection from', client_address)
                    connection.setblocking(0)
                    self.inputs.append(connection)

                    self.outputs.append(connection)

                    # Give the connection a queue for data we want to send
                    self.message_queues[connection] = queue.Queue()
                else:
                    self.remove_connection(s)

                # Handle outputs
            for s in writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except queue.Empty:
                    continue
                    # outputs.remove(s)
                try:
                    s.send(next_msg)
                    s.send(b'\n')
                except OSError:
                    self.remove_connection(s)

                # Handle "exceptional conditions"
            for s in exceptional:
                # Stop listening for input on the connection
                self.remove_connection(s)

                # Remove message queue
                del self.message_queues[s]

    def remove_connection(self, s: socket.socket):
        if s in self.inputs:
            self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        s.close()

    def send_data(self, data_string: str):
        for s in self.message_queues:
            self.message_queues[s].put_nowait(data_string.encode())

    def stop(self):
        self.event.set()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
