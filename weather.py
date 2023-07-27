#!/usr/bin/env python3
import requests
import json
import datetime
from time import sleep
import PIL
import matrix_tools
from rgbmatrix import graphics

m = matrix_tools.getMatrix()
c = m.CreateFrameCanvas()
font0507 = graphics.Font()
font0507.LoadFont('/home/mxs/rpi-rgb-led-matrix/fonts/5x7.bdf')
font0406 = graphics.Font()
font0406.LoadFont('/home/mxs/rpi-rgb-led-matrix/fonts/4x6.bdf')
softWhite = graphics.Color(200, 200, 200)

s = '/home/mxs/RMatrix/thumbnails/'
icons = [
PIL.Image.open(s+'sunny.png'),
PIL.Image.open(s+'pcloudy.png'),
PIL.Image.open(s+'cloudy.png'),
PIL.Image.open(s+'lrain.png'),
PIL.Image.open(s+'hrain.png'),
PIL.Image.open(s+'snow.png'),
PIL.Image.open(s+'fog.png'),
PIL.Image.open(s+'stormy.png')
]
for obj in icons:
	obj.thumbnail((20,20), PIL.Image.ANTIALIAS)
	icons[icons.index(obj)] = obj.convert('RGB')

def refresh():
	print("WARNING: SENDING GET REQUEST FOR WEATHER DATA.")
	response = requests.get('https://api.open-meteo.com/v1/forecast?latitude=33.749&longitude=-84.388&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,cloudcover&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&timezone=America%2FNew_York')
	file_w = open('weather_data.json', 'w')
	json.dump(response.json(), file_w)

def load():
	global data
	file_r = open('weather_data.json', 'r')
	data = json.load(file_r)

def hourly():
	global ticker
	global days
	ticker = []
	days = []
	hourly = data['hourly']
	for time in hourly['time']:
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

def display():
	global thisday
	global c
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
	slide = 0
	nextSlide = False
	Y = 30
	infoX = 22
	infoY = 14

	while len(displaying) > 0:
		for desc in displaying:
			if desc[1]-pos == 1 and desc[0]%2 == 0:
				if displaying.index(desc) > 1:
					remove = displaying[0]
				desc[1] += 1
				stuck = desc
			else:
				length = graphics.DrawText(c, font0507, desc[1]-pos, Y, colors[desc[0]%2], ticker[desc[0]])
				desc[2] = length
			if displaying.index(desc) == len(displaying)-1 and desc[1]+length-pos < 64:
				displaying.append([desc[0]+1, desc[1] + length, 0])
				if ticker[desc[0]+1] == '12AM: ':
					thisday += 1
			if length + desc[1] < pos:
				remove = desc
		if stuck != None:
			matrix_tools.fillRect(c, 0, 23, stuck[2]-4, 7, blank)
			graphics.DrawText(c, font0507, 1, Y, colors[0], ticker[stuck[0]])
			stuck = None
		if remove != None:
			displaying.remove(remove)
			remove = None
		pos += 1

		graphics.DrawLine(c, 0, 22, 64, 22, softWhite)
		graphics.DrawText(c, font0507, 49, 7, softWhite, days[thisday])
		if slide == 0:
			graphics.DrawText(c, font0406, infoX, infoY, softWhite, "Information")
		elif slide == 1:
			graphics.DrawText(c, font0406, infoX, infoY, softWhite, "Fiddles")
		if datetime.datetime.now().second%5 == 0:
			if not nextSlide:
				nextSlide = True
				if slide < 1:
					slide += 1
				else:
					slide = 0
		else:
			nextSlide = False

		c.SetImage(icons[round(datetime.datetime.now().second/8)], 1,1)

		c = m.SwapOnVSync(c)
		sleep(0.05)
		m.Clear()

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
	display()
