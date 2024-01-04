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
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_axis_range import LiveAxisRange

class main_window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = uic.loadUi('gui3_rt_plot.ui', self) # load user interface

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
		self.serial_data_in_queue = queue.Queue() 
		self.thread_killer = threading.Event() # event to kill all threads 

		# counters lcd
		self.counter1 = 0
		self.counter2 = 0
		self.counter3 = 0 

		# buttons
		self.pushButton1.clicked.connect(lambda: self.on_click(1))
		self.pushButton2.clicked.connect(lambda: self.on_click(2))
		self.pushButton3.clicked.connect(lambda: self.on_click(3))  

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
			# DATA FROM SERIAL
			try:
				self.serial_data_in_queue.put(arduino.readline().decode("utf-8"))
			except Exception as e:
				print(e)
				pass
		try:
			arduino.close()
		except Exception as e:
			print(e)
			pass
		print("[closed_serial_port_handler]")

	# Update gui thread
	def update_gui(self):
		x = 0
		while not self.thread_killer.is_set():
			if not self.serial_data_in_queue.empty():
				try: 
					value = self.serial_data_in_queue.get_nowait()
					x+=1
					self.conn_plot1.cb_append_data_point(float(value[0]),x)
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

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = main_window() 
	w.show()
	sys.exit(app.exec_())
