import socket
import pyaudio
import wave
import time
import threading


class AudioSocketServer(object):
    """docstring for AudioSocketServer"""
    def __init__(self, host, port):
        super().__init__()
        self.HOST = host
        self.PORT = port
        self.CHUNK = 1024*2*4
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

                    print(len(data), i)
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
        while True:
            print('CONNECTED')
            connection, address = self.server_socket.accept()
            self.clients[connection] = str(address[1])
            self.start_audio_receiving(connection, address)


    def start_threading(self):
        socket_thread = threading.Thread(target=self.thread_new_connection)
        socket_thread.start()

    def start_audio_receiving(self, connection, address):
        self.shutdown = False
        Thread_recv_TCP = threading.Thread(target=self.thread_audio_receiving,
                                    args=(connection, address), daemon = True)
        Thread_recv_TCP.start()

if __name__ == '__main__':
    audio_server = AudioSocketServer()
    audio_server.start_threading()






    # CHUNK = 1024
    # FORMAT = pyaudio.paInt16
    # CHANNELS = 1
    # RATE = 12100
    # RECORD_SECONDS = 4
    # WAVE_OUTPUT_FILENAME = "server_output.wav"
    # WIDTH = 2
    # frames = []

# p = pyaudio.PyAudio()
# stream = p.open(format=p.get_format_from_width(WIDTH),
#                 channels=CHANNELS,
#                 rate=RATE,
#                 output=True,
#                 frames_per_buffer=CHUNK)


# HOST = '192.168.100.2'
# PORT = 50007
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))
# s.listen(1)
# conn, addr = s.accept()
# print ('Connected by', addr)
# data = conn.recv(CHUNK)

# i=1
# while data != b'':
#     data = conn.recv(CHUNK)
#     stream.write(data)
#     i=i+1
#     print(i, len(data))
#     frames.append(data)

# wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)
# wf.writeframes(b''.join(frames))
# wf.close()

# stream.stop_stream()
# stream.close()
# p.terminate()
# conn.close()


# import socket
# import threading

# class Server:
#     def __init__(self):
#             self.ip = socket.gethostbyname(socket.gethostname())
#             while 1:
#                 try:
#                     self.port = int(input('Enter port number to run on --> '))

#                     self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                     self.s.bind((self.ip, self.port))

#                     break
#                 except:
#                     print("Couldn't bind to that port")

#             self.connections = []
#             self.accept_connections()

#     def accept_connections(self):
#         self.s.listen(100)

#         print('Running on IP: '+self.ip)
#         print('Running on port: '+str(self.port))
        
#         while True:
#             c, addr = self.s.accept()

#             self.connections.append(c)

#             threading.Thread(target=self.handle_client,args=(c,addr,)).start()
        
#     def broadcast(self, sock, data):
#         for client in self.connections:
#             if client != self.s and client != sock:
#                 try:
#                     client.send(data)
#                 except:
#                     pass

#     def handle_client(self,c,addr):
#         while 1:
#             try:
#                 data = c.recv(1024)
#                 self.broadcast(c, data)
            
#             except socket.error:
#                 c.close()

# server = Server()
