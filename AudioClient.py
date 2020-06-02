import socket
import pyaudio
import wave
from array import array
import threading

class AudioSocketClient(object):
    """docstring for AudioSocket"""
    def __init__(self):
        super().__init__()
        self.CHUNK = 1024*2*4
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 22100
        self.WIDTH = 2

        p = pyaudio.PyAudio()

        self.audio_stream_in = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

        self.audio_stream_out = p.open(format=p.get_format_from_width(self.WIDTH),
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
        self.laddr = self.audio_socket.getsockname()[1]

    def get_laddr(self):
        return self.laddr

    def thread_for_send(self, name, recipient):
        while not self.shutdown_audio_thread:
            # try:
            while not self.shutdown_audio_thread:
                data  = self.audio_stream_in.read(self.CHUNK)
                dataChunk = array('h', data)
                vol = max(dataChunk)
                if(vol > 500):
                    print("Recording Sound...", len(data))
                    self.audio_socket.sendall(recipient.encode()+data[:len(data)-5])
                    # print(len(data))
                else:
                    pass
                    # print("Silence..")
            # except:
            self.shutdown_audio_thread = True
        print("*done sending")
        self.audio_stream_in.stop_stream()
        self.audio_stream_in.close()
        p.terminate()
        self.audio_socket.close()
        print("*closed")


    def start_sending(self, recipient):
        print("*sending")
        self.shutdown_audio_thread = False
        audio_send_thread = threading.Thread(target=self.thread_for_send, args=('send', recipient))#, daemon = True)
        audio_send_thread.start()

    def pause_sending(self):
        self.audio_stream_in.stop_stream()

    def unpause_sending(self):
        self.audio_stream_in.start_stream()

    def stop_sending(self):
        self.shutdown_audio_thread = True

    def thread_for_recv(self):
        while not self.shutdown_audio_thread:
            # try:
            while not self.shutdown_audio_thread:
                data = self.audio_socket.recv(self.CHUNK)
                if len(data) == 0: self.shutdown_audio_thread = True
                data = data[5:]
                print(len(data), 'recv')
                if self.audio_stream_out.is_active():
                    self.audio_stream_out.write(data)
            # except IOError:
            #     print('error')
            # except:
            #     self.shutdown_audio_thread = True
        print("*done receiving")
        self.audio_stream_out.stop_stream()
        self.audio_stream_out.close()
        p.terminate()
        self.audio_socket.close()
        print("*closed")


    def start_receiving(self):
        print("*receiving")
        self.shutdown_audio_thread = False
        audio_recv_thread = threading.Thread(target=self.thread_for_recv)#, daemon = True)
        audio_recv_thread.start()

    def pause_receiving(self):
        self.audio_stream_out.stop_stream()

    def unpause_receiving(self):
        self.audio_stream_out.start_stream()

if __name__ == '__main__':
    audio = AudioSocketClient()
    # audio.start_sending()
    audio.start_receiving()

    while True:
        a = input()
        if a == 'p':
            audio.pause_sending()
        elif a == 'u':
            audio.unpause_sending()
        elif a == 's':
            audio.pause_receiving()
        elif a == 'a':
            audio.unpause_receiving()
