import cv2 as c
from PIL import ImageGrab
from datetime import datetime
from time import sleep
import numpy as n
region = (1060,493,1180,675)
sleep(2)
symbol = c.cvtColor(n.array(ImageGrab.grab((region))), c.COLOR_BGR2GRAY)
n.save(f"Symbols/{datetime.now().strftime('%H-%M-%S.%f')}",symbol)