import socket
import threading


class Server(threading.Thread):
    def __init__(self, port):
        self.socket = socket.socket()
        self.socket.bind(('', port))
        self.socket.listen(5)
        self.socket.setblocking(True)
        self.clients_locking = threading.Lock()
        self.clients = set()
        threading.Thread.__init__(self)

    def run(self):
        while True:
            connection, address = self.socket.accept()
            print("heard from %s &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&" % (address[0]))
            with self.clients_locking:
                self.clients.add(connection)

    def send_data(self, data_string: str):
        #print("*****************sending data**********************")
        with self.clients_locking:
            for client in self.clients:
                client.send(data_string.encode())
                client.send(b'\n')
