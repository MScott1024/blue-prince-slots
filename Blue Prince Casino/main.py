import cv2 as c
import pyautogui as p
from time import sleep
from keyboard import add_hotkey
from tkinter import messagebox
from PIL import ImageGrab
from skimage.metrics import structural_similarity as ssim
from os import _exit

regions = [(0,0,1,1), (0,0,1,1), (0,0,1,1), (0,0,1,1)]
ButtonPos = [(0,0), (0,0), (0,0), (0,0)]

if messagebox.askyesno("","Are you using the golden slot machine?"):
    rerollCount = 5
else:
    rerollCount = 3

def stop():
    _exit(0)
add_hotkey('escape', stop)

def detectSymbol(region):
    match = None
    bestScore = 0
    symbol = c.cvtColor(ImageGrab.grab(region), c.COLOR_BGR2GRAY)
    for name in ["clover, crown, net, snake, double, coinStack, coin, nothing"]:
        score, _ = ssim(symbol, c.imread(f"symbols/{name}.png"), full=True)
        if score >= bestScore:
            bestScore = score
            match = name
    return match

def rerollCheck(symbols):
    global rerollCount, rerollsUsed
    if rerollsUsed >= rerollCount:
        return False, 0
    reroll = False
    index = 0
    #3 crowns = yes
    #3 crowns 1 clover = no
    #2 coins = no
    #2 coins 1 double = yes
    #2 stacks = no
    #2 stacks 1 double = yes
    



    if reroll:
        rerollsUsed += 1
    return reroll, index

while True:
    rerollsUsed = 0
    while True:
        symbols = []
        for region in regions:
            symbols.append(detectSymbol(region))

        reroll, index = rerollCheck(symbols)
        if reroll:
            p.moveTo(ButtonPos[index])
            sleep(.1)
            p.click()
            sleep(0)
        else:
            break
    p.moveTo(0,0)
    sleep(.1)
    p.click()
    # wait until machine is ready again
