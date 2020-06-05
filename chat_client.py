# -*- coding: utf-8 -*-
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QObject
from client_design import Ui_MainWindow  
from os import path

class Communicate(QObject):
	new_message = pyqtSignal()


class MainWindow(QtWidgets.QMainWindow):
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
		self.AUDIO_GLOBAL = 'globl'
		self.CONNECT_TO_AUDIO_CHAT = 'conn_audio'
		self.DISCONNECT_FROM_AUDIO_CHAT = 'disc_audio'
		self.RECV_ADDR = 'recv_addr'
		self.SEND_ADDR = 'send_addr'
		self.CLOSE_ADDR = 'clos_addr'
		self.ARROW = '-->'
		self.HISTORY = 'history'
		self.HISTORY_START = 'history_start'
		self.HISTORY_END = 'history_end'
		self.HISTORY_REQUEST = 'history_request'
		self.ACTIVE_CLIENTS = 'active_clients'

		self.BASE_COLOR = '#F0F0F0'
		self.RED_COLOR = '#DB4747'

		self.clients = [self.GLOBAL]
		self.dialog_button_dict = {}
		self.message_list = []
		self.audio_dialog_button_dict = {}
		self.clients_id_and_name = {}

		self.signal = Communicate()
		self.signal.new_message.connect(self.new_message)
		self.recipient_address = self.GLOBAL

		self.called_client_address = None
		self.active_video_call = False

		self.dialog_layout = self.set_layout_with_scroll_area(self.ui.verticalLayout, self.ui.scrollArea)
		self.audio_layout = self.set_layout_with_scroll_area(self.ui.verticalLayout_2, self.ui.scrollArea_3)
		self.find_server()


	def set_layout_with_scroll_area(self, ui_layout, ui_scroll_area):
		layout = ui_layout
		Widget = Qt.QWidget()
		Widget.setLayout(layout)
		scroll_area = ui_scroll_area
		scroll_area.setWidget(Widget)
		return layout


	def add_button_into_layout(self, name, layout, button_dict, info, action=None, set_style=False):
		button = Qt.QPushButton(f'{name}')
		if set_style:
			button.setStyleSheet(f'background : {self.BASE_COLOR};')

		layout.addWidget(button)
		button_dict[button] = info
		if action:
			button.clicked.connect(action)

		return button


	def dialog_button_click(self):
		sender = self.sender()
		for button, address in self.dialog_button_dict.items():
			if sender == button:
				self.recipient_address = address

				self.change_dialog_button_color(button, self.BASE_COLOR)
				self.display_all_messages_from_sender(address)
				self.display_clients_in_audio_chat(address)
				break


	def change_dialog_button_color(self, button, color):
		button.setStyleSheet(f'background : {color};')


	def find_dialog_button_for_change_color(self, sender, recipient):
		if recipient != self.GLOBAL:
			for but, addr in self.dialog_button_dict.items():

				if sender == addr and self.recipient_address != addr:
					self.change_dialog_button_color(but, self.RED_COLOR)	

		elif recipient == self.GLOBAL and self.recipient_address != self.GLOBAL:
			for but, addr in self.dialog_button_dict.items():

				if self.GLOBAL == addr:
					self.change_dialog_button_color(but, self.RED_COLOR)


	def add_dialog_button_if_no_such(self, sender_address, client_name):
		for button, address in self.dialog_button_dict.items():
			if sender_address == address:
				return button

		return self.add_button_into_layout(client_name, self.dialog_layout, self.dialog_button_dict,\
												 sender_address, self.dialog_button_click, True)


	def append_new_message_into_chat(self, sender, recipient, message):
		if recipient == self.GLOBAL and self.recipient_address == self.GLOBAL:
				self.ui.TEdit_Chat_Text.append(message)

		elif recipient != self.GLOBAL and self.recipient_address == sender:
				self.ui.TEdit_Chat_Text.append(message)


	def del_button_from_layuot(self, button_dict, address):
		for button, addr in button_dict.items():
			if address == addr:
				button.setParent(None)
				del_button = button
		button_dict.pop(del_button)


	def if_any_connect_or_disconnect(self, mtype, sender, client_name):
		if mtype == self.CONNECT:
			self.clients.append(sender)
			self.ui.ComboBox_Of_Clients.addItem(client_name)

		elif mtype == self.DISCONNECT:
			self.ui.ComboBox_Of_Clients.removeItem(self.clients.index(sender))
			self.clients.remove(sender)
			self.del_button_from_layuot(sender, self.dialog_button_dict)


	def show_context_menu(self, name):
		# self.sender_info = self.sender()
		self.message_box = QtWidgets.QMessageBox()
		self.message_box.setText(f'{name} call you')

		button = Qt.QPushButton('Accept')
		button.clicked.connect(self.accept_incomming_call)
		self.message_box.addButton(button, QtWidgets.QMessageBox.AcceptRole)

		button = Qt.QPushButton('Cancel')
		button.clicked.connect(self.cancel_incomming_call)
		self.message_box.addButton(button, QtWidgets.QMessageBox.RejectRole)

		self.message_box.exec_()


	def accept_incomming_call(self):
		print('send')
		self.shutdown_incomming_call = True
		self.message_box.setParent(None)
		self.send_message_to_server(self.ACCEPT_CALL, self.called_client_address, 'accepted call', False)

		self.start_call(self.incomming_audio_addr, self.laddr)


	def cancel_incomming_call(self):
		self.shutdown_incomming_call = True
		self.message_box.setParent(None)
		self.send_message_to_server(self.CANCEL_CALL, self.recipient_address, 'canceled call', False)


	def display_clients_in_audio_chat(self, recipient_address):
		for button, _ in self.audio_dialog_button_dict.items():
				button.setParent(None)
		if recipient_address == self.GLOBAL:
			for client_id, name in self.clients_id_and_name.items():
				self.add_button_into_layout(name, self.audio_layout, self.audio_dialog_button_dict, client_id)
		else:
			if self.called_client_address == self.recipient_address:
				self.add_button_into_layout(self.name, self.audio_layout, self.audio_dialog_button_dict, self.name)
				self.add_button_into_layout('name', self.audio_layout, self.audio_dialog_button_dict, self.called_client_address)


	def display_all_messages_from_sender(self, recipient_address):
		# message[0] - sender, message[1] - recipient, message[2] - message_text
		self.ui.TEdit_Chat_Text.clear()
		if recipient_address == self.GLOBAL:					
			for message in self.message_list:
				if message[1] == recipient_address:

					if message[0] == self.ARROW:
						self.ui.TEdit_Chat_Text.append(f'{message[0]} {message[2]}')
					else:
						self.ui.TEdit_Chat_Text.append(f'{message[2]}')

		else:
			for message in self.message_list:
				if message[1] == recipient_address:

					if message[0] == self.ARROW:
						self.ui.TEdit_Chat_Text.append(f'{message[0]} {message[2]}')
					else:
						self.ui.TEdit_Chat_Text.append(f'{message[2]}')
						
				elif message[0] == recipient_address and message[1] != self.GLOBAL:
					self.ui.TEdit_Chat_Text.append(f'{message[2]}')


	def thread_incomming_call(self):
		while not self.shutdown_incomming_call:
			try:
				while not self.shutdown_incomming_call:
					# playsound('call.mp3')

					time.sleep(1)
			except:
				self.shutdown_incomming_call = True


	def start_call(self, audio_address, laddr):
		# self.audio_socket.set_send_audio_stream()
		self.audio_socket.set_recv_audio_stream()
		self.audio_socket.start_sending(audio_address)
		self.audio_socket.start_receiving(laddr)


	def check_system_message(self, data):
		if data[0] == self.HISTORY_START:
			for i in reversed(range(len(self.message_list))):
				if self.message_list[i][1] == self.GLOBAL:
					del self.message_list[i] 
			return True

		elif data[0] == self.HISTORY:
			try:
				for i in range(1,len(data),5):
					self.message_list.append([data[i+1],data[i+2],f'{data[i+3]} :: {data[i+4]}'])
			except:
				pass
			return True

		elif data[0] == self.HISTORY_END:
			for but, addr in self.dialog_button_dict.items():
				if addr == self.GLOBAL:
					but.click()
			return True

		elif data[0] == self.CONNECT_TO_AUDIO_CHAT:
			self.add_button_into_layout(data[3], self.audio_layout, self.audio_dialog_button_dict, data[1])
			self.clients_id_and_name[data[1]] = data[3]

		elif data[0] == self.DISCONNECT_FROM_AUDIO_CHAT:
			self.del_button_from_layuot(self.audio_dialog_button_dict, data[1])
			self.clients_id_and_name.pop(data[1])

		elif data[0] == self.ACTIVE_CLIENTS:
			if len(data) != 2:
				for i in range(1,len(data),2):
					self.ui.ComboBox_Of_Clients.addItem(data[i])
					self.clients.append(data[i+1])
			return True

		return False


	def check_call_message(self, data):
		if data[0] == self.INCOMMING_CALL:
			self.called_client_address = data[1]
			self.incomming_audio_addr = data[4]
			self.shutdown_incomming_call = False
			Thread_in_call = threading.Thread(target=self.thread_incomming_call, daemon = True)
			Thread_in_call.start()
			self.show_context_menu(data[3])
			return True

		elif data[0] == self.ACCEPT_CALL:
			self.incomming_audio_addr = data[4]
			self.called_client_address = data[1]

			self.start_call(self.incomming_audio_addr, self.laddr)
			return True

		elif data[0] == self.CANCEL_CALL:
			return True

		elif data[0] == self.CLOSE_CALL:
			self.audio_socket.close_send_and_recv_stream()
			self.called_client_address = None
			return True

		elif data[0] == self.RECV_ADDR:
			recv_ip = self.video_socket.get_recv_ip()
			recv_port = self.video_socket.get_recv_port()
			self.send_message_to_server(self.SEND_ADDR, data[1], f'${recv_ip}${recv_port}$', False)

			self.video_socket.show()
			info = data[4].split('$')
			self.send_ip, self.send_port = info[1], info[2]
			print(self.send_ip, self.send_port)
			self.video_socket.set_send_socket(self.send_ip, self.send_port)
			self.video_socket.start_image_sending()
			self.active_video_call = True
			return True

		elif data[0] == self.SEND_ADDR:
			self.video_socket.show()
			info = data[4].split('$')
			self.send_ip, self.send_port = info[1], info[2]
			print(self.send_ip, self.send_port)
			self.video_socket.set_send_socket(self.send_ip, self.send_port)
			self.video_socket.start_image_sending()
			return True

		elif data[0] == self.CLOSE_ADDR:
			self.video_socket.close_socket()
			return True

		return False


	def new_message(self):
		data = self.TCP_socket.get_new_message()
		print(data)
		if not self.check_system_message(data) and not self.check_call_message(data):
			try:
				mtype = data[0]
				sender = data[1]
				recipient = data[2]
				client_name = data[3]
				message = data[3]+data[4]

				self.add_dialog_button_if_no_such(sender, client_name)
				self.if_any_connect_or_disconnect(mtype, sender, client_name)
				self.append_new_message_into_chat(sender, recipient, message)

				self.message_list.append([sender, recipient, message])
				
				time.sleep(0.2)
				self.find_dialog_button_for_change_color(sender, recipient)	
			except:
				pass


	def find_server(self):
		client_host = ss.gethostbyname(ss.gethostname())
		client_port = 50007

		UDP_socket = UDPConnection(client_host, client_port)
		UDP_socket.setsockopt_broadcast()

		UDP_socket.start_UDP_receiving()
		UDP_socket.start_UDP_sending()

		time.sleep(0.05)
		host, port = UDP_socket.get_finded_ip_and_port()
		self.ui.Edit_IP.setText(host)
		self.ui.Edit_Port.setText(str(port))
		UDP_socket.stop()

		self.script_for_mas_os()


	def log_in(self):
		# try:
		self.host = self.ui.Edit_IP.text()
		self.port = int(self.ui.Edit_Port.text())
		self.name = self.ui.Edit_Name.text()

		self.TCP_socket.set_host_and_port(self.host, self.port)
		self.TCP_socket.set_client_name(self.name)
		self.TCP_socket.connect()

		self.audio_socket = AudioSocketClient()
		self.audio_socket.set_host_and_port(self.host, self.port+1)
		self.audio_socket.create_socket()
		self.laddr = str(self.audio_socket.get_laddr())
		self.send_message_to_server(self.SET_LADDR, self.GLOBAL, self.laddr, False)

		self.video_socket = VideoSocket()
		# self.video_socket.bind_recv_socket()
		self.video_socket.setWindowTitle(self.name)

		self.add_dialog_button_if_no_such(self.GLOBAL, self.GLOBAL)

		self.ui.Btn_Log_In.setDisabled(True)
		self.ui.Btn_Log_Out.setDisabled(False)
		self.ui.Btn_Send_Message.setDisabled(False)
		self.ui.Btn_History_Request.setDisabled(False)
		# except:
		# 	pass
		self.script_for_mas_os()


	def prepare_and_send_message(self):	
		message = self.ui.TEdit_Input_Message.toPlainText()

		if message:
			self.send_message_to_server(self.MESSAGE, self.recipient_address, message, True)


	def send_message_to_server(self, mtype, recipient, message, print_message):
		time_now = strftime("%H:%M:%S %d-%m-%Y", gmtime())
		mes = f' |{time_now}| {message}'

		if mtype != self.HISTORY_REQUEST and mtype != self.SET_LADDR:
			self.message_list.append([self.ARROW, recipient, mes])
		self.TCP_socket.send(mtype, recipient, f'{message}')#{content}')

		if print_message:
			self.ui.TEdit_Input_Message.clear()
			self.ui.TEdit_Chat_Text.append(f'{self.ARROW} {mes}')
			self.ui.TEdit_Input_Message.setFocus()
		self.script_for_mas_os()


	def log_out(self):
		self.ui.Btn_Log_In.setDisabled(False)
		self.ui.Btn_Log_Out.setDisabled(True)
		self.ui.Btn_Send_Message.setDisabled(True)
		self.ui.Btn_History_Request.setDisabled(True)

		self.close_connection()
		self.close_all_dialogs()
		for i in reversed(range(1, self.ui.ComboBox_Of_Clients.count())):
			self.ui.ComboBox_Of_Clients.removeItem(i)
			del self.clients[i]
		self.message_list.clear()

		self.script_for_mas_os()


	def close_connection(self):
		self.TCP_socket.disconnect()


	def close_all_dialogs(self):
		for dialog, addr in self.dialog_button_dict.items():
			dialog.setParent(None)
		self.dialog_button_dict.clear()


	def history_request(self):
		self.send_message_to_server(self.HISTORY_REQUEST, self.GLOBAL, 'history request', False)
		self.script_for_mas_os()


	def call_recipient_button_click(self):
		self.called_client_address = self.recipient_address
		if self.recipient_address != self.GLOBAL:
			self.send_message_to_server(self.INCOMMING_CALL, self.called_client_address, 'incomming call', False)
		else:
			self.start_call(self.AUDIO_GLOBAL, self.AUDIO_GLOBAL)
			self.clients_id_and_name[self.name] = self.name
			self.add_button_into_layout(self.name, self.audio_layout, self.audio_dialog_button_dict, self.name)
			self.send_message_to_server(self.CONNECT_TO_AUDIO_CHAT, self.GLOBAL, 'connect to global audio chat', False)

	def mute_mic_button_click(self):
		self.audio_socket.pause_unpause_sending()


	def mute_voise_button_click(self):
		self.audio_socket.pause_unpause_receiving()


	def close_call_button_click(self):
		if self.called_client_address != self.GLOBAL:
			self.send_message_to_server(self.CLOSE_CALL, self.called_client_address, 'close call', False)
		else:
			self.send_message_to_server(self.DISCONNECT_FROM_AUDIO_CHAT, self.GLOBAL, 'disconnect frm global audio chat', False)
			self.clients_id_and_name.pop(self.name)
			self.del_button_from_layuot(self.audio_dialog_button_dict, self.name)
		self.audio_socket.close_send_and_recv_stream()
		self.called_client_address = None


	def video_button_click(self):
		if not self.active_video_call:
			if self.recipient_address != self.GLOBAL:
				recv_ip = self.video_socket.get_recv_ip()
				recv_port = self.video_socket.get_recv_port()
				self.send_message_to_server(self.RECV_ADDR, self.recipient_address, f'${recv_ip}${recv_port}$', False)
				self.video_client_address = self.recipient_address
		else:
			self.video_socket.close_socket()
			self.send_message_to_server(self.CLOSE_ADDR, self.video_client_address, 'close video call', False)
		self.active_video_call = not self.active_video_call
		# self.video_socket.start_image_sending()

	def change_active_dialog(self):
		name = self.ui.ComboBox_Of_Clients.currentText()
		address = self.clients[self.ui.ComboBox_Of_Clients.currentIndex()]

		button = self.add_dialog_button_if_no_such(address, name)
		button.click()


	def set_TCP_socket(self, socket):
		self.TCP_socket = socket


	# def set_audio_socket(self, audio_socket):
	# 	pass
		# self.audio_socket = AudioSocketClient()


	def script_for_mas_os(self):
		self.hide()
		self.show()


	def closeEvent(self, event): 
		self.close_connection()
		self.video_socket.close()


if __name__ == "__main__":
	import sys
	import socket as ss
	import threading
	import time
	from UDPConnection import UDPConnection
	from TCPConnection import TCPConnection
	from AudioClient import AudioSocketClient
	from VideoClient import VideoSocket
	from time import gmtime, strftime
	from playsound import playsound


	app = QtWidgets.QApplication(sys.argv)
	application = MainWindow()
	application.show()

	TCP_socket = TCPConnection(application.signal.new_message)
	application.set_TCP_socket(TCP_socket)

	# audio_socket = AudioSocketClient()
	# application.set_audio_socket(audio_socket)

	application.ui.Btn_Find_Server.clicked.connect(application.find_server)
	application.ui.Btn_Log_In.clicked.connect(application.log_in)
	application.ui.Btn_Send_Message.clicked.connect(application.prepare_and_send_message)
	application.ui.Btn_Log_Out.clicked.connect(application.log_out)
	application.ui.Btn_History_Request.clicked.connect(application.history_request)
	application.ui.Btn_Call.clicked.connect(application.call_recipient_button_click)
	application.ui.Btn_Mute_Mic.clicked.connect(application.mute_mic_button_click)
	application.ui.Btn_Mute_Voise.clicked.connect(application.mute_voise_button_click)
	application.ui.Btn_Close_Call.clicked.connect(application.close_call_button_click)
	application.ui.Btn_Video.clicked.connect(application.video_button_click)
	application.ui.ComboBox_Of_Clients.currentIndexChanged.connect(application.change_active_dialog)

	# video_socket = VideoSocket()
	# video_socket.show()

	sys.exit(app.exec_())
