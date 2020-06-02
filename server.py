import socket, threading, time

import cv2
import numpy as np
import sys
import math

from PyQt5.QtCore import pyqtSignal, QObject
# from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtGui import QPixmap, QImage

class Communicate(QObject):
	new_message = pyqtSignal()

class App(QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle('Тест')
		self.setGeometry(200, 200, 300, 300)

		self.signal = Communicate()
		self.signal.new_message.connect(self.new_message)

		self.label = QLabel(self)
		self.first_frame = True

		Thread_recv_TCP = threading.Thread(target=self.thread_TCP_receiving, daemon = True)
		Thread_recv_TCP.start()

	# def load_image(self, file_name):
	# 	pixmap = QPixmap(file_name)

	# 	self.label = QLabel(self)
	# 	self.label.setPixmap(pixmap)
	# 	self.label.resize(pixmap.width(), pixmap.height())

	# 	self.resize(pixmap.width(), pixmap.height())

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


	def thread_TCP_receiving(self):
		TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# TCP_socket.bind(("10.211.55.3", 50007))
		TCP_socket.bind(("192.168.100.2", 50007))
		TCP_socket.listen(10)

		BUF = 8192*2 + 4

		connection, address = TCP_socket.accept()

		shutdown = False
		is_image = False

		img = ''.encode()
		# first_mes = True
		# only_part_of_len = False
		# i = 0
		while not shutdown:
			# try:
			print("cicle")
			# first = True
			# readed_len = -1
			# message_len = BUF
			# dif = -1

			# package = 0
			# package_count = -1

			while not shutdown:
				# if is_image and package > package_count:
				# 	nparr = np.frombuffer(img, np.uint8)
				# 	frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
				# 	# cv2.imshow('Live Feed', frame)
				# 	# cv2.imwrite('messigray.png',frame)
				# 	self.frame = frame
				# 	self.signal.new_message.emit()

				# 	# if cv2.waitKey(1) & 0xFF == ord('q'):
				# 	# 	break

				# data = connection.recv(BUF)#.decode("utf-8")
				# try:
				img = ''.encode()
				img_len = int(connection.recv(6))
				print("img_len ->",img_len)
				totrec = 0
				# msgArray = []
				while totrec<img_len :
					chunk = connection.recv(img_len - totrec)
					# if chunk == '':
					# 	raise RuntimeError("Socket connection broken")
					# msgArray.append(chunk)
					img += chunk
					totrec += len(chunk)
				print("recv_len",len(img))
				# ost = BUF - (img_len % BUF)
				# a = connection.recv(ost)

				nparr = np.frombuffer(img, np.uint8)
				frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
				self.frame = frame
				self.signal.new_message.emit()
				# except:
				# 	print('len', len(img))
				# 	i += 1
				# 	img += connection.recv(BUF*BUF)
				# 	# print('len', len(img))
				# 	print('error', i)
				# 	# break

			# 	# print(data[:6], data[-4:])
			# 	# print(data, 'end')
				

			# 	if not data:
			# 			shutdown = True
			# 			break

			# 	if package <= package_count:
			# 		pass
			# 	else:
			# 		# print(data[:6])
			# 		# error = False
			# 		# try:
			# 		print(str(data[:6]))
			# 		# if data[:5] == b'xxxxx':
			# 		# 	print("lox")
			# 		# 	continue
			# 		message_len = int(data[:6])
			# 		package_count = math.ceil(message_len // BUF)
			# 		package = 0
			# 		print(package_count)
			# 		data = data[6:]
			# 		is_image = True
			# 		# except:
			# 		# 	error = True
			# 		# 	print("error")
			# 		img = ''.encode()


			# 	package += 1
			# 	img += data
			break

		print('close')
		time.sleep(5)

if __name__ == '__main__':
	app = QApplication(sys.argv)

	ex = App()
	# ex.load_image('messigray.png')
	ex.show()

	sys.exit(app.exec_())

