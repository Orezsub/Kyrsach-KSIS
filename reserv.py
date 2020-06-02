import socket
import time
import cv2
import numpy as np
import sys
import math

TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
TCP_socket.bind(("192.168.0.101", 50007))
TCP_socket.listen(10)

BUF = 8192*2

connection, address = TCP_socket.accept()

shutdown = False
is_image = False

img = ''.encode()
first_mes = True
only_part_of_len = False

while not shutdown:
	# try:
	print("cicle")
	first = True
	readed_len = -1
	message_len = BUF
	dif = -1

	package = 0
	package_count = -1

	while not shutdown:
		if is_image and package > package_count:
			nparr = np.frombuffer(img, np.uint8)
			frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
			# cv2.imshow('Live Feed', frame)
			cv2.imwrite('messigray.png',frame)
			# if cv2.waitKey(1) & 0xFF == ord('q'):
			# 	break

		data = connection.recv(BUF)#.decode("utf-8")
		print(data[:10], 'end')
		if not data:
				shutdown = True
				break

		if package <= package_count:
			# print("package")

			pass
			# if readed_len + BUF > message_len:
			# 	dif = message_len - readed_len
			# 	# print(data)
			# 	frame_img = img + data[:dif]
			# 	data = data[:dif]
			# 	# print(data)
			# 	print(message_len)
			# 	print(readed_len)
			# 	print((readed_len % BUF) - dif)
			# 	readed_len += dif
			# 	img = ''.encode()
			# 	first = True
			# 	# only_part_of_len = True
			# 	continue
				
			# else:
			# 	readed_len += BUF

			# # print(data)
			# if first:
				# print(data)
				# if only_part_of_len:
				# 	print(data)
				# 	shutdown = True
				# # 	break
				# if not first_mes:
				# 	pass
					# if only_part_of_len:
					# 	message_len = int(part_of_len + data[: 6 - len(part_of_len)])
					# 	data = data[6 - len(part_of_len) :]
					# 	only_part_of_len = False
					# 	# first = False

					# if BUF - dif < 6:
					# 	part_of_len = data[BUF-dif:]
					# 	only_part_of_len = True
					# else:
					# 	message_len = int(data[BUF-dif : BUF-dif+6])
					# 	data = data[BUF-dif+6:]
					# 	# first = False

				# else:
				
				# readed_len = BUF - 6
				# data = data[6:]
				# first_mes = False

				# if not only_part_of_len:
				# first = False

			# 	break
		else:

			print(data[:6])
			message_len = int(data[:6])
			package_count = math.ceil(message_len // BUF)
			package = 0
			print(package_count)
			data = data[6:]
			img = ''.encode()

			is_image = True


		package += 1
		img += data



	# nparr = np.fromBUFfer(frame_img, np.uint8)
	# frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	# cv2.imshow('Live Feed', frame)
	# cv2.waitKey(100)
	# break

	# except:
		# shutdown = True
# print(sys.getsizeof(img))

# cv2.waitKey(100)
# print(sys.getsizeof(frame))
# nparr = np.fromstring(img, np.uint8)
# imgg = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
# print(imgg)
# cv2.imshow('frame', imgg)

# print(img)
print('close')
time.sleep(5)