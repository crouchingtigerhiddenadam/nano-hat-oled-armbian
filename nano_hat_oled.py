'''
## License

The MIT License (MIT)

NanoHAT OLED for Armbian: NanoHAT OLED and GPIO Button Control for Armbian
Copyright (C)2020 CrouchingTigerHiddenAdam @tigerhiddenadam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from PIL import Image, ImageDraw, ImageFont
import os
import smbus
import subprocess
import time

SCREEN_BLANK_TIMEOUT = 30

current_time = time.time()
i2c0_bus = smbus.SMBus(0) # access to OLED
image = Image.new('1', (128, 64))
image_draw = ImageDraw.Draw(image)
image_font8 = ImageFont.truetype('DejaVuSansMono.ttf', 8)
image_font10 = ImageFont.truetype('DejaVuSansMono.ttf', 10)
image_font15 = ImageFont.truetype('DejaVuSansMono.ttf', 15)
image_font25 = ImageFont.truetype('DejaVuSansMono.ttf', 25)
key1_page_index = 1
key2_page_index = 2
key3_page_index = 3
page_index = 0
page_refresh_time = 0
screen_blank_time = current_time + SCREEN_BLANK_TIMEOUT
shutdown_time = 0

def write_i2c_image_data(i2c_bus, image):
  block_data = []
  image_data = image.load()
  page = 0
  while page < 8:
    x = 0
    while x < 128: # iterate through the x axis for 128 pixels
      bit = 7
      byte = 0
      while bit >= 0: # swap bits
        byte = byte << 1
        if image_data[x, page * 8 + bit]:
          byte = byte | 1
        bit = bit - 1
      block_data.append(byte)
      if len(block_data) == 32:
        i2c_bus.write_i2c_block_data(0x3c, 0x40, block_data)
        block_data = []
      x = x + 1
    page = page + 1

try:

  with open('/sys/class/gpio/export', 'w') as file: file.write('0\n') # initialise GPIO 0 (key1)
  with open('/sys/class/gpio/export', 'w') as file: file.write('2\n') # initialise GPIO 2 (key2)
  with open('/sys/class/gpio/export', 'w') as file: file.write('3\n') # initialise GPIO 3 (key3)
  with open('/sys/class/gpio/gpio0/direction', 'w') as file: file.write('in\n')
  with open('/sys/class/gpio/gpio2/direction', 'w') as file: file.write('in\n')
  with open('/sys/class/gpio/gpio3/direction', 'w') as file: file.write('in\n')

  i2c0_bus.write_i2c_block_data(0x3c, 0x00, [
    0xae,       # set display off 
    0x00,       # set lower column address
    0x10,       # set higher column address
    0x40,       # set display start line
    0xb0, 0x81, # set page address
    0xcf,       # set screen flip
    0xa1,       # set segment remap
    0xa8,       # set multiplex ratio
    0x3f,       # set duty 1/64
    0xc8,       # set com scan direction
    0xd3, 0x00, # set display offset
    0xd5, 0x80, # set osc division
    0xd9, 0xf1, # set pre-charge period
    0xda, 0x12, # set com pins
    0xdb, 0x40, # set vcomh
    0x8d, 0x14, # set charge pump on
    0xa6,       # set display normal (not inverse)
    0x20, 0x00, # set horizontal addressing mode
    0xaf
  ])

  while True:
    current_time = time.time()
    with open('/sys/class/gpio/gpio0/value') as file: # poll key1 down
      if file.read(1) == '1':
        page_index = key1_page_index
        page_refresh_time = 0
        screen_blank_time = current_time + SCREEN_BLANK_TIMEOUT
        continue
    with open('/sys/class/gpio/gpio2/value') as file: # poll key2 down
      if file.read(1) == '1':
        page_index = key2_page_index
        page_refresh_time = 0
        screen_blank_time = current_time + SCREEN_BLANK_TIMEOUT
        continue
    with open('/sys/class/gpio/gpio3/value') as file: # poll key3 down
      if file.read(1) == '1':
        page_index = key3_page_index
        page_refresh_time = 0
        screen_blank_time = current_time + SCREEN_BLANK_TIMEOUT
        continue
    if current_time > screen_blank_time:
      i2c0_bus.write_i2c_block_data(0x3c, 0x00, [0xae]) # set display off
      continue
    elif current_time > page_refresh_time:
      i2c0_bus.write_i2c_block_data(0x3c, 0x00, [0xaf]) # set display on
      if page_index == -1: # break and shutdown page_index -1
        break
      elif page_index == 0:
        splash = Image.open('splash.png')
        image.paste(splash)
        write_i2c_image_data(i2c0_bus, image)
        splash.close()
	page_index = 1 # redirect to page 1
        page_refresh_time = current_time + 5 # after 5 seconds
      elif page_index == 1:
	key1_page_index = 1
	key2_page_index = 2
	key3_page_index = 3
        text1 = time.strftime('%A')
        text2 = time.strftime('%e %b %Y')
        text3 = time.strftime('%X')
        image_draw.rectangle((0, 0, 128, 64), 0)
        image_draw.text((6,  2), text1, 1, image_font15)
        image_draw.text((6, 20), text2, 1, image_font15)
        image_draw.text((6, 36), text3, 1, image_font25)
        page_refresh_time = current_time + 1
        write_i2c_image_data(i2c0_bus, image)
      elif page_index == 2:
	key1_page_index = 1
	key2_page_index = 2
	key3_page_index = 3
        text1 = subprocess.check_output("top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'", shell = True)
        text2 = subprocess.check_output("ip a show | grep -E '^\s*inet' | grep -m1 global | awk '{print $2}' | sed 's|/.*||'", shell = True)
        text3 = subprocess.check_output("free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'", shell = True)
        text4 = subprocess.check_output("df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'", shell = True)
        text5 = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"CPU Temp %3.1fc\", $1/1000}'", shell = True)
        image_draw.rectangle((0, 0, 128, 64), 0)
        image_draw.text((6,  2), text1, 1, image_font10)
        image_draw.text((6, 14), text2, 1, image_font10)
        image_draw.text((6, 26), text3, 1, image_font10)
        image_draw.text((6, 38), text4, 1, image_font10)
        image_draw.text((6, 50), text5, 1, image_font10)
        page_refresh_time = current_time + 2
        write_i2c_image_data(i2c0_bus, image)
      elif page_index == 3:
	key1_page_index = 1
	key2_page_index = 2
	key3_page_index = 4
        image_draw.rectangle((0, 0, 128, 64), 0)
        image_draw.text((6, 2), 'Shutdown?', 1, image_font15)
        image_draw.rectangle((4, 22, 124, 34), 1)
        image_draw.text((6, 22), 'No',  0, image_font10)
        image_draw.text((6, 36), 'Yes', 1, image_font10)
        image_draw.text((6, 54), 'F3: Toggle Choices', 1, image_font8)
        page_refresh_time = current_time + 5
        write_i2c_image_data(i2c0_bus, image)
      elif page_index == 4:
	key1_page_index = -1
	key2_page_index = 4
	key3_page_index = 3
        image_draw.rectangle((0, 0, 128, 64), 0)
        image_draw.text((6, 2), 'Shutdown?', 1, image_font15)
        image_draw.rectangle((4, 36, 124, 48), 1)
        image_draw.text((6, 22), 'No',  1, image_font10)
        image_draw.text((6, 36), 'Yes', 0, image_font10)
        image_draw.text((6, 54), 'F1: Confirm Shutdown', 1, image_font8)
        page_refresh_time = current_time + 5
        write_i2c_image_data(i2c0_bus, image)
  time.sleep(.2)

except KeyboardInterrupt:
  print(' CTRL+C detected')

finally:

  i2c0_bus.write_i2c_block_data(0x3c, 0x00, [0xae]) # set display off
  with open('/sys/class/gpio/unexport', 'w') as file: file.write('0\n') # release GPIO 0 (key1)
  with open('/sys/class/gpio/unexport', 'w') as file: file.write('2\n') # release GPIO 2 (key2)
  with open('/sys/class/gpio/unexport', 'w') as file: file.write('3\n') # release GPIO 3 (key3)

  if page_index == -1: # shutdown now if the page_index was -1
    os.system('shutdown now')
  else:
    exit(0)
