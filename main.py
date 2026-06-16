import cv2 as c
import pyautogui as p
import openpyxl as o
from time import sleep
from keyboard import add_hotkey
from tkinter import messagebox
from PIL import ImageGrab
from skimage.metrics import structural_similarity as ssim
from os import _exit

debug = True
p.PAUSE = 0.05
workbook = o.load_workbook("data.xlsx")
sheet = workbook["sheet"]
data = [[], [], [], [], []]
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for section in range(5):
    for row in range(2,210):
        row = [sheet[f"{alphabet[section*2]}{row}"].value, sheet[f"{alphabet[section*2+1]}{row}"].value]
        if row[0] is not None:
            row[0] = row[0].split()
            data[section].append(row)
regions = [(0,0,1,1), (0,0,1,1), (0,0,1,1), (0,0,1,1)]
ButtonPos = [(0,0), (0,0), (0,0), (0,0)]
possibleSymbols = ["clover", "crown", "net", "snake", "double", "coinStack", "coin", "nothing"]

if messagebox.askyesno("","Are you using the golden slot machine?"):
    rerollCount = 5
else:
    rerollCount = 3

def stop():
    _exit(0)
add_hotkey('escape', stop)

def detectSymbol(region):
    global possibleSymbols
    match = None
    bestScore = 0
    symbol = c.cvtColor(ImageGrab.grab(region), c.COLOR_BGR2GRAY)
    for name in possibleSymbols:
        score, _ = ssim(symbol, c.imread(f"symbols/{name}.png"), full=True)
        if score >= bestScore:
            bestScore = score
            match = name
    return match

def rerollCheck(symbols):
    global rerollCount, rerollsUsed, possibleSymbols
    if rerollsUsed >= rerollCount:
        return False, 0
    reroll = False
    index = 0
    sortedSymbols = sorted(symbols, key=lambda x: {value: i for i, value in enumerate(possibleSymbols)}[x])
    for state in data[rerollCount-rerollsUsed-1]:
        if state[0] == sortedSymbols:
            reroll = True
            for slot in range(4):
                if symbols[slot] ==state[1]:
                    index = state[1]
                    break
            break
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
            if debug:
                sleep(1)
            p.click()
            sleep(1.5)
        else:
            break
    p.moveTo(1650,410)
    if debug:
        sleep(1)
    p.click()
    pixel = p.pixel(1675, 255)
    while pixel[0] > 30 or pixel[1] > 30 or pixel[2] > 30:
        sleep(0.05)
        pixel = p.pixel(1675, 255)
    sleep(3.4)