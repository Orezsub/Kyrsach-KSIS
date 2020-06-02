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

# cap.set(int(3),320)
# cap.set(int(4),240)
# cap.set(int(5),15)

class Communicate(QObject):
	new_message = pyqtSignal()

class VideoSocket(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle('client')
		self.setGeometry(200, 200, 300, 300)

		self.signal = Communicate()
		self.signal.new_message.connect(self.new_message)

		self.label = QLabel(self)
		self.first_frame = True

		self.scale_percent = 40

		self.shutdown_sending = False
		self.shutdown_receiving = False

		# self.start_image_sending()
		self.start_image_receiving()


	def new_message(self):
		frame = self.frame
		height, width, channel = frame.shape
		bytesPerLine = 3 * width
		qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
		pixmap = QPixmap(qImg)
		self.label.setPixmap(pixmap)

		if self.first_frame:
			self.first_frame = False
			self.label.resize(pixmap.width(), pixmap.height())
			self.resize(pixmap.width(), pixmap.height())

	def thread_image_sending(self):
		self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.send_socket.connect(("192.168.100.5", 50007))
		# socket.connect(("10.211.55.3", 50007))
		cap = cv2.VideoCapture(0)
		while not self.shutdown_sending:
			try:
				while not self.shutdown_sending:
					ret, frame = cap.read()
					if ret:
						try:
							width = int(frame.shape[1] * self.scale_percent / 100)
							height = int(frame.shape[0] * self.scale_percent / 100)
							dim = (width, height)
							resized_frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
							data = cv2.imencode('.jpg', resized_frame)[1].tostring()
							print(len(data))
						except:
							continue

					a = input()
					self.send_socket.sendall(str(len(data)).zfill(6).encode()+data)
			except:
				print('error')
				self.shutdown_sending = True

	def start_image_sending(self):
		Thread_send_image = threading.Thread(target=self.thread_image_sending, daemon = True)
		Thread_send_image.start()

	def thread_image_receiving(self):
		self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.recv_socket.bind(("192.168.100.2", 50008))
		self.recv_socket.listen(10)
		connection, address = self.recv_socket.accept()
		while not self.shutdown_receiving:
			try:
				while not self.shutdown_receiving:
					img = ''.encode()
					img_len = int(connection.recv(6))
					print("img_len ->",img_len)
					totrec = 0

					while totrec<img_len :
						chunk = connection.recv(img_len - totrec)
						img += chunk
						totrec += len(chunk)
					print("recv_len",len(img))

					nparr = np.frombuffer(img, np.uint8)
					frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

					self.frame = frame
					self.signal.new_message.emit()

			except:
				self.shutdown_receiving = True

	def start_image_receiving(self):
		Thread_recv_image = threading.Thread(target=self.thread_image_receiving, daemon = True)
		Thread_recv_image.start()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = VideoSocket()
	ex.show()

	time.sleep(5)
	ex.start_image_sending()

	sys.exit(app.exec_())


