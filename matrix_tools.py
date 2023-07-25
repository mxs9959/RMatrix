#!/usr/bin/env python3
import random
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

options = RGBMatrixOptions()
options.hardware_mapping = 'adafruit-hat-pwm'
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.row_address_type = 0
options.multiplexing = 0
options.pwm_bits = 11
options.brightness = 100
options.pwm_lsb_nanoseconds = 130
options.led_rgb_sequence = 'RGB'
options.pixel_mapper_config = ''
options.panel_type = ''
options.show_refresh_rate = 0
options.gpio_slowdown = 4
options.disable_hardware_pulsing = False
options.drop_privileges=False

matrix = RGBMatrix(options = options)

def getMatrix():
	return matrix

def fillRect(m, x, y, w, h, color):
	for X in range(w-x):
		graphics.DrawLine(m, X, y, X, y+h, color)

def randVisColor(thres):
	r = 0
	g = 0
	b = 0
	while r < thres:
		r = random.randint(0,255)
	while g < thres:
		g = random.randint(0,255)
	while b < thres:
		b = random.randint(0,255)
	return (r,g,b)
