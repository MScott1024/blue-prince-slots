import cv2 as c
from PIL import ImageGrab
import datetime as datetime
region = (0,0,1,1)
symbol = c.cvtColor(ImageGrab.grab(region), c.COLOR_BGR2GRAY)
symbol.save(f"Symbols/{datetime.time(datetime.now())}.png")