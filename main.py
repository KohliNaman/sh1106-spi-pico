from machine import Pin, SPI
from sh1106 import SH1106_SPI
import framebuf
from time import sleep
from utime import sleep_ms

spi = SPI(0, 10485760, mosi=Pin(3), sck=Pin(2))
oled = SH1106_SPI(128, 64, spi, Pin(5),Pin(7), Pin(6))
#oled = SH1106_SPI(WIDTH, HEIGHT, spi, dc,rst, cs) use GPIO PIN NUMBERS
while True:
    try:
                oled.fill(0)
                oled.show()
                #sleep(1)
                oled.text("Naman is hero",0,0)
                oled.text("test line 2",0,8)
                oled.text("is this the 3rd line",0,16) #this will not complete and not wrap,is intentional
                oled.show()
                sleep_ms(1000)
    except KeyboardInterrupt:
        break
