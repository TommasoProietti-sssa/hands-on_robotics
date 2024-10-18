import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5 import uic
import re
import threading
from threading import Thread
import queue
import time
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_axis_range import LiveAxisRange
import datetime
import socket
import json


class main_window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = uic.loadUi('gui4_data_saving.ui', self) # load user interface

		# threading variables
		self.tcp_data_in_queue = queue.Queue() 
		self.thread_killer = threading.Event() # event to kill all threads 
		self.tcp_data_in_queue_to_writer = queue.Queue() # queue for data to write on file
		self.flag_save_data = threading.Event() # start/stop saving data

		# counters lcd
		self.counter1 = 0
		self.counter2 = 0
		self.counter3 = 0 

		# buttons
		self.connect_button.clicked.connect(self.connectToPort) 
		self.pushButton1.clicked.connect(lambda: self.on_click(1))
		self.pushButton2.clicked.connect(lambda: self.on_click(2))
		self.pushButton3.clicked.connect(lambda: self.on_click(3))
		self.save_data_button.clicked.connect(self.save_data) 

		# plot 
		self.ui.plot_widget.setBackground('w')
		self.ui.plot_widget.setLabel('left', 'Amplitude (-)')
		self.ui.plot_widget.showGrid(x=False, y=True)
		self.ui.plot_widget.y_range_controller = LiveAxisRange(fixed_range=[0, 10])
		# self.ui.plot_widget.addLegend()
		self.plot1_liveline = LiveLinePlot(pen="blue", name="Value1") # name is used in legend
		self.ui.plot_widget.addItem(self.plot1_liveline)
		self.conn_plot1 = DataConnector(self.plot1_liveline, max_points=500, plot_rate=200, ignore_auto_range=False)

	# Button click event
	def on_click(self, button):
		if button == 1:
			print('Button 1 clicked')
			self.counter1 += 1
			self.lcdNumber1.display(self.counter1)
		elif button == 2:
			print('Button 2 clicked')
			self.counter2 += 1
			self.lcdNumber2.display(self.counter2)
		elif button == 3:
			print('Button 3 clicked')
			self.counter3 += 1
			self.lcdNumber3.display(self.counter3)

	# Connect to COM port
	def connectToPort(self):
		Thread(target=self.tcp_port_handler, args=()).start()
		time.sleep(0.1) # wait for tcp port to open
		Thread(target=self.update_gui, args=()).start()
		Thread(target=self.data_writer, args=()).start()
		self.connect_button.setEnabled(False) # Disable button

	# TCP port handler thread
	def tcp_port_handler(self):
		arduino = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP socket
		arduino.connect(('localhost', 1234)) # Connect to the TCP server
		while not self.thread_killer.is_set():
			# DATA FROM tcp
			try:
				data = arduino.recv(1024) # Read data from the TCP server
				values = json.loads(data) # Convert the JSON string to a dictionary
				self.tcp_data_in_queue.put(values)
				if self.flag_save_data.is_set(): # if saving data, put data in writer queue
					self.tcp_data_in_queue_to_writer.put(values) 
			except Exception as e:
				print(e)
				pass
		try:
			arduino.close()
		except Exception as e:
			print(e)
			pass
		print("[closed_tcp_port_handler]")

	# Update gui thread
	def update_gui(self):
		x = 0
		while not self.thread_killer.is_set():
			if not self.tcp_data_in_queue.empty():
				try: 
					values = self.tcp_data_in_queue.get_nowait()
					x+=1
					self.conn_plot1.cb_append_data_point(float(values['random_float']),x)
				except Exception as e:
					print(e)
					pass
			time.sleep(0.001) # needed to avoid freezing of gui
		print("[closed_data_plotter]")

	# Close event (when clicking on the X)
	def closeEvent(self,event):
		self.thread_killer.set() # kill all threads
		self.close()
		print('[closed_gui]')
		
	# Click on save data button (start/stop saving data)
	def save_data(self):
		if not self.flag_save_data.is_set():
			filename_words = len(re.findall(r'\w+', self.filename_edit.text()))
			if filename_words == 0:
				self.filename_edit.setText("default filename")
			self.filename_edit.setStyleSheet('border: 1px solid green')
			self.flag_save_data.set()
		else:
			self.filename_edit.setText("")
			self.filename_edit.setStyleSheet('')
			self.flag_save_data.clear()
	
	# Data writer thread
	def data_writer(self):
		while not self.thread_killer.is_set():
			if self.flag_save_data.is_set():
				# Input string from filename_edit
				input_name = self.filename_edit.text()
				input_name = input_name.replace(' ','_')
				# Date
				year = str(datetime.datetime.now().year)
				month = str(datetime.datetime.now().month)
				day = str(datetime.datetime.now().day)
				hour = str(datetime.datetime.now().hour)
				minute = str(datetime.datetime.now().minute)
				second = str(datetime.datetime.now().second)
				# Final filename
				filename = year + month + day + '_' + hour + minute + second + '_' + input_name + '.csv'
				print(filename)
				# Opening new file
				output_file = open(filename,'w')
				time.sleep(0.1)  # waiting for the file to be opened
				while self.flag_save_data.is_set():
					if not self.tcp_data_in_queue_to_writer.empty():
						try:
							values = self.tcp_data_in_queue_to_writer.get_nowait()  
							output_file.write(str(values['random_int']) + "," + str(values['random_float']) + "\n")
						except Exception as e:
							print(e)
							pass
					time.sleep(0.001) # needed of gui
				output_file.close()
				print(filename)
			time.sleep(0.001) # needed of gui
		print("[closed_data_writer]")

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = main_window() 
	w.show()
	sys.exit(app.exec_())
