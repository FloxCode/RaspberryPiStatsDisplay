#!/usr/bin/python3
# coding=utf-8
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time

RST = None

disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
disp.begin()
disp.clear()
disp.display()

height = 32
width  = 128
x      = 0
y      = -3

sleepTime = 5

uptimeCmd   = "uptime | grep -o 'up [^,]*' | grep -o '[^ ]*$'"
cpuLoadCmd  = "top -bn1 | grep load | awk '{printf \"%.1f\", $(NF-2)*100/4}'"
cpuTempCmd  = "vcgencmd measure_temp | grep -o '[0-9]\+\.[0-9]'"
hdUsageCmd  = "df | grep /dev/sda1 | awk '{printf \"%.1f\", $3*100/($3+$4)}'"
sdUsageCmd  = "df | grep /dev/root | awk '{printf \"%.1f\", $3*100/($3+$4)}'"
memUsageCmd = "free -m | awk 'NR==2{printf \"%.1f\", $3*100/$2 }'"

image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
#font = ImageFont.truetype('fonts/Retron2000.ttf', 27)
fontData = ImageFont.truetype('fonts/monofonto.ttf', 24)
fontText = ImageFont.truetype('fonts/monofonto.ttf', 15)

def showData(display, dataCmd, preText, postText):
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    value = str(subprocess.check_output(dataCmd, shell=True).strip(), 'utf-8')
    print(preText+" "+value+postText)
    draw.text((x, y),    preText,        font=fontText, fill=255)
    draw.text((x, y+11), value+postText, font=fontData, fill=255)
    display.image(image)
    display.display()

while True:
   
    # Zeit seit Systemstart
    showData(disp, uptimeCmd, "Läuft seit", "")
    time.sleep(sleepTime)

    # CPU-Temperatur
    showData(disp, cpuTempCmd, "CPU-Temp.", "\'C")
    time.sleep(sleepTime)
    
    # CPU-Auslastung
    showData(disp, cpuLoadCmd, "CPU-Load", "%")
    time.sleep(sleepTime)

    # Festplatte
    showData(disp, hdUsageCmd, "Ext. Festpl.", "%")
    time.sleep(sleepTime)

    # SD-Karte
    showData(disp, sdUsageCmd, "Micro-SD", "%")
    time.sleep(sleepTime)

    # Arbeitsspeicher
    showData(disp, memUsageCmd, "RAM", "%")
    time.sleep(sleepTime)
