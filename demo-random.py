from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

import serial
import threading
import time
from datetime import datetime
import numpy as np
import configparser
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib
matplotlib.use("Agg")
matplotlib.set_loglevel("WARNING")
import matplotlib.pyplot as plt
import random
#from gpiozero import Button, OutputDevice
from signal import pause

LabelBase.register(name= "Thai",
                   fn_regular='THSarabunNew.ttf',
                   fn_bold='THSarabunNew Bold.ttf',)

now = datetime.now()
class MainLayout(BoxLayout):
	pass

class HomeScreen(Screen):
	pass
	
class ConfigScreen(Screen):
	def save_config(self):
		app = App.get_running_app()
		app.soil_wet = int(self.ids.soil_wet_input.text)
		app.soil_dry = int(self.ids.soil_dry_input.text)
		app.rain_wet = int(self.ids.rain_wet_input.text)
		app.rain_dry = int(self.ids.rain_dry_input.text)
		
		app.config["SOIL"]["dry"] = str(app.soil_dry)
		app.config["SOIL"]["wet"] = str(app.soil_wet)
		app.config["RAIN"]["dry"] = str(app.rain_dry)
		app.config["RAIN"]["wet"] = str(app.rain_wet)
		
		with open("config.ini", "w") as f:
			app.config.write(f)
			
	def on_leave(self):
		app = App.get_running_app()
		self.ids.soil_wet_input.text = str(app.soil_wet)
		self.ids.soil_dry_input.text = str(app.soil_dry)
		self.ids.rain_wet_input.text = str(app.rain_wet)
		self.ids.rain_dry_input.text = str(app.rain_dry)
		
class DashboardScreen(Screen):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		Clock.schedule_once(self.show_dashboard)
		
	def on_enter(self):
		self.refresh_clock = Clock.schedule_interval(self.update_dashboard, 0.5)
	
	def on_leave(self):
		self.refresh_clock.cancel()
		
	def show_dashboard(self, dt):
		self.fig, self.ax = plt.subplots()
		self.data_points = 24
		self.xdata = np.arange(self.data_points)
		
		self.soil_data = np.zeros(self.data_points)
		self.rain_data = np.zeros(self.data_points)
		self.vr_data = np.zeros(self.data_points)
		
		self.line_soil, = self.ax.plot(self.xdata, self.soil_data, color="green", linewidth = 2, label = "Soil")
		self.line_rain, = self.ax.plot(self.xdata, self.rain_data, color="blue", linewidth = 2, label = "Rain")
		self.line_vr, = self.ax.plot(self.xdata, self.vr_data, color="orange", linewidth = 2, label = "Volume")
		
		self.ax.set_xlabel("Time", color='black')
		self.ax.set_ylabel("Percent (%)", color='black')
		
		self.ax.set_ylim(0, 100)
		self.ax.set_title("Dashboard Monitor", color='black', fontsize=18)
		self.ax.tick_params(axis='both', labelsize=8, colors='black')
		
		self.fig.patch.set_facecolor("none")
		self.ax.set_facecolor("#E9E9E9")

		for spine in self.ax.spines.values():
			spine.set_visible(False)

		self.ax.grid(True, linestyle='--', alpha=0.5, color='gray')
		self.ax.legend()
		
		self.plot_canvas = FigureCanvasKivyAgg(self.fig)
		self.ids.temp_dashboard.add_widget(self.plot_canvas)

	def update_dashboard(self, dt):
		app = App.get_running_app()
		
		soil = float(app.soil)
		rain = float(app.rain)
		vr = float(app.vr)
		
		# เลื่อน buffer (rolling window)
		self.soil_data = np.append(self.soil_data[1:], soil)
		self.rain_data = np.append(self.rain_data[1:], rain)
		self.vr_data   = np.append(self.vr_data[1:], vr)

		# อัปเดตเฉพาะ ydata (ไม่ต้อง plot ใหม่)
		self.line_soil.set_ydata(self.soil_data)
		self.line_rain.set_ydata(self.rain_data)
		self.line_vr.set_ydata(self.vr_data)
		self.plot_canvas.draw_idle()
	
class Demo(App):
	soil = StringProperty("0")
	rain = StringProperty("0")
	vr = StringProperty("0")
	current_time = StringProperty(now.strftime("%H:%M:%S"))
	power_status = StringProperty("ปิด")
	
	_demo_enabled = False
	_demo_clock = None
	
	soil_dry = NumericProperty(1023)
	soil_wet = NumericProperty(900)

	rain_dry = NumericProperty(1023)
	rain_wet = NumericProperty(500)
	
	def build(self):
		self.title = "ระบบฟาร์มอัจฉริยะ"
		self.load_config()
		
		Clock.schedule_interval(self.refresh_time, 1)
		threading.Thread(target = self.readSerial, daemon = True).start()
		
		#self.button = Button(17, pull_up = True, bounce_time = 0.2)
		#self.output = OutputDevice(27, initial_value = False)
		
		#self.state = False
		#self.button.when_pressed = self.toggle_power
		
		return MainLayout()

	def enable_demo_mode(self, reason: str = ""):
		if self._demo_enabled:
			return
		self._demo_enabled = True
		if reason:
			print(f"[DEMO MODE] {reason}")
		else:
			print("[DEMO MODE] Enabled")
		self._demo_clock = Clock.schedule_interval(self.update_value_demo, 1)

	def update_value_demo(self, dt):
		# Random percent values for UI demo/testing (0–100)
		self.soil = str(random.randint(0, 100))
		self.rain = str(random.randint(0, 100))
		self.vr = str(random.randint(0, 100))
	
	def toggle_power(self):
		self.state = not self.state
		self.output.value = self.state
		self.power_status = "เปิด" if self.state else "ปิด"
		
	def refresh_time(self, dt):
		self.current_time = datetime.now().strftime("%H:%M:%S")
		
	def load_config(self):
		self.config = configparser.ConfigParser()
		self.config.read("config.ini")
		
		self.soil_dry = int(self.config["SOIL"]["dry"])
		self.soil_wet = int(self.config["SOIL"]["wet"])

		self.rain_dry = int(self.config["RAIN"]["dry"])
		self.rain_wet = int(self.config["RAIN"]["wet"])
		
	def readSerial(self):
		try:
			self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)
		except Exception as e:
			Clock.schedule_once(lambda dt: self.enable_demo_mode(f"Serial not available"))
			return
		while True:
			try:
				line = self.ser.readline().decode().strip()
				if line:
					try:
						parts = line.split(";")
						self.data = {}
							
						for part in parts:
							key, value = part.split(":")
							self.data[key] = int(value)
						Clock.schedule_once(self.update_value)
					except:
						pass
			except Exception as e:
				print(e)
		
	def update_value(self, dt):
		soil_percent = np.interp(self.data.get("soil",0), [self.soil_wet,self.soil_dry], [100,0])
		soil_percent = np.clip(soil_percent, 0, 100)
		self.soil = str(int(soil_percent))
		
		rain_percent = np.interp(self.data.get("rain",0), [self.rain_wet,self.rain_dry], [100,0])
		rain_percent = np.clip(rain_percent, 0, 100)
		self.rain = str(int(rain_percent))
		
		vr_percent = np.interp(self.data.get("vr",0), [0,1023], [0,100])
		vr_percent = np.clip(vr_percent, 0, 100)
		self.vr = str(int(vr_percent))
		
if __name__ == "__main__":
	Demo().run()
