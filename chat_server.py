
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5 import QtCore, QtWidgets
from server_design import Ui_MainWindow  


class Communicate(QObject):
	new_mes = pyqtSignal()
	# new_audio = pyqtSignal()

class MainWindow(QtWidgets.QWidget):
	def __init__(self):
		super(MainWindow, self).__init__()
		
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		self.GLOBAL = 'Global'
		self.CONNECT = 'connect'
		self.DISCONNECT = 'disconnect'
		self.MESSAGE = 'message'
		self.INCOMMING_CALL = 'in_call'
		self.ACCEPT_CALL = 'ac_call'
		self.CANCEL_CALL = 'ce_call'
		self.SET_LADDR = 's_laddr'
		# self.AUDIO = 'audio'
		# self.NEW_CONTENT = 'new_content'
		# self.DEL_CONTENT = 'del_content'
		self.HISTORY_REQUST = 'history_request'
		self.ACTIVE_CLIENTS = 'active_clients'
		self.MAX_MESSAGE_SIZE = 2048

		self.clients = {}
		self.audio_clients = {}
		self.message_list = []
		# self.content_list = []
		self.client_id_and_name = {}
		self.clients_audio_addr = {}

		self.signal = Communicate()
		self.signal.new_mes.connect(self.new_mes)
		# self.signal.new_audio.connect(self.new_audio)
		
		self.base_message_type = [self.CONNECT, self.DISCONNECT]
		self.call_message_type = [self.INCOMMING_CALL, self.ACCEPT_CALL, self.CANCEL_CALL]
	# def new_audio(self):
	# 	data = self.audio_socket.get_new_message()
	# 	recipient = data[:5]
	# 	audio_data = data[5:]
	# 	connection, address = self.audio_socket.get_client_connection_and_address()
	# 	self.send_audio_to_client(audio_data, recipient, connection)

	# def send_audio_to_client(self, audio_data, recipient, connection):
	# 	for client, addr in self.audio_clients.items():
	# 		if connection != client and addr == recipient:
	# 			# if message:
	# 			print('send to', addr)
	# 			client.send(audio_data)

	def process_system_message(self, mtype, client_name, client_id, connection, raw_message):
		# for client, addr in self.clients.items():
		# 	if connection == client:
		# 		break
		# else:
		# 	address = str(connection)[-7:-2]
		# 	self.clients[connection] = str(address)
		# 	self.client_id_and_name[address] = client_name

		if mtype == self.DISCONNECT:
			print(self.clients)
			print(connection)
			print(self.client_id_and_name)
			self.client_id_and_name.pop(self.clients[connection])
			self.clients_audio_addr.pop(self.clients[connection])
			self.clients.pop(connection)

		elif mtype == self.CONNECT:
			active_clients = ''
			for _id, _name in self.client_id_and_name.items():
				active_clients += f'†{_name}†{_id}'

			connection.send(bytes(f'active_clients{active_clients}'.encode('utf-8')))
			self.client_id_and_name[client_id] = client_name

		elif mtype == self.SET_LADDR:
			audio_socket_address = raw_message[-5:]
			self.clients_audio_addr[client_id] = audio_socket_address

		elif mtype == self.HISTORY_REQUST:
			connection.send(bytes(f'history_start†'.encode('utf-8')))
			history = ''
			time.sleep(0.2)

			for mes in self.message_list:
				if sys.getsizeof(history+f'{mes}†') >= self.MAX_MESSAGE_SIZE:
					connection.send(bytes(f'history†{history}'.encode('utf-8')))
					history = ''
					time.sleep(0.15)

				history += f'{mes}†'

			connection.send(bytes(f'history†{history}'.encode('utf-8')))
			time.sleep(0.2)
			connection.send(bytes(f'history_end†'.encode('utf-8')))

			# time.sleep(0.2)
			# loaded_content = ''
			# for content_info in self.content_list:
			# 	loaded_content += f'†{content_info[0]}†{content_info[1]}†{content_info[2]}†{content_info[3]}'
			# connection.send(bytes(f'loaded_content{loaded_content}'.encode('utf-8')))


	def new_mes(self):
		data = self.socket.get_new_message()
		connection, address = self.socket.get_client_connection_and_address()

		try:
			mtype, recipient, client_name, raw_message = data[0], data[1], data[2], data[3:]
		except:
			return
		client_id, client_ip = str(address[1]), address[0]

		message = self.prepare_message(mtype, recipient, client_name, raw_message, client_id, client_ip)
		self.process_system_message(mtype, client_name, client_id, connection, raw_message)

		if mtype != self.HISTORY_REQUST and mtype != self.SET_LADDR:
			self.send_message_to_client(message, recipient, connection)
			# if mtype != self.AUDIO:
			self.ui.TEdit_for_server_info.append(f'{message} {address}')


	def prepare_message(self, mtype, recipient, client_name, data, client_id, client_ip):
		mes = '†'.join(data)
		# if mtype == self.AUDIO:
		# 	message = data[0]
		# else:
		message = f' |{client_ip}:{PORT}| {data[0]}'


		if recipient == self.GLOBAL and mtype != self.HISTORY_REQUST:
			self.message_list.append(f'{mtype}†{client_id}†{recipient}†{client_name}†{message}')

		if mtype in self.base_message_type:
			return self.message_constructor(mtype, client_id, recipient, client_name, '', message)

		elif mtype in self.call_message_type:
			for client, addr in self.clients_audio_addr.items():
				if client == client_id:
					return self.message_constructor(mtype, client_id, recipient, client_name, '', addr)

		elif mtype == self.MESSAGE:
			return self.message_constructor(mtype, client_id, recipient, client_name, ' :: ', message)

		elif mtype == self.ACTIVE_CLIENTS:
			return self.message_constructor(mtype, client_id, recipient, client_name, '', mes)

		# elif mtype == self.NEW_CONTENT:
		# 	if recipient == self.GLOBAL:
		# 		for i in range(0, len(content), 2):
		# 			self.content_list.append([client_id, recipient, content[i], content[i+1]])
					
		# 	return self.message_constructor(mtype, client_id, recipient, client_name, '', message, content)

		# elif mtype == self.DEL_CONTENT:
		# 	if recipient == self.GLOBAL:

		# 		for content_info in self.content_list:
		# 			if content_info[2] == content[0]:
		# 				self.content_list.remove(content_info)

		# 	return self.message_constructor(mtype, client_id, recipient, client_name, '', message, content)


	def message_constructor(self, mtype, client_id, recipient, client_name, symblos, message):
		# content_text = '†'.join(content)
		return f'{mtype}†{client_id}†{recipient}†{client_name}†{symblos}{message}'


	def send_message_to_client(self, message, recipient, connection):
		for client, addr in self.clients.items():
			if connection != client and (addr == recipient or recipient == self.GLOBAL):
				if message:
					client.send(bytes(message.encode('utf-8')))


	def set_socket(self, socket):
		self.socket = socket


	def set_audio_socket(self, audio_socket):
		self.audio_socket = socket


	def thread(self):
		while True:
			connection, address = self.socket.accept()
			self.clients[connection] = str(address[1])
			print(self.clients, 'clients')

	# def audio_thread(self):
	# 	while True:
	# 		connection, address = self.audio_socket.accept()
	# 		self.audio_clients[connection] = str(address[1])


	def start_threading(self):
		socket_thread = threading.Thread(target=self.thread, daemon = True)
		socket_thread.start()


	# def start_audio_threading(self):
	# 	audio_socket_thread = threading.Thread(target=self.audio_thread, daemon = True)
	# 	audio_socket_thread.start()

# def thread_incomming_call():
# 	CHUNK = 1024
# 	FORMAT = pyaudio.paInt16
# 	CHANNELS = 1
# 	RATE = 12100
# 	WIDTH = 2
# 	p = pyaudio.PyAudio()
# 	stream = p.open(format=p.get_format_from_width(WIDTH),
# 		channels=CHANNELS,
# 		rate=RATE,
# 		output=True,
# 		frames_per_buffer=CHUNK)

# 	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	s.bind(("192.168.100.2", 50009))
# 	s.listen(1)
# 	conn, addr = s.accept()
# 	print ('Connected by', addr)
# 	data = conn.recv(CHUNK)

# 	i=1
# 	while data != b'':
# 		print('data')
# 		data = conn.recv(CHUNK)
# 		stream.write(data)

# 	stream.stop_stream()
# 	stream.close()
# 	p.terminate()
# 	conn.close()

if __name__ == "__main__":
	import socket, threading, time, sys
	from time import gmtime, strftime
	from UDPConnection import UDPConnection
	from TCPConnection import TCPConnection
	from AudioServer import AudioSocketServer
	# import pyaudio

	HOST = socket.gethostbyname(socket.gethostname())
	PORT = 50007
	# AUDIO_PORT = 50008
	LISTEN_ALL_HOST = '0.0.0.0'
	
	app = QtWidgets.QApplication(sys.argv)
	application = MainWindow()
	application.show()

	UDP_socket = UDPConnection(HOST, PORT)
	UDP_socket.setsockopt_reuseaddr()
	UDP_socket.bind(LISTEN_ALL_HOST, PORT) 	
	UDP_socket.send_address_to_sender()
	UDP_socket.start_UDP_receiving()
		
	TCP_socket = TCPConnection(application.signal.new_mes)
	TCP_socket.setsockopt_reuseaddr()
	TCP_socket.bind(HOST, PORT)
	TCP_socket.listen(10)
	TCP_socket.set_server_socket()

	application.set_socket(TCP_socket)
	application.start_threading()

	# audio_socket = TCPConnection(application.signal.new_audio)
	# audio_socket.setsockopt_reuseaddr()
	# audio_socket.bind(HOST, AUDIO_PORT)
	# audio_socket.listen(10)
	# audio_socket.set_server_socket()

	audio_socket = AudioSocketServer(HOST, PORT+1)
	# application.set_audio_socket(audio_socket)

	# Thread = threading.Thread(target=thread_incomming_call, daemon = True)
	# Thread.start()

	sys.exit(app.exec())
	