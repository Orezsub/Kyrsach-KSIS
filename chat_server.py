
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5 import QtCore, QtWidgets
from server_design import Ui_MainWindow  


class Communicate(QObject):
	new_mes = pyqtSignal()

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
		self.CLOSE_CALL = 'cl_call'
		self.SET_LADDR = 's_laddr'
		self.CONNECT_TO_AUDIO_CHAT = 'conn_audio'
		self.DISCONNECT_FROM_AUDIO_CHAT = 'disc_audio'
		self.HISTORY_REQUST = 'history_request'
		self.ACTIVE_CLIENTS = 'active_clients'
		self.MAX_MESSAGE_SIZE = 2048

		self.clients = {}
		self.audio_clients = {}
		self.message_list = []
		self.client_id_and_name = {}
		self.clients_audio_addr = {}

		self.signal = Communicate()
		self.signal.new_mes.connect(self.new_mes)
		
		self.base_message_type = [self.CONNECT, self.DISCONNECT, self.CONNECT_TO_AUDIO_CHAT, \
											self.DISCONNECT_FROM_AUDIO_CHAT]
		self.call_message_type = [self.INCOMMING_CALL, self.ACCEPT_CALL, self.CANCEL_CALL, self.CLOSE_CALL]


	def process_system_message(self, mtype, client_name, client_id, connection, raw_message):
		if mtype == self.DISCONNECT:
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
			audio_socket_address = raw_message[0][-5:]
			print(audio_socket_address)
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
			self.ui.TEdit_for_server_info.append(f'{message} {address}')


	def prepare_message(self, mtype, recipient, client_name, data, client_id, client_ip):
		mes = '†'.join(data)
		message = f' |{client_ip}:{PORT}| {data[0]}'

		if recipient == self.GLOBAL and mtype != self.HISTORY_REQUST:
			self.message_list.append(f'{mtype}†{client_id}†{recipient}†{client_name}†{message}')

		if mtype in self.base_message_type:
			return self.message_constructor(mtype, client_id, recipient, client_name, '', message)

		elif mtype in self.call_message_type:
			for client, audio_addr in self.clients_audio_addr.items():
				if client == client_id:
					return self.message_constructor(mtype, client_id, recipient, client_name, '', audio_addr)

		elif mtype == self.MESSAGE:
			return self.message_constructor(mtype, client_id, recipient, client_name, ' :: ', message)

		elif mtype == self.ACTIVE_CLIENTS:
			return self.message_constructor(mtype, client_id, recipient, client_name, '', mes)


	def message_constructor(self, mtype, client_id, recipient, client_name, symblos, message):
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
			# print(self.clients, 'clients')


	def start_threading(self):
		socket_thread = threading.Thread(target=self.thread, daemon = True)
		socket_thread.start()


if __name__ == "__main__":
	import socket, threading, time, sys
	from time import gmtime, strftime
	from UDPConnection import UDPConnection
	from TCPConnection import TCPConnection
	from AudioServer import AudioSocketServer

	HOST = socket.gethostbyname(socket.gethostname())
	PORT = 50007
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

	audio_socket = AudioSocketServer(HOST, PORT+1)

	sys.exit(app.exec())
