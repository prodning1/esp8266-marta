import network,socket
import json,sys
import machine,ssd1306
import time

#station = 'OAKLAND CITY STATION'
station = 'NORTH AVE STATION'

wifi_ssid = 'raptorfizzle'
wifi_pass = 'oatmeals'

I2C_SDA_PIN = 4;
I2C_SCL_PIN = 5;

api_key = '${API_KEY}'
api_host = 'developer.itsmarta.com'
api_path = {};
api_path['RealtimeTrain'] = 'RealtimeTrain/RestServiceNextTrain/GetRealtimeArrivals?apikey=' + api_key

i2c = machine.I2C(machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

working_string = ''
open_brace_indices = []
max_len = 0

current_trains = []

oled_text = [];
def print_oled(text):
	oled_text.append(text)
	if len(oled_text) > 6:
		oled_text.pop(0)

	oled.fill(0)

	p = 0
	for text in oled_text:
		oled.text(text, 0, p)
		p += 10

	oled.show()

def oled_clear():
	oled_text = [];
	oled.fill(0)
	oled.show()

def connect_wifi():
	sta_if = network.WLAN(network.STA_IF)
	print_oled('network init\'d')
	if not sta_if.isconnected():
		sta_if.active(True)
		sta_if.connect(wifi_ssid, wifi_pass)
		print_oled('c: ' + wifi_ssid)
		while not sta_if.isconnected():
			pass
	print_oled(sta_if.ifconfig()[0])

def initialize_train_json_parse():
	global working_string
	global open_brace_indices
	global max_len

	working_string = ''
	open_brace_indices = []
	max_len = 0

def grab_and_parse_trains():
	host = api_host
	path = api_path['RealtimeTrain']
	try:
		addr = socket.getaddrinfo(host, 80)[0][-1]
		s = socket.socket()
		s.connect(addr)
		s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
		
		initialize_train_json_parse()
		while True:
			data = s.recv(100)
			if data:
				parse_train_data(str(data, 'utf8'))
			else:
				break
		s.close()
	except OSError:
		print_oled('retrying...')

def parse_train_data(data):
	global working_string
	global open_brace_indices
	global max_len

	for c in data:
#		print_oled(c)
		working_string += c

		if (c == '{'):
			open_brace_indices.append(len(working_string))
		if (c == '}'):
			matching_brace_index = open_brace_indices.pop()
			temporary_string = working_string[matching_brace_index-1:]
			try:
				parsed_json = json.loads(temporary_string);

				if parsed_json['STATION'] == station:
					print_oled(parsed_json['DESTINATION'] + ' ' + parsed_json['WAITING_TIME'])
#				print_oled(parsed_json['LINE'] +
#				'\t' + parsed_json['DESTINATION'] +
#				'\t\t' + parsed_json['WAITING_TIME'])

				working_string = ''
			except ValueError:
				print_oled('JSON exc')
				continue

		working_string_len = len(working_string)
		if (working_string_len > max_len):
			max_len = working_string_len

oled_clear()
print_oled('wifi connecting')

connect_wifi()

print_oled('connected')

while True:
	print_oled('updating trains')
	grab_and_parse_trains()
	time.sleep(15)
