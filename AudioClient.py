import socket
import pyaudio
import wave
from array import array
import threading

class AudioSocketClient(object):
    """docstring for AudioSocket"""
    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()

        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 22100
        self.WIDTH = 2

        self.CONNECT = '00001'
        self.DISCONNECT = '00000'

        self.mute_mic = False
        self.mute_voise = False


    def set_send_audio_stream(self):
        self.send_audio_stream = self.pyaudio.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)


    def set_recv_audio_stream(self):
        self.recv_audio_stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(self.WIDTH),
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        output=True,
                        frames_per_buffer=self.CHUNK)


    def set_host_and_port(self, host, port):
        self.HOST = host
        self.PORT = port


    def create_socket(self):
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_socket.connect((self.HOST, self.PORT))
        self.audio_socket.settimeout(0.5)
        self.laddr = self.audio_socket.getsockname()[1]


    def get_laddr(self):
        return self.laddr

    def send_code(self, code):
        self.audio_socket.send((code+''.zfill(self.CHUNK-len(code))).encode())


    def thread_for_send(self, name, recipient):
        self.set_send_audio_stream()
        # self.send_code(self.CONNECT)
        self.send_audio_stream.start_stream()
        while not self.shutdown_send_thread:
            try:
                while not self.shutdown_send_thread:
                    data  = self.send_audio_stream.read(int(self.CHUNK))
                    dataChunk = array('h', data)
                    vol = max(dataChunk)
                    if(vol > 500):
                        print("Recording Sound...", len(data), len(recipient.encode()))
                        # self.audio_socket.sendall(data)
                        self.audio_socket.sendall(recipient.encode()+data[:len(data)-5])
                    else:
                        pass
                        # print("Silence..")
            except socket.timeout:
                print('timeout')
                continue

            self.close_send_stream()


    def start_sending(self, recipient):
        self.recipient = recipient
        print("*sending")
        self.shutdown_send_thread = False
        audio_send_thread = threading.Thread(target=self.thread_for_send, args=('send', self.recipient), daemon = True)
        audio_send_thread.start()


    def pause_unpause_sending(self):
        if not self.mute_mic:
            self.shutdown_send_thread = True
        else:
            self.start_sending(self.recipient)
        self.mute_mic = not self.mute_mic


    def stop_sending(self):
        self.shutdown_send_thread = True


    def close_send_stream(self):
        print("*done sending")
        self.send_audio_stream.stop_stream()
        self.send_audio_stream.close()


    def thread_for_recv(self, name, default_sender):
        self.set_recv_audio_stream()
        self.recv_audio_stream.start_stream()
        while not self.shutdown_recv_thread:
            try:
                while not self.shutdown_recv_thread:
                    data = self.audio_socket.recv(self.CHUNK*2)

                    sernder = data[:5].decode()
                    data = data[5:]
                    print(len(data), 'recv', sernder)
                    if default_sender == sernder:
                        self.recv_audio_stream.write(data)

            except socket.timeout:
                print('error audio')
                continue
            except UnicodeDecodeError:
                continue

            self.close_recv_stream()


    def start_receiving(self, sender):
        print("*receiving")
        self.sender = sender
        self.shutdown_recv_thread = False
        audio_recv_thread = threading.Thread(target=self.thread_for_recv, args=('recv', self.sender), daemon = True)
        audio_recv_thread.start()


    def pause_unpause_receiving(self):
        if not self.mute_voise:
            self.shutdown_recv_thread = True
        else:
            self.start_receiving(self.sender)
        self.mute_voise = not self.mute_voise


    def stop_receiving(self):
        self.shutdown_recv_thread = True


    def close_recv_stream(self):
        print("*done receiving")
        self.recv_audio_stream.stop_stream()
        self.recv_audio_stream.close()


    def close_send_and_recv_stream(self):
        self.stop_sending()
        self.stop_receiving()


    def close_all(self):
        self.close_send_and_recv_stream()
        self.pyaudio.terminate()
        self.audio_socket.close()
        print("*closed")

