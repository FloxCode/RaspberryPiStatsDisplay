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
updateTime    = 3
shutdownDelay = 5
# Daten-Kommandos
uptimeCmd   = "uptime | grep -o 'up [^,]*' | grep -o '[0-9].*' | sed -e 's/days/Tagen/g' | sed -e 's/day/Tag/g'"
cpuLoadCmd  = "top -bn1 | grep load | awk '{printf \"%.1f\", $(NF-2)*100/4}'"
cpuTempCmd  = "vcgencmd measure_temp | grep -o '[0-9]\+\.[0-9]'"
hdUsageCmd  = "df | grep /dev/sda1 | awk '{printf \"%.1f\", $3*100/($3+$4)}'"
sdUsageCmd  = "df | grep /dev/root | awk '{printf \"%.1f\", $3*100/($3+$4)}'"
memUsageCmd = "free | awk 'NR==2{printf \"%.1f\", $3*100/$2 }'"
swapCmd     = "free | awk 'NR==3{printf \"%.1f\", $3*100/$2 }'"
shutdownCmd = "sudo shutdown -h now"

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

class PushButton(object):
    NONE     = 0
    PUSHED   = 1
    RELEASED = 2
    HELD     = 3

    def __init__(self, pin, gpioMode, pullUp, holdTime, debounce):
        GPIO.setmode(gpioMode)
        if(pullUp):
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.pin         = pin
        self.pullUp      = pullUp
        self.holdTime    = holdTime
        self.debounce    = debounce
        self.hasBeenPushed = False
        self.pushTime      = time.time() - 10.0
        self.releaseTime   = self.pushTime - 20.0

    def state(self):
        state  = PushButton.NONE
        pushed = self.pullUp != GPIO.input(self.pin)

        stateChanged = False

        # Merken, ob gedrueckt / losgelassen wurde
        if(pushed and not self.hasBeenPushed or not pushed and self.hasBeenPushed):
            stateChanged = True

        # Als losgelassen / gedrueckt interpretieren, wenn letzter Wechsel lang genug her ist
        now = time.time()
        if(stateChanged):
            if(pushed and int((now - self.pushTime)*1000) > self.debounce):
                state = PushButton.PUSHED
            elif(not pushed and int((now - self.releaseTime)*1000) > self.debounce):
                state = PushButton.RELEASED
        else:
            if(pushed and int((now - self.pushTime)*1000) > self.holdTime):
                state = PushButton.HELD

        if(stateChanged):
            if(pushed):
                self.pushTime = now
            else:
                self.releaseTime = now

        self.hasBeenPushed = pushed

        return state

cmdIndex = 0
btn = PushButton(PIN_SHUTDOWN, GPIO.BCM, True, 1000, 50)
vary = True
lastUpdate = time.time() - updateTime
holdStart = None
while True:
    now = time.time()

    # Buttonstatus bestimmen
    state = btn.state()
    if(PushButton.RELEASED == state):
        vary = not vary

    if(PushButton.HELD == state):
        if(holdStart == None):
            holdStart = now
        else:
            # Berechnen, seit wann gehalten wird
            seconds = int(now - holdStart)
            if(seconds < shutdownDelay):
                write(disp, "Shutdown:", "         "+str(shutdownDelay-seconds))
            else:
                write(disp, "", "SHUTDOWN")
                subprocess.call(shutdownCmd, shell=True)
    else:
        holdStart = None

    # Statusausgaben
    update = int(now - lastUpdate) > updateTime 
    if(not PushButton.HELD == state and update):
        if(vary):
            cmdIndex = (cmdIndex+1) % len(cmds)
        showData(disp, cmds[cmdIndex][0], cmds[cmdIndex][1], cmds[cmdIndex][2])
        lastUpdate = now

    time.sleep(0.05)
    

