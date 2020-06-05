import socket, threading, time

import cv2
import numpy as np
import sys
import math

import pyaudio
import wave

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtGui import QPixmap, QImage

class CommunicateSignal(QObject):
	new_message = pyqtSignal()

class VideoSocket(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle('client')
		self.setGeometry(200, 200, 300, 300)

		self.signal = CommunicateSignal()
		self.signal.new_message.connect(self.new_message)

		self.label = QLabel(self)
		self.first_frame = True
		self.scale = True

		self.scale_percent = 40

		self.bind_recv_socket()

		self.start_image_receiving()


	def set_send_socket(self, ip, port):
		self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.send_socket.connect((ip, int(port)))


	def bind_recv_socket(self):
		self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.recv_ip = socket.gethostbyname(socket.gethostname())
		self.recv_port = 50009
		self.send_port = self.recv_port+1
		try:
			self.recv_socket.bind((self.recv_ip, self.recv_port))
			print(self.recv_ip, self.recv_port)
		except:
			self.send_port = self.recv_port
			print(self.recv_ip, self.recv_port+1)
			self.recv_socket.bind((self.recv_ip, self.recv_port+1))
		self.recv_socket.listen(10)


	def get_recv_ip(self):
		return self.recv_ip


	def get_recv_port(self):
		return self.recv_port


	def new_message(self):
		frame = self.frame
		height, width, channel = frame.shape
		dif = 1000/width
		resized_frame = cv2.resize(frame, (1000, int(height*dif)), interpolation = cv2.INTER_AREA)
		height, width, channel = resized_frame.shape
		bytesPerLine = 3 * width
		qImg = QImage(resized_frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
		pixmap = QPixmap(qImg)
		self.label.setPixmap(pixmap)

		if self.first_frame:
			self.first_frame = False
			self.label.resize(pixmap.width(), pixmap.height())
			self.resize(pixmap.width(), pixmap.height())


	def thread_image_sending(self):
		cap = cv2.VideoCapture(0)
		while not self.shutdown_sending:
			try:
				while not self.shutdown_sending:
					ret, frame = cap.read()
					if ret:
						# try:
							width = int(frame.shape[1] * self.scale_percent / 100)
							height = int(frame.shape[0] * self.scale_percent / 100)
							dim = (width, height)
							resized_frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
							data = cv2.imencode('.jpg', resized_frame)[1].tostring()

							if self.scale:
								if len(data) < 45_000:
									self.scale_percent += 5
								elif len(data) > 55_000:
									self.scale_percent -= 5
								else:
									self.scale = False

							print(len(frame), len(resized_frame), len(data))
							self.send_socket.sendall(str(len(data)).zfill(6).encode()+data)

			except BrokenPipeError:
				# self.restart_video_thread()
				break

		print('end sending')
		self.close()


	def start_image_sending(self):
		self.shutdown_sending = False
		Thread_send_image = threading.Thread(target=self.thread_image_sending, daemon = True)
		Thread_send_image.start()

	def restart_video_thread(self):
		self.start_image_sending()

	def stop_image_sending(self):
		self.shutdown_sending = True


	def thread_image_receiving(self):
		connection, address = self.recv_socket.accept()
		connection.settimeout(0.5)
		while not self.shutdown_receiving:
			try:
				while not self.shutdown_receiving:
					img = ''.encode()
					img_len = int(connection.recv(6))
					# print("img_len ->",img_len)
					totrec = 0

					while totrec<img_len :
						chunk = connection.recv(img_len - totrec)
						img += chunk
						totrec += len(chunk)
					# print("recv_len",len(img))

					nparr = np.frombuffer(img, np.uint8)
					frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

					self.frame = frame
					self.signal.new_message.emit()

			except socket.timeout:
				print('error')
			except ValueError:
				break
			# except:
				# print('rrrr')
				# self.shutdown_receiving = True
		print('end receiving')
		self.close()


	def start_image_receiving(self):
		self.shutdown_receiving = False
		Thread_recv_image = threading.Thread(target=self.thread_image_receiving, daemon = True)
		Thread_recv_image.start()

	def stop_image_receiving(self):
		self.shutdown_receiving = True

	def close_socket(self):
		self.stop_image_sending()
		self.stop_image_receiving()
		self.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = VideoSocket()
	ex.show()

	time.sleep(5)
	ex.start_image_sending()

	sys.exit(app.exec_())


