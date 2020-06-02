from PyQt5 import QtCore, QtWidgets
import socket, threading, time
from time import gmtime, strftime


class TCPConnection(QtWidgets.QWidget):
	"""docstring for TCPConnection"""
	def __init__(self, signal):
		super().__init__()
		self.GLOBAL = 'Global'
		self.CONNECT = 'connect'
		self.DISCONNECT = 'disconnect'
		self.MAX_MESSAGE_SIZE = 2048

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_name = ''
		self.message_signal = signal
		self.is_server = False


	def send(self, mtype,receiver, message, exstra_message=''):
		time_now = strftime("%H:%M:%S %d-%m-%Y", gmtime())
		message = f' |{time_now}| {message}'
		# try:
		self.socket.send(bytes(f'{mtype}†{receiver}†[{self.client_name}]†{message}{exstra_message}', encoding='UTF-8'))
		# except OSError:
		# 	pass

	# def send_audio(self,receiver, message, size):
	# 	try:
	# 		# sys_message = f'{mtype}†{receiver}†[{self.client_name}]†'
	# 		print('send audio')
	# 		self.audio_socket.sendall((receiver).encode()+message[:size-len(receiver)])
	# 		# self.socket.sendall(message[:size-len(sys_message)-20])
	# 		# print("TCP", len(message[:size-len(sys_message)]))
	# 		# print(len(message), len(str(message).encode('UTF-8')))
	# 		# print()
	# 		# print(len(message[:size-len(sys_message)-20]))
	# 		# print(len(sys_message+str(message[:size-len(sys_message)])))

	# 	except OSError:
	# 		pass

	def connect(self):
		self.socket.connect((self.host, self.port))
		self.send(self.CONNECT, self.GLOBAL, 'connected to chat')
		self.start_TCP_receiving(None,None)


	def setsockopt_reuseaddr(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


	def bind(self, host, port):
		self.socket.bind((host, port))


	def listen(self, count):
		self.socket.listen(count)


	def accept(self):
		connection, address = self.socket.accept()
		self.start_TCP_receiving(connection, address)
		return connection, address


	# def accept_audio(self):
	# 	connection, address = self.socket.accept()
	# 	self.start_audio_receiving(connection, address)
	# 	return connection, address


	def set_server_socket(self):
		self.is_server = True


	def set_client_connection_and_address(self, connection, address):
		self.connection = connection
		self.address = address


	def get_client_connection_and_address(self):
		return self.connection, self.address


	def set_new_message(self, message):
		self.message = message


	def get_new_message(self):
		return self.message


	def set_host_and_port(self, host, port):
		self.host = host
		self.port = port


	def set_client_name(self, client_name):
		self.client_name = client_name


	def thread_TCP_receiving(self, connection, address):
		while not self.shutdown:
			try:
				while not self.shutdown:
					if self.is_server:
						data = connection.recv(self.MAX_MESSAGE_SIZE).decode("utf-8").split('†')
						self.set_client_connection_and_address(connection, address)

					else:
						data = self.socket.recv(self.MAX_MESSAGE_SIZE).decode("utf-8").split('†')
						
					self.set_new_message(data)
					if not data[0]: return
					self.message_signal.emit()

					time.sleep(0.2)
			except:
				self.shutdown = True


	# def thread_audio_receiving(self, connection, address):
	# 	print('start recv')
	# 	while not self.shutdown_audio_recv:
	# 		try:
	# 			while not self.shutdown_audio_recv:
	# 				if self.is_server:
	# 					data = connection.recv(self.MAX_MESSAGE_SIZE)#.decode("utf-8").split('†')
	# 					self.set_client_connection_and_address(connection, address)

	# 				else:
	# 					data = self.socket.recv(self.MAX_MESSAGE_SIZE)#.decode("utf-8").split('†')
						
	# 				self.set_new_message(data)
	# 				if not data[0]: return
	# 				self.message_signal.emit()

	# 				# time.sleep(0.2)
	# 		except:
	# 			self.shutdown_audio_recv = True
	# 	print('stop recv')


	def start_TCP_receiving(self, connection, address):
		self.shutdown = False
		Thread_recv_TCP = threading.Thread(target=self.thread_TCP_receiving,
									args=(connection, address), daemon = True)
		Thread_recv_TCP.start()


	# def start_audio_receiving(self, connection, address):
	# 	self.shutdown_audio_recv = False
	# 	Thread_recv_audio = threading.Thread(target=self.thread_audio_receiving,
	# 								args=(connection, address), daemon = True)
	# 	Thread_recv_audio.start()


	def disconnect(self):
		self.send(self.DISCONNECT, self.GLOBAL, 'disconnected from chat')
		self.shutdown = True 
		self.socket.close()
