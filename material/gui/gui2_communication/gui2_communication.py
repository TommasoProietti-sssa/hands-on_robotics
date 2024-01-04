import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5 import uic
from serial.tools.list_ports import comports
import re
import serial
import threading
from threading import Thread
import queue
import time

class main_window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = uic.loadUi('gui2_communication.ui', self) # load user interface

		# list available COM ports and add them to the bar menu
		for port in comports():
			try:
				port_name = re.split(' - ', str(port))
				action = QAction(port_name[0], self)
				action.triggered.connect(self.connectToPort) 
				self.menu_Connect.addAction(action)
			except Exception as e:
				print(e)

		# threading variables
		self.serial_data_out_queue = queue.Queue()
		self.serial_data_in_queue = queue.Queue() 
		self.thread_killer = threading.Event() # event to kill all threads  

		# buttons
		self.pushButton1.clicked.connect(lambda: self.on_click(1))
		self.pushButton2.clicked.connect(lambda: self.on_click(2))
		self.pushButton3.clicked.connect(lambda: self.on_click(3))  

	# Button click event
	def on_click(self, button):
		if button == 1:
			print('Button 1 clicked')
		elif button == 2:
			print('Button 2 clicked')
		elif button == 3:
			print('Button 3 clicked')
		self.serial_data_out_queue.put(str(button)) # send button number to serial

	# Connect to COM port
	def connectToPort(self):
		self.port = self.sender().text() # COM port string
		Thread(target=self.serial_port_handler, args=()).start()
		time.sleep(0.1) # wait for serial port to open
		Thread(target=self.update_gui, args=()).start()
		self.menu_Connect.setTitle('Connected to '+ self.port) # Change menu title
		self.menu_Connect.setEnabled(False) # Disable menu

	# Serial port handler thread
	def serial_port_handler(self):
		arduino = serial.Serial(self.port, baudrate=9600, timeout=.1) # Opening serial communication
		while not self.thread_killer.is_set():
			# DATA TO SERIAL
			if not self.serial_data_out_queue.empty():
				try:
					arduino.write(self.serial_data_out_queue.get_nowait().encode("utf-8"))
				except Exception as e:
					print(e)
					pass
			# DATA FROM SERIAL
			try:
				data = arduino.readline().decode("utf-8") # read data from serial
				values = data.split(",") # split at commas
				values = values[:-1] # remove final '/r/n'
				if len(values) != 3: # check if data is complete
					print("Incomplete data")
					continue
				self.serial_data_in_queue.put(values)
			except Exception as e:
				print(e)
				pass
		try:
			arduino.close()
		except Exception as e:
			print(e)
			pass
		print("[closed_serial_port_handler]")

	# Update GUI thread
	def update_gui(self): 
		# loading all data from serial data queue
		while not self.thread_killer.is_set():
			if not self.serial_data_in_queue.empty():
				try:
					values = self.serial_data_in_queue.get_nowait() # get_no_wait here would kill the gui
					# update labels
					self.lcdNumber1.display(values[0])
					self.lcdNumber2.display(values[1])
					self.lcdNumber3.display(values[2])
				except Exception as e:
					print(e)
			time.sleep(0.001) # needed by gui
		print("[closed_update_gui]")

	# Close event (when clicking on the X)
	def closeEvent(self,event):
		self.thread_killer.set() # kill all threads
		self.close()
		print('[closed_gui]')

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = main_window() 
	w.show()
	sys.exit(app.exec_())
