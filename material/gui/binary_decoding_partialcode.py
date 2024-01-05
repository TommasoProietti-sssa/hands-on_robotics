
# BINARY SERIAL COMMUNICATION
DATA_NUMBER = 4  # number of elements in string passed by arduino
VAR_NAMES = "time,var1,var2,var3" # variable names for csv file
DATA_PACKET_FORMAT_STRING = '<Lfi?' # serial communication format: '<' little endian, 'L' unsigned long, 'f' float, 'i' int, '?' bool
DATA_PACKET_SIZE = 13 # size of the packet in bytes (4bytes = float, int, unsigned long. 1 byte = bool)
SERIAL_HEADER = b'\x21' # '!'
SERIAL_FOOTER = b'\x40' # '@'
class ParsingState(enum.IntEnum): # state machine for parsing packets
	HEADER = 0
	FOOTER = 2
	DATA = 1

class main_window(QMainWindow):

	# here all the gui stuff

	def serial_port_handler(self):
		arduino = serial.Serial(self.port, baudrate=SERIAL_BAUDRATE, timeout=.1) # Opening serial communication
		
		packet_parser_state = ParsingState.HEADER # state machine for parsing packets
		serial_buffer = b'' # initialize serial buffer
		packet_parser_counter = 0
		packet_parser_buffer = b''

		while not self.thread_killer.is_set():
			# DATA FROM SERIAL
			try:
				serial_buffer = arduino.read(1) # read 1 byte per time
				# state machine for parsing packets --> HEADER -> DATA -> FOOTER -> HEADER -> ...
				if packet_parser_state == ParsingState.HEADER: 
					if serial_buffer == SERIAL_HEADER:
						packet_parser_state = ParsingState.DATA
						packet_parser_counter = 0
						packet_parser_buffer = b''
						continue
					else: # skip this byte, not the header
						continue
				elif packet_parser_state == ParsingState.DATA:
					packet_parser_buffer += serial_buffer
					packet_parser_counter += 1
					if packet_parser_counter == DATA_PACKET_SIZE:
						packet_parser_state = ParsingState.FOOTER
						continue
					else: # skip this byte, not yet the footer
						continue
				elif packet_parser_state == ParsingState.FOOTER:
					packet_parser_state = ParsingState.HEADER
					if serial_buffer == SERIAL_FOOTER:
						try:
							values = list(struct.unpack(DATA_PACKET_FORMAT_STRING, packet_parser_buffer)) # unpack data to list "values"
						except Exception as e:
							print('--> Error parsing packet')
							print(e)
					else:
						print("--> Corrupted packet: ", serial_buffer)
						continue # skip this packet (it's corrupted)
				
				self.serial_data_in_queue.put(values) # put data in queue to distribute to other threads
			except Exception as e:
				print(e)
				pass
		try:
			arduino.close()
		except Exception as e:
			print(e)
			pass
		print("[closed_serial_port_handler]")

	