#!/usr/bin/env python3
from flask import Flask
import threading
import os
from time import sleep
from rgbmatrix import graphics
import matrix_tools
import weather

app = Flask(__name__)
m = matrix_tools.getMatrix()
font0713 = graphics.Font()
font0713.LoadFont('/home/mxs/rpi-rgb-led-matrix/fonts/7x13.bdf')
cyan = graphics.Color(0, 200, 200)
modes = []

@app.route('/weather')
def weather_go():
	global weather_display
	if not 'weather' in modes:
		weather_display = threading.Thread(target=weather.display)
		m.Clear()
		weather.load()
		weather.init()
		modes.append('weather')
		weather_display.start()
		return "Displaying weather information."
	else:
		return "Must stop current weather display before starting new one."

@app.route('/esc')
def ESC():
	if 'weather' in modes:
		weather.ESC = True
		weather_display.join()
		modes.remove('weather')
	home_screen()
	return "Stopped all modes."

@app.route('/shutdown')
def SHUTDOWN():
	ESC()
	sleep(1)
	m.Clear()
	graphics.DrawText(m, weather.font0507, 1, 19, weather.softWhite, "Shutdown...")
	sleep(1.5)
	os.system('sudo shutdown -h now')

def home_screen():
	m.Clear()
	graphics.DrawText(m, font0713, 8, 14, weather.softWhite, "RMatrix")
	graphics.DrawText(m, weather.font0507, 5, 26, cyan, "Select mode")

if __name__ == '__main__':
	home_screen()
	app.run(debug=True, host='0.0.0.0', use_reloader=False)


