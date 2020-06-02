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
		self.AUDIO = 'audio'
		# self.NEW_CONTENT = 'new_content'
		# self.DEL_CONTENT = 'del_content'
		self.ARROW = '-->'
		self.HISTORY = 'history'
		self.HISTORY_START = 'history_start'
		self.HISTORY_END = 'history_end'
		self.HISTORY_REQUEST = 'history_request'
		self.ACTIVE_CLIENTS = 'active_clients'
		# self.LOADED_CONTENT = 'loaded_content'
		# self.UPLOAD_FILE = 'upload_file'

		self.BASE_COLOR = '#F0F0F0'
		self.RED_COLOR = '#DB4747'

		self.clients = [self.GLOBAL]
		self.dialog_button_dict = {}
		# self.upload_files_button_dict = {}
		# self.download_files_button_dict = {}
		self.message_list = []
		# self.upload_file_list = []
		# self.download_file_list = []
		# self.content_info = []
		# self.sender_info = ''
		
		self.signal = Communicate()
		self.signal.new_message.connect(self.new_message)
		# self.signal.new_audio.connect(self.new_audio)
		# self.signal.new_content.connect(self.new_content_signal)
		# self.signal.enable_button.connect(self.enable_button)
		# self.signal.show_message.connect(self.show_message)
		self.recipient_address = self.GLOBAL


		self.dialog_layout = self.set_layout_with_scroll_area(self.ui.verticalLayout, self.ui.scrollArea)
		# self.upload_file_layout = self.set_layout_with_scroll_area(self.ui.horizontalLayout, self.ui.scrollArea_2)
		# self.download_file_layout = self.set_layout_with_scroll_area(self.ui.verticalLayout_2, self.ui.scrollArea_3)
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
				# self.display_all_files_from_sender(address)
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

		# button = Qt.QPushButton('Info')
		# button.clicked.connect(self.show_file_info)
		# message_box.addButton(button, QtWidgets.QMessageBox.ActionRole)

		self.message_box.exec_()

	def accept_incomming_call(self):
		print('send')
		self.shutdown_incomming_call = True
		self.message_box.setParent(None)
		self.send_message_to_server(self.ACCEPT_CALL, self.recipient_address, 'accepted call', False)
		
		self.audio_socket.start_sending(self.incomming_addr)
		self.audio_socket.start_receiving()
		# p = pyaudio.PyAudio()
		# CHUNK = 1024
		# CHANNELS = 1
		# RATE = 22100
		# WIDTH = 2
		# self.recv_audio_stream = p.open(format=p.get_format_from_width(WIDTH), channels=CHANNELS, rate=RATE,\
		# 					 output=True, frames_per_buffer=CHUNK)
		# print('send')
	# sender = self.sender_info
	# for button, file_id in self.download_files_button_dict.items():
	# 	if sender == button:

	# 		for download_file_info in self.download_file_list:
	# 			if download_file_info[2] == file_id:
	# 				file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', f'/home/{download_file_info[3]}')[0]

	# 				if file_path:
	# 					response = self.HTTP_client.download_file(file_id, file_path)
	# 					self.check_errors_in_response(response)
	# 					break


	# def show_message(self):
	# 	self.show_message_box(self.content_info[0])


	# def show_message_box(self, info):
	# 	message_box = QtWidgets.QMessageBox.information(self, 'title', info)


	def cancel_incomming_call(self):
		self.shutdown_incomming_call = True
		self.message_box.setParent(None)
		self.send_message_to_server(self.CANCEL_CALL, self.recipient_address, 'canceled call', False)
		# sender = self.sender_info
		# for button, file_id in self.download_files_button_dict.items():
		# 	if sender == button:	
		# 		button.setParent(None)
		# 		deleted_button = button

		# 		for download_file_info in self.download_file_list:
		# 			if download_file_info[2] == file_id:
		# 				response = self.HTTP_client.delete_download_file(file_id)

		# 				if self.check_errors_in_response(response):
		# 					content = f'†{file_id}†{download_file_info[3]}'

		# 					self.send_message_to_server(self.DEL_CONTENT, self.recipient_address, \
		# 								f'delete -> @{download_file_info[3]}', True, content)
		# 					self.download_file_list.remove(download_file_info)
		# 					break
		# 		break

	# 	self.download_files_button_dict.pop(deleted_button)


	# def if_any_content_info_in_message(self, mtype, sender, recipient, content):
	# 	if mtype == self.NEW_CONTENT:
	# 		for i in range(0, len(content), 2):
	# 			file_basename = content[i+1]
	# 			if recipient == self.recipient_address:
	# 				self.add_button_into_layout(file_basename, self.download_file_layout, \
	# 													self.download_files_button_dict, content[i], self.show_context_menu)

	# 			self.download_file_list.append([sender, recipient, content[i], content[i+1]])

	# 	elif mtype == self.DEL_CONTENT:
	# 		for i in range(0, len(content), 2):
	# 			for download_file_info in self.download_file_list:
	# 				if download_file_info[2] == content[i]:

	# 					for button, file_id in self.download_files_button_dict.items():
	# 						if file_id == content[i]:
	# 							button.setParent(None)
	# 							self.download_files_button_dict.pop(button)
	# 							break

	# 					self.download_file_list.remove(download_file_info)
	# 					break


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


	# def display_all_files_from_sender(self, recipient_address):
	# 	for button, file_id in self.download_files_button_dict.items():
	# 			button.setParent(None)
	# 	self.download_files_button_dict.clear()

	# 	if recipient_address == self.GLOBAL:
	# 		for download_file_info in self.download_file_list:

	# 			if download_file_info[1] == recipient_address:
	# 				file_basename = download_file_info[3]
	# 				self.add_button_into_layout(file_basename, self.download_file_layout, \
	# 									self.download_files_button_dict, download_file_info[2], self.show_context_menu)

	# 	else:
	# 		for download_file_info in self.download_file_list:

	# 			if download_file_info[1] == recipient_address:
	# 				file_basename = download_file_info[3]
	# 				self.add_button_into_layout(file_basename, self.download_file_layout, \
	# 									self.download_files_button_dict, download_file_info[2], self.show_context_menu)

	# 			elif download_file_info[0] == recipient_address and download_file_info[1] != self.GLOBAL:
	# 				file_basename = download_file_info[3]
	# 				self.add_button_into_layout(file_basename, self.download_file_layout, \
	# 									self.download_files_button_dict, download_file_info[2], self.show_context_menu)

	def thread_incomming_call(self):
		while not self.shutdown_incomming_call:
			try:
				while not self.shutdown_incomming_call:
					# playsound('call.mp3')

					time.sleep(1)
			except:
				self.shutdown_incomming_call = True


	# def thread_audio_sending(self, name, recipient):
	# 	print('start listen')
	# 	CHUNK = 1024
	# 	FORMAT = pyaudio.paInt16
	# 	CHANNELS = 1
	# 	RATE = 12100
	# 	while not self.shutdown_send_audio:
	# 		# try:
	# 			# while not self.shutdown_send_audio:
					
	# 		p = pyaudio.PyAudio()

	# 		stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
	# 		data  = stream.read(CHUNK)
	# 		dataChunk = array('h', data)
	# 		vol = max(dataChunk)
	# 		if(vol > 500):
	# 			# print("Recording Sound...")
	# 			# self.audio_socket.send_audio(recipient, data, len(data))
	# 			print('send audio')
	# 			self.audio_socket.sendall(data)
	# 			# s.sendall(data[:2000])
	# 			# print(len(data))
	# 		# else:
	# 			# print("Silence..")
					
	# 		# except:
	# 			# self.shutdown_send_audio = True
	# 			# stream.stop_stream()
	# 			# stream.close()
	# 			# p.terminate()
	# 	print('stop listen')


	# def new_audio(self):
	# 	print('data')
	# 	# data = self.audio_socket.get_new_message()
	# 	# self.recv_audio_stream.write(data[5:])


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

		# elif data[0] == self.LOADED_CONTENT:
		# 	if len(data) != 2:
		# 		for i in reversed(range(len(self.download_file_list))):
		# 			if self.download_file_list[i][1] == self.GLOBAL:
		# 				del self.download_file_list[i] 

		# 		for i in range(1, len(data), 4):
		# 			self.download_file_list.append([data[i], data[i+1], data[i+2], data[i+3]])
		# 		self.display_all_files_from_sender(self.GLOBAL)
		# 	return True

		return False


	def check_call_message(self, data):
		if data[0] == self.INCOMMING_CALL:
			self.incomming_addr = data[4]
			self.shutdown_incomming_call = False
			Thread_in_call = threading.Thread(target=self.thread_incomming_call, daemon = True)
			Thread_in_call.start()
			self.show_context_menu(data[3])
			return True

		elif data[0] == self.ACCEPT_CALL:
			self.incomming_addr = data[4]
			self.audio_socket.start_sending(self.incomming_addr)
			self.audio_socket.start_receiving()
			# self.shutdown_send_audio = False
			# Thread_audio_send = threading.Thread(target=self.thread_audio_sending,
			# 												args=('audio', self.recipient_address), daemon = True)
			# Thread_audio_send.start()
			return True

		elif data[0] == self.CANCEL_CALL:
			return True

		elif data[0] == self.AUDIO:
			# data = conn.recv(CHUNK)
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
				# content = data[5:]

				self.add_dialog_button_if_no_such(sender, client_name)
				self.if_any_connect_or_disconnect(mtype, sender, client_name)
				# self.if_any_content_info_in_message(mtype, sender, recipient, content)
				self.append_new_message_into_chat(sender, recipient, message)

				self.message_list.append([sender, recipient, message])
				
				time.sleep(0.2)
				self.find_dialog_button_for_change_color(sender, recipient)	
			except:
				pass

	# def new_content_signal(self):
	# 	self.add_button_into_layout(self.content_info[0], self.content_info[1], \
	# 									self.content_info[2], self.content_info[3], self.content_info[4])


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

			self.audio_socket.set_host_and_port(self.host, self.port+1)
			self.audio_socket.create_socket()
			laddr = self.audio_socket.get_laddr()
			self.send_message_to_server(self.SET_LADDR, self.GLOBAL, str(laddr), False)

			self.add_dialog_button_if_no_such(self.GLOBAL, self.GLOBAL)

			self.ui.Btn_Log_In.setDisabled(True)
			self.ui.Btn_Log_Out.setDisabled(False)
			self.ui.Btn_Send_Message.setDisabled(False)
			self.ui.Btn_History_Request.setDisabled(False)
		except:
			pass
		self.script_for_mas_os()


	# def view_upload_files(self):
	# 	for upload_file_info in self.upload_file_list:
	# 		file_basename = upload_file_info[1]
	# 		self.add_button_into_layout(file_basename, self.download_file_layout, \
	# 							self.download_files_button_dict, upload_file_info[0], self.show_context_menu)

	# 		self.download_file_list.append([self.ARROW, self.recipient_address, upload_file_info[0], upload_file_info[1]])


	# def clear_upload_file_layout(self):
	# 	for button, file_id in self.upload_files_button_dict.items():
	# 		button.setParent(None)

	# 	self.upload_file_list.clear()
	# 	self.upload_files_button_dict.clear()


	def prepare_and_send_message(self):	
		message = self.ui.TEdit_Input_Message.toPlainText()

		if message:
			self.send_message_to_server(self.MESSAGE, self.recipient_address, message, True)

		# if len(self.upload_file_list) != 0:
		# 	content_info = ''
		# 	content_name = 'upload ->'
		# 	for upload_file in self.upload_file_list:
		# 		content_info += f'†{upload_file[0]}†{upload_file[1]}'
		# 		content_name += f' @{upload_file[1]}'

		# 	self.send_message_to_server(self.NEW_CONTENT, self.recipient_address, content_name, True, content_info)

		# 	self.view_upload_files()
		# 	self.clear_upload_file_layout()
		# 	self.HTTP_client.clear_download_buffer()


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

		# for button, file_id in self.download_files_button_dict.items():
		# 	button.setParent(None)
		# self.download_files_button_dict.clear()
		# self.download_file_list.clear()
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


	def upload_file_button_click(self):
		
		if self.recipient_address != self.GLOBAL:
			self.send_message_to_server(self.INCOMMING_CALL, self.recipient_address, 'incomming call', False)

			# time.sleep(1)
			
			# host = self.ui.Edit_IP.text()
			# port = int(self.ui.Edit_Port.text())+1

			# self.audio_socket.set_host_and_port(host, 50008)
			# self.audio_socket.set_client_name(self.ui.Edit_Name.text())
			# self.audio_socket.connect('audio')
		# else:
		# 	self.shutdown_send_audio = False
		# 	Thread_audio_send = threading.Thread(target=self.thread_audio_sending,
		# 													args=('audio', self.recipient_address), daemon = True)
		# 	Thread_audio_send.start()
		# self.ui.Btn_Send_Message.setDisabled(True)
		# file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
		# threading.Thread(target=self.upload_file_thread,args=(self.UPLOAD_FILE, file_path), daemon=True).start()


	# def get_basename(self, file_path):
	# 	return path.basename(file_path)


	# def delete_upload_file(self):
	# 	sender = self.sender()
	# 	for button, file_id in self.upload_files_button_dict.items():
	# 		if sender == button:
				
	# 			response = self.HTTP_client.delete_upload_file(file_id)
	# 			if self.check_errors_in_response(response):
	# 				button.setParent(None)

	# 				self.upload_files_button_dict.pop(button)

	# 				for upload_file_info in self.upload_file_list:
	# 					if upload_file_info[0] == file_id:
	# 						self.upload_file_list.remove(upload_file_info)
	# 						break
	# 				break





	# def show_file_info(self):
	# 	sender = self.sender_info
	# 	for button, file_id in self.download_files_button_dict.items():
	# 		if sender == button:

	# 			for download_file_info in self.download_file_list:
	# 				if download_file_info[2] == file_id:

	# 					response = self.HTTP_client.get_info_about_file(file_id, download_file_info[3])
	# 					if self.check_errors_in_response(response):
	# 						self.show_message_box(response[2])


	# def check_errors_in_response(self, response):
	# 	if response[0] != 200 and response[1] != 'OK':
	# 		self.content_info = [f'ERROR {response[0]}\n{response[1]}\n{response[2]}']
	# 		self.signal.show_message.emit()
	# 		return False

	# 	return True


	def change_active_dialog(self):
		name = self.ui.ComboBox_Of_Clients.currentText()
		address = self.clients[self.ui.ComboBox_Of_Clients.currentIndex()]

		button = self.add_dialog_button_if_no_such(address, name)
		button.click()


	def set_TCP_socket(self, socket):
		self.TCP_socket = socket

	def set_audio_socket(self, audio_socket):
		self.audio_socket = audio_socket
		# self.audio_socket = ss.socket(ss.AF_INET, ss.SOCK_STREAM)
		# self.audio_socket.connect(("192.168.100.2", 50009))

	# def set_HTTP_client(self, client):
	# 	self.HTTP_client = client
	# 	self.HTTP_client.connect_to_server('',8000)
	# 	response = self.HTTP_client.initialization()
	# 	self.check_errors_in_response(response)


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
	# import HTTPClient
	from time import gmtime, strftime
	from playsound import playsound


	app = QtWidgets.QApplication(sys.argv)
	application = MainWindow()
	application.show()

	TCP_socket = TCPConnection(application.signal.new_message)
	application.set_TCP_socket(TCP_socket)

	audio_socket = AudioSocketClient()
	application.set_audio_socket(audio_socket)
	# HTTP_client = HTTPClient.HttpClient()
	# application.set_HTTP_client(HTTP_client)

	application.ui.Btn_Find_Server.clicked.connect(application.find_server)
	application.ui.Btn_Log_In.clicked.connect(application.log_in)
	application.ui.Btn_Send_Message.clicked.connect(application.prepare_and_send_message)
	application.ui.Btn_Log_Out.clicked.connect(application.log_out)
	application.ui.Btn_History_Request.clicked.connect(application.history_request)
	application.ui.Btn_Upload_File.clicked.connect(application.upload_file_button_click)
	application.ui.ComboBox_Of_Clients.currentIndexChanged.connect(application.change_active_dialog)


	sys.exit(app.exec_())
	