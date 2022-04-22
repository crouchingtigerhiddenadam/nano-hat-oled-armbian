#!/usr/bin/python3
"""
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
"""

from PIL import Image, ImageDraw, ImageFont
import os
import smbus
import subprocess
import time
import gpiod

DISPLAY_OFF_TIMEOUT = 30

cmd_index = 0
current_time = time.time()
display_refresh_time = 0
display_off_time = current_time + DISPLAY_OFF_TIMEOUT
i2c0_bus = smbus.SMBus(0)  # access to OLED
image = Image.new("1", (128, 64))
image_draw = ImageDraw.Draw(image)
image_font8 = ImageFont.truetype("DejaVuSansMono.ttf", 8)
image_font10 = ImageFont.truetype("DejaVuSansMono.ttf", 10)
image_font15 = ImageFont.truetype("DejaVuSansMono.ttf", 15)
image_font25 = ImageFont.truetype("DejaVuSansMono.ttf", 25)
key1_cmd_index = 1
key2_cmd_index = 2
key3_cmd_index = 3
shutdown_time = 0


def write_i2c_image_data(i2c_bus, image):
    block_data = []
    image_data = image.load()
    page = 0

    while page < 8:
        x = 0

        while x < 128:  # iterate through the x axis for 128 pixels
            bit = 7
            byte = 0

            while bit >= 0:  # swap bits
                byte = byte << 1
                if image_data[x, page * 8 + bit]:
                    byte = byte | 1
                bit = bit - 1

            block_data.append(byte)

            if len(block_data) == 32:
                i2c_bus.write_i2c_block_data(0x3C, 0x40, block_data)
                block_data = []
            x = x + 1
        page = page + 1


try:
    chip = gpiod.Chip("gpiochip1")
    offsets = [0, 2, 3]
    lines = chip.get_lines(offsets)
    lines.request("nanohatoled", type=gpiod.LINE_REQ_EV_BOTH_EDGES)
    display_on = False

    i2c0_bus.write_i2c_block_data(
        0x3C,
        0x00,
        [
            0xAE,  # set display off
            0x00,  # set lower column address
            0x10,  # set higher column address
            0x40,  # set display start line
            0xB0,
            0x81,  # set page address
            0xCF,  # set screen flip
            0xA1,  # set segment remap
            0xA8,  # set multiplex ratio
            0x3F,  # set duty 1/64
            0xC8,  # set com scan direction
            0xD3,
            0x00,  # set display offset
            0xD5,
            0x80,  # set osc division
            0xD9,
            0xF1,  # set pre-charge period
            0xDA,
            0x12,  # set com pins
            0xDB,
            0x40,  # set vcomh
            0x8D,
            0x14,  # set charge pump on
            0xA6,  # set display normal (not inverse)
            0x20,
            0x00,  # set horizontal addressing mode
            0xAF,  # set display on
        ],
    )

    while True:
        #time.sleep(0.025)
        vals = lines.event_wait(sec=1)
        current_time = time.time()

        if vals:
            for line in vals:
                event = line.event_read()
                if event.type == gpiod.LineEvent.RISING_EDGE:
                    offset = event.source.offset()
                    if offset == 0:
                        cmd_index = key1_cmd_index
                    elif offset == 2:
                        cmd_index = key2_cmd_index
                    elif offset == 3:
                        cmd_index = key3_cmd_index

                    display_refresh_time = 0
                    display_off_time = current_time + DISPLAY_OFF_TIMEOUT
                    continue
                elif event.type == gpiod.LineEvent.FALLING_EDGE:
                    continue
                else:
                    raise TypeError('Invalid event type')

        if current_time > display_off_time:
            if display_on:
                i2c0_bus.write_i2c_block_data(0x3C, 0x00, [0xAE])  # set display off
                display_on = False
            continue
        elif current_time > display_refresh_time:
            if not display_on:
                i2c0_bus.write_i2c_block_data(0x3C, 0x00, [0xAF])  # set display on
                display_on = True

            if cmd_index == 0:
                key1_cmd_index = 1
                key2_cmd_index = 2
                key3_cmd_index = 3
                splash = Image.open("splash.png")
                image.paste(splash)
                write_i2c_image_data(i2c0_bus, image)
                splash.close()
                display_refresh_time = current_time + DISPLAY_OFF_TIMEOUT
            elif cmd_index == 1:
                key1_cmd_index = 0
                key2_cmd_index = 2
                key3_cmd_index = 3
                text1 = time.strftime("%A")
                text2 = time.strftime("%e %b %Y")
                text3 = time.strftime("%X")
                image_draw.rectangle((0, 0, 128, 64), 0)
                image_draw.text((6, 2), text1, 1, image_font15)
                image_draw.text((6, 20), text2, 1, image_font15)
                image_draw.text((6, 36), text3, 1, image_font25)
                display_refresh_time = current_time + 1
                write_i2c_image_data(i2c0_bus, image)
            elif cmd_index == 2:
                key1_cmd_index = 1
                key2_cmd_index = 0
                key3_cmd_index = 3
                text1 = subprocess.check_output(
                    "ip a show | grep -E '^\s*inet' | grep -m1 global | awk '{printf \"IPv4: %s\", $2}' | sed 's|/.*||'",
                    shell=True,
                    text=True,
                )
                text2 = subprocess.check_output(
                    'df -h | awk \'$NF=="/"{printf "Card: %d/%dGB %s", $3,$2,$5}\'',
                    shell=True,
                    text=True,
                )
                text3 = subprocess.check_output(
                    "free -m | awk 'NR==2{printf \"RAM:  %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'",
                    shell=True,
                    text=True,
                )
                text4 = subprocess.check_output(
                    "top -bn1 | grep load | awk '{printf \"Load: %.2f\", $(NF-2)}'",
                    shell=True,
                    text=True,
                )
                text5 = subprocess.check_output(
                    "cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"Temp: %3.1fc\", $1/1000}'",
                    shell=True,
                    text=True,
                )
                image_draw.rectangle((0, 0, 128, 64), 0)
                image_draw.text((6, 2), text1, 1, image_font10)
                image_draw.text((6, 14), text2, 1, image_font10)
                image_draw.text((6, 26), text3, 1, image_font10)
                image_draw.text((6, 38), text4, 1, image_font10)
                image_draw.text((6, 50), text5, 1, image_font10)
                display_refresh_time = current_time + 2
                write_i2c_image_data(i2c0_bus, image)
            elif cmd_index == 3:
                key1_cmd_index = 1
                key2_cmd_index = 2
                key3_cmd_index = 4
                image_draw.rectangle((0, 0, 128, 64), 0)
                image_draw.text((6, 2), "Shutdown?", 1, image_font15)
                image_draw.rectangle((4, 22, 124, 34), 1)
                image_draw.text((6, 22), "No", 0, image_font10)
                image_draw.text((6, 36), "Yes", 1, image_font10)
                image_draw.text((6, 54), "F3: Toggle Choices", 1, image_font8)
                display_refresh_time = current_time + 5
                write_i2c_image_data(i2c0_bus, image)
            elif cmd_index == 4:
                key1_cmd_index = 99
                key2_cmd_index = 4
                key3_cmd_index = 3
                image_draw.rectangle((0, 0, 128, 64), 0)
                image_draw.text((6, 2), "Shutdown?", 1, image_font15)
                image_draw.rectangle((4, 36, 124, 48), 1)
                image_draw.text((6, 22), "No", 1, image_font10)
                image_draw.text((6, 36), "Yes", 0, image_font10)
                image_draw.text((6, 54), "F1: Confirm Shutdown", 1, image_font8)
                display_refresh_time = current_time + 5
                write_i2c_image_data(i2c0_bus, image)
            elif cmd_index == 99:  # break and shutdown cmd_index 99
                break

except KeyboardInterrupt:
    print(" CTRL+C detected")
except Exception as error:
    print(error)

finally:
    i2c0_bus.write_i2c_block_data(0x3C, 0x00, [0xAE])  # set display off
    if cmd_index == 99:  # shutdown now if the command index was 99
        os.system("shutdown now")
    else:
        exit(0)
