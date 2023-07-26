#!/usr/bin/env python3
import requests
import json
import datetime
from time import sleep
import threading
import matrix_tools
from rgbmatrix import graphics

m = matrix_tools.getMatrix()
font0507 = graphics.Font()
font0507.LoadFont('/home/mxs/rpi-rgb-led-matrix/fonts/5x7.bdf')
font0406 = graphics.Font()
font0406.LoadFont('/home/mxs/rpi-rgb-led-matrix/fonts/4x6.bdf')
softWhite = graphics.Color(200, 200, 200)

#There are two methods to handle data: refresh and load. Refresh retrieves data from Open-Meteo API, so it will be used infrequently and only by user command. Refresh stores the data to a JSON file. Load retrieves the data and stores it as a dictionary in the variable data.
def refresh():
	print("WARNING: SENDING GET REQUEST FOR WEATHER DATA.")
	response = requests.get('https://api.open-meteo.com/v1/forecast?latitude=33.749&longitude=-84.388&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,cloudcover&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&timezone=America%2FNew_York')
	file_w = open('weather_data.json', 'w')
	json.dump(response.json(), file_w)

def load():
	global data
	file_r = open('weather_data.json', 'r')
	data = json.load(file_r)

#hourly method generates a list of strings to be played when hourly data is displayed.
#The ticker is primarily based on timestamps. Timestamps are gathered from the data and converted into prettier forms.
#An assortment of hourly data points is available. The desired data is collected and joined with a unit, a label, and ultimately the timestamp that corresponds to it.
#The final ticker strings are stored in a list. Timestamps are displayed in different colors from their corresponding data.
def hourly():
	global ticker
	global days
	ticker = []
	days = []
	hourly = data['hourly']
	for time in hourly['time']:
		#Creating timestamp for ticker
		hr = int(time[11:13])
		if hr > 12:
			hr = str(hr-12) + "PM: "
		elif hr == 0:
			day = datetime.date(int(time[0:4]), int(time[5:7]), int(time[8:10])).weekday()
			if day == 0:
				day = "MON"
			elif day == 1:
				day = "TUE"
			elif day == 2:
				day = "WED"
			elif day == 3:
				day = "THU"
			elif day == 4:
				day = "FRI"
			elif day == 5:
				day = "SAT"
			elif day == 6:
				day = "SUN"
			days.append(day)
			hr = "12AM: "
		elif hr == 12:
			hr = str(hr) + "PM: "
		else:
			hr = str(hr) + "AM: "

		#Creating data list
		item = hourly['time'].index(time)
		info = ""
		for point in hourly:
			if point == 'time':
				ticker.append(hr)
			elif point == 'temperature_2m':
				info += "Temp: " + str(hourly[point][item]) + "F, "
			elif point == 'relativehumidity_2m':
				info += "RH: " + str(hourly[point][item]) + "%, "
			elif point == 'precipitation_probability':
				info += "PP: " + str(hourly[point][item]) + "%, "
			elif point == 'cloudcover':
				info += "Cover: " + str(hourly[point][item]) + "% "
		ticker.append(info)

#stickScroll displays a list of strings on the matrix by scrolling them with alternating colors. The headers will stick to the side until replaced.
def stickScroll():
	global thisday
	global draw
	draw = False
	color1 = matrix_tools.randVisColor(100)
	color2 = matrix_tools.randVisColor(100)
	colors = [graphics.Color(color1[0], color1[1], color1[2]), graphics.Color(color2[0], color2[1], color2[2])]
	displaying = []
	displaying.append([0,0,0])
	pos = -64
	remove = None
	stuck = None
	thisday = 0
	blank = graphics.Color(0,0,0)
	Y = 30

	#Displaying strings and managing which are displayed.
	while len(displaying) > 0:
		for desc in displaying:
			if desc[1]-pos == 1 and desc[0]%2 == 0:
				if displaying.index(desc) > 1:
					remove = displaying[0]
				desc[1] += 1
				stuck = desc
			else:
				length = graphics.DrawText(m, font0507, desc[1]-pos, Y, colors[desc[0]%2], ticker[desc[0]])
				desc[2] = length
			if displaying.index(desc) == len(displaying)-1 and desc[1]+length-pos < 64:
				displaying.append([desc[0]+1, desc[1] + length, 0])
				if ticker[desc[0]+1] == '12AM: ':
					thisday += 1
			if length + desc[1] < pos:
				remove = desc
		if stuck != None:
			matrix_tools.fillRect(m, 0, 23, stuck[2]-4, 7, blank)
			graphics.DrawText(m, font0507, 1, Y, colors[0], ticker[stuck[0]])
			stuck = None
		graphics.DrawLine(m, 0, 22, 64, 22, softWhite)
		draw = True
		sleep(0.05) #Keep over the daily method draw checking period
		pos += 1
		m.Clear()
		draw = False
		if not remove == None:
			displaying.remove(remove)
			remove = None

#daily displays the daily weather information at the top of the matrix. It cycles through messages.
def daily():
	slide = 0
	while True:
		while not draw:
			sleep(0.02)
		graphics.DrawText(m, font0507, 49, 7, softWhite, days[thisday])
		if slide == 0:
			graphics.DrawText(m, font0406, 20, 15, softWhite, "Information")
		elif slide == 1:
			graphics.DrawText(m, font0406, 20, 15, softWhite, "Fiddles")
		if datetime.datetime.now().second%5 == 0:
			if slide < 1:
				slide += 1
			else:
				slide = 0

if __name__ == '__main__':
	print("Welcome to Max Scholle's Weather Display.")
	print("Using work from hzeller on Github and using weather data from OpenMeteo.\n")
	update = input("Would you like to update the weather data now? y/n ")
	if update == 'y':
		refresh()
	print("\nLoading and interpreting data...")
	load()
	hourly()
	print("Displaying the weather...")
	scroll = threading.Thread(target=stickScroll)
	top = threading.Thread(target=daily)
	scroll.start()
	top.start()
