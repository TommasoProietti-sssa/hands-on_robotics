import socket
import random
import time
import json


def send_random_numbers():
	# Create a TCP socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind the socket to localhost and a specific port
	server_address = ('localhost', 1234)
	server_socket.bind(server_address)

	# Listen for incoming connections
	server_socket.listen(1)

	print('Server is listening on {}:{}'.format(*server_address))

	while True:
		# Accept a client connection
		client_socket, client_address = server_socket.accept()
		print('Accepted connection from {}:{}'.format(*client_address))

		# Send random numbers at 200Hz frequency
		while True:
			random_int = random.randint(0, 10)
			random_float1 = random.uniform(0, 5.0)

			data = {
				'random_int': random_int,
				'random_float1': random_float1,
			}

			# Convert the dictionary to a JSON string
			json_data = json.dumps(data)

			# Send the JSON data to the client
			client_socket.sendall(json_data.encode())

			# Wait for 5 milliseconds (200Hz frequency)
			time.sleep(0.005)

		# Close the client connection
		client_socket.close()

if __name__ == '__main__':
	send_random_numbers()
