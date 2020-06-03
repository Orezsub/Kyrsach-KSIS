# -*- coding: utf-8 -*-
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QObject
from client_design import Ui_MainWindow  
from os import path

# import pyaudio
# import wave
# from array import array

class Communicate(QObject):
	new_message = pyqtSignal()
	# new_audio = pyqtSignal()
	# new_content = pyqtSignal()
	# enable_button = pyqtSignal()
	# show_message = pyqtSignal()


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
		self.SET_LADDR = 's_laddr'
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

		self.signal = Communicate()
		self.signal.new_message.connect(self.new_message)
		self.recipient_address = self.GLOBAL


		self.dialog_layout = self.set_layout_with_scroll_area(self.ui.verticalLayout, self.ui.scrollArea)
		self.find_server()
		self.log_in()

	def set_layout_with_scroll_area(self, ui_layout, ui_scroll_area):
		layout = ui_layout
		Widget = Qt.QWidget()
		Widget.setLayout(layout)
		scroll_area = ui_scroll_area
		scroll_area.setWidget(Widget)
		return layout


	def add_button_into_layout(self, name, layout, button_dict, info, action, set_style=False):
		button = Qt.QPushButton(f'{name}')
		if set_style:
			button.setStyleSheet(f'background : {self.BASE_COLOR};')

		layout.addWidget(button)
		button_dict[button] = info
		button.clicked.connect(action)

		return button


	def dialog_button_click(self):
		sender = self.sender()
		for button, address in self.dialog_button_dict.items():
			if sender == button:
				self.recipient_address = address

				self.change_dialog_button_color(button, self.BASE_COLOR)
				self.display_all_messages_from_sender(address)
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


	def del_dialog_button(self, address):
		for but, addr in self.dialog_button_dict.items():
			if address == addr:	
				but.setParent(None)
				del_but = but
		self.dialog_button_dict.pop(del_but)				


	def if_any_connect_or_disconnect(self, mtype, sender, client_name):
		if mtype == self.CONNECT:
			self.clients.append(sender)
			self.ui.ComboBox_Of_Clients.addItem(client_name)

		elif mtype == self.DISCONNECT:
			self.ui.ComboBox_Of_Clients.removeItem(self.clients.index(sender))
			self.clients.remove(sender)
			self.del_dialog_button(sender)


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
		self.send_message_to_server(self.ACCEPT_CALL, self.recipient_address, 'accepted call', False)

		# self.audio_socket = AudioSocketClient()
		# self.audio_socket.set_host_and_port(self.host, self.port+1)
		# self.audio_socket.create_socket()
		self.audio_socket.set_audio_stream_in()
		self.audio_socket.start_sending(self.incomming_addr)
		self.audio_socket.start_receiving()


	def cancel_incomming_call(self):
		self.shutdown_incomming_call = True
		self.message_box.setParent(None)
		self.send_message_to_server(self.CANCEL_CALL, self.recipient_address, 'canceled call', False)


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

		elif data[0] == self.ACTIVE_CLIENTS:
			if len(data) != 2:
				for i in range(1,len(data),2):
					self.ui.ComboBox_Of_Clients.addItem(data[i])
					self.clients.append(data[i+1])
			return True

		return False


	def check_call_message(self, data):
		if data[0] == self.INCOMMING_CALL:
			self.incomming_addr = data[4][-7:-2]
			self.shutdown_incomming_call = False
			Thread_in_call = threading.Thread(target=self.thread_incomming_call, daemon = True)
			Thread_in_call.start()
			self.show_context_menu(data[3])
			return True

		elif data[0] == self.ACCEPT_CALL:
			self.incomming_addr = data[4][-7:-2]

			# self.audio_socket = AudioSocketClient()
			# self.audio_socket.set_host_and_port(self.host, self.port+1)
			# self.audio_socket.create_socket()
			self.audio_socket.set_audio_stream_in()
			self.audio_socket.start_sending(self.incomming_addr)
			self.audio_socket.start_receiving()
			return True

		elif data[0] == self.CANCEL_CALL:
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
		try:
			self.host = self.ui.Edit_IP.text()
			self.port = int(self.ui.Edit_Port.text())

			self.TCP_socket.set_host_and_port(self.host, self.port)
			self.TCP_socket.set_client_name(self.ui.Edit_Name.text())
			self.TCP_socket.connect()

			self.audio_socket = AudioSocketClient()
			self.audio_socket.set_host_and_port(self.host, self.port+1)
			self.audio_socket.create_socket()
			laddr = str(self.audio_socket.get_laddr())
			# self.audio_socket.start_sending('00000')
			self.send_message_to_server(self.SET_LADDR, self.GLOBAL, laddr, False)

			self.add_dialog_button_if_no_such(self.GLOBAL, self.GLOBAL)

			self.ui.Btn_Log_In.setDisabled(True)
			self.ui.Btn_Log_Out.setDisabled(False)
			self.ui.Btn_Send_Message.setDisabled(False)
			self.ui.Btn_History_Request.setDisabled(False)
		except:
			pass
		self.script_for_mas_os()


	def prepare_and_send_message(self):	
		message = self.ui.TEdit_Input_Message.toPlainText()

		if message:
			self.send_message_to_server(self.MESSAGE, self.recipient_address, message, True)


	def send_message_to_server(self, mtype, recipient, message, print_message):#, content='†'):
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


	# def enable_button(self):
	# 	self.ui.Btn_Send_Message.setDisabled(False)


	# def upload_file_thread(self, name, file_path):
	# 	if file_path:
	# 		file_basename = self.get_basename(file_path)
	# 		response = self.HTTP_client.upload_file(file_path)
	# 		if self.check_errors_in_response(response):

	# 			self.content_info = [file_basename, self.upload_file_layout, \
	# 												self.upload_files_button_dict, response[2], self.delete_upload_file]
	# 			self.signal.new_content.emit()

	# 			self.upload_file_list.append([response[2], file_basename])

	# 	self.signal.enable_button.emit()


	def call_recipient_button_click(self):
		
		if self.recipient_address != self.GLOBAL:
			self.send_message_to_server(self.INCOMMING_CALL, self.recipient_address, 'incomming call', False)


	def mute_mic_button_click(self):
		# self.audio_socket = AudioSocketClient()
		# self.audio_socket.set_audio_stream_in()
		# self.audio_socket.set_host_and_port(self.host, self.port+1)
		# self.audio_socket.create_socket()
		# self.audio_socket.start_sending('00000')
		# self.audio_socket.start_receiving()
		pass
		# audio = AudioSocketClient()
		# audio.set_host_and_port('192.168.100.2', 50008)
		# audio.create_socket()
		# audio.start_sending('00000')
		# self.audio_socket.start_sending('00000')


	def change_active_dialog(self):
		name = self.ui.ComboBox_Of_Clients.currentText()
		address = self.clients[self.ui.ComboBox_Of_Clients.currentIndex()]

		button = self.add_dialog_button_if_no_such(address, name)
		button.click()


	def set_TCP_socket(self, socket):
		self.TCP_socket = socket


	def set_audio_socket(self, audio_socket):
		pass
		# self.audio_socket = AudioSocketClient()


	def script_for_mas_os(self):
		self.hide()
		self.show()


	def closeEvent(self, event): 
		self.close_connection()


if __name__ == "__main__":
	import sys
	import socket as ss
	import threading
	import time
	from UDPConnection import UDPConnection
	from TCPConnection import TCPConnection
	from AudioClient import AudioSocketClient
	from time import gmtime, strftime
	from playsound import playsound


	app = QtWidgets.QApplication(sys.argv)
	application = MainWindow()
	application.show()

	TCP_socket = TCPConnection(application.signal.new_message)
	application.set_TCP_socket(TCP_socket)

	audio_socket = AudioSocketClient()
	application.set_audio_socket(audio_socket)

	application.ui.Btn_Find_Server.clicked.connect(application.find_server)
	application.ui.Btn_Log_In.clicked.connect(application.log_in)
	application.ui.Btn_Send_Message.clicked.connect(application.prepare_and_send_message)
	application.ui.Btn_Log_Out.clicked.connect(application.log_out)
	application.ui.Btn_History_Request.clicked.connect(application.history_request)
	application.ui.Btn_Call.clicked.connect(application.call_recipient_button_click)
	application.ui.Btn_Mute_Mic.clicked.connect(application.mute_mic_button_click)
	application.ui.ComboBox_Of_Clients.currentIndexChanged.connect(application.change_active_dialog)


	sys.exit(app.exec_())
	