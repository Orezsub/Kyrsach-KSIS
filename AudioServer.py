import socket
import pyaudio
import wave
import time
import threading


class AudioSocketServer(object):
    """docstring for AudioSocketServer"""
    def __init__(self, host, port):
        # super().__init__()
        self.HOST = host
        self.PORT = port
        self.CHUNK = 1024
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(1)


        self.clients = {}
        self.incomming_addresses = []
        self.shutdown = False

        self.start_threading()

    def del_connection_from_cliets_dict(self, connection):
        for client, addr in self.clients.items():
            if connection == client:# and addr == recipient:
                self.clients.pop(connection)
                break

    def thread_audio_receiving(self, connection, address):
        print('lol')
        i = 0
        while not self.shutdown:
            try:
                while not self.shutdown:
                    data = connection.recv(self.CHUNK)

                    recipient = data[:5]

                    if len(data) == 0:
                        print('e', self.shutdown)
                        self.del_connection_from_cliets_dict(connection)
                        break

                    print(len(data), i, recipient)
                    i += 1
                    for client, addr in self.clients.items():
                        if connection != client:# and addr == recipient:
                            print('send to', addr)
                            client.sendall(data)
                # break
            except ConnectionResetError:
                print('error reset')
                self.del_connection_from_cliets_dict(connection)
                # self.shutdown = True
                break
            except BrokenPipeError:
                print('error pipe')
                self.del_connection_from_cliets_dict(connection)
                break
            break


    def thread_new_connection(self):
        print('wait for connections')
        while True:
            connection, address = self.server_socket.accept()
            print('CONNECTED from', str(address[1]))
            self.clients[connection] = str(address[1])
            self.start_audio_receiving(connection, address)


    def start_threading(self):
        socket_thread = threading.Thread(target=self.thread_new_connection, daemon = True)
        socket_thread.start()

    def start_audio_receiving(self, connection, address):
        self.shutdown = False
        Thread_recv_TCP = threading.Thread(target=self.thread_audio_receiving,
                                    args=(connection, address))#, daemon = True)
        Thread_recv_TCP.start()

if __name__ == '__main__':
    audio_server = AudioSocketServer('192.168.100.2', 50008)
    # audio_server.start_threading()
