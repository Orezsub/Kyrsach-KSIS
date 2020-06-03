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
        self.send_code(self.CONNECT)
        self.send_audio_stream.start_stream()
        while not self.shutdown_send_thread:
            # try:
            while not self.shutdown_send_thread:
                data  = self.send_audio_stream.read(int(self.CHUNK/2))
                dataChunk = array('h', data)
                vol = max(dataChunk)
                if(vol > 500):
                    print("Recording Sound...", len(data), len(recipient.encode()))
                    self.audio_socket.sendall(recipient.encode()+data[:len(data)-5])
                else:
                    pass
                    # print("Silence..")
            # except:
            self.close_send_stream()


    def start_sending(self, recipient):
        print("*sending")
        self.shutdown_send_thread = False
        audio_send_thread = threading.Thread(target=self.thread_for_send, args=('send', recipient), daemon = True)
        audio_send_thread.start()


    def pause_unpause_sending(self):
        if self.send_audio_stream.is_active():
            self.send_audio_stream.stop_stream()
        else:
            self.send_audio_stream.start_stream()


    def stop_sending(self):
        self.shutdown_send_thread = True


    def close_send_stream(self):
        print("*done sending")
        self.send_audio_stream.stop_stream()
        self.send_audio_stream.close()


    def thread_for_recv(self, name, default_recipient):
        self.recv_audio_stream.start_stream()
        while not self.shutdown_recv_thread:
            try:
                while not self.shutdown_recv_thread:
                    data = self.audio_socket.recv(self.CHUNK)
                    if len(data) == 0: self.shutdown_recv_thread = True

                    recipient = data[:5].decode()
                    data = data[5:]
                    print(len(data), 'recv')
                    if self.recv_audio_stream.is_active() and default_recipient == recipient:
                        self.recv_audio_stream.write(data)

            except socket.timeout:
                print('error')

            if self.shutdown_recv_thread:
                self.close_recv_stream()
                self.send_code(self.DISCONNECT)


    def start_receiving(self, recipient):
        print("*receiving")
        self.shutdown_recv_thread = False
        audio_recv_thread = threading.Thread(target=self.thread_for_recv, args=('recv', recipient), daemon = True)
        audio_recv_thread.start()


    def pause_unpause_receiving(self):
        if self.recv_audio_stream.is_active():
            self.recv_audio_stream.stop_stream()
        else:
            self.recv_audio_stream.start_stream()


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

# if __name__ == '__main__':
#     audio = AudioSocketClient()
#     audio.set_host_and_port('192.168.100.2', 50008)
#     audio.create_socket()
#     audio.start_sending('00000')
#     # audio.start_receiving()

#     while True:
#         a = input()
#         # if a == 'p':
#         #     audio.pause_sending()
#         # elif a == 'u':
#         #     audio.unpause_sending()
#         # elif a == 's':
#         #     audio.pause_receiving()
#         # elif a == 'a':
#         #     audio.unpause_receiving()
