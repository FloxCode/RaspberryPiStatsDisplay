#!/usr/bin/python3
# coding=utf-8
import Adafruit_SSD1306
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time

# Konfiguration
RST = None
PIN_SHUTDOWN = 26
height =  32
width  = 128
x      =   0
y      =  -3
sleepTime = .5
shutdownDelay = 5
# Daten-Kommandos
uptimeCmd   = "uptime | grep -o 'up [^,]*' | grep -o '[0-9].*' | sed -e 's/days/Tagen/g' | sed -e 's/day/Tag/g'"
cpuLoadCmd  = "top -bn1 | grep load | awk '{printf \"%.1f\", $(NF-2)*100/4}'"
cpuTempCmd  = "vcgencmd measure_temp | grep -o '[0-9]\+\.[0-9]'"
hdUsageCmd  = "df | grep /dev/sda1 | awk '{printf \"%.1f\", $3*100/($3+$4)}'"
sdUsageCmd  = "df | grep /dev/root | awk '{printf \"%.1f\", $3*100/($3+$4)}'"
memUsageCmd = "free | awk 'NR==2{printf \"%.1f\", $3*100/$2 }'"
swapCmd     = "free | awk 'NR==3{printf \"%.1f\", $3*100/$2 }'"

cmds = [(uptimeCmd,   "Läuft seit",  ""),
        (cpuLoadCmd,  "CPU-Last",    "%"),
        (cpuTempCmd,  "CPU-Temp.",   "\'C"),
        (hdUsageCmd,  "USB-Festpl.", "%"),
        (sdUsageCmd,  "Micro-SD",    "%"),
        (memUsageCmd, "RAM",         "%"),
        (swapCmd,     "Swap",        "%")
        ]

disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
disp.begin()
disp.clear()
disp.display()

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
#font = ImageFont.truetype('fonts/Retron2000.ttf', 27)
fontData = ImageFont.truetype('fonts/monofonto.ttf', 24)
fontText = ImageFont.truetype('fonts/monofonto.ttf', 15)

def write(display, header, text):
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x, y),    header, font=fontText, fill=255)
    draw.text((x, y+11), text,   font=fontData, fill=255)
    display.image(image)
    display.display()

def showData(display, dataCmd, preText, postText):
    value = str(subprocess.check_output(dataCmd, shell=True).strip(), 'utf-8')
    print(preText+" "+value+postText)
    write(display, preText, value+postText)

def shutdownCheck(display, shutDownDelay):
    if(False == GPIO.input(PIN_SHUTDOWN)):
        write(display, "SHUTDOWN...", "         "+str(shutDownDelay))

cmdIndex = 0
while True:
    #
    shutdownCheck(disp, shutdownDelay)
    
    # Statusausgaben
    showData(disp, cmds[cmdIndex][0], cmds[cmdIndex][1], cmds[cmdIndex][2])
    time.sleep(sleepTime)
    
    cmdIndex = (cmdIndex+1) % len(cmds)

