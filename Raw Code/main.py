import cv2 as c
import pyautogui as p
import openpyxl as o
import numpy as n
import tkinter as tk
from time import sleep
from keyboard import add_hotkey, is_pressed
from tkinter import messagebox
from PIL import ImageGrab
from skimage.metrics import structural_similarity as ssim
from os import _exit

debug = False

root = tk.Tk()
root.attributes('-topmost', True)
root.geometry("1x1+0+5000")
if messagebox.askyesno("","Are you using the golden slot machine?"):
    rerollCount = 5
    regions = [(679,506,808,705), (828,506,958,705), (980,506,1110,705), (1125,506,1256,705)]
    colorCheckPixel = (1677,314)
    workbook = o.load_workbook("goldMachineData.xlsx")
else:
    rerollCount = 3
    regions = [(775,493,895,675), (914,493,1033,675), (1060,493,1181,675), (1200,493,1321,675)]
    colorCheckPixel = (1770, 336)
    workbook = o.load_workbook("regularMachineData.xlsx")
root.destroy()
root = tk.Tk()
root.attributes('-topmost', True)
root.geometry("1x1+0+5000")
messagebox.showinfo("","Bot ready. Press space to start and escape to exit.")
root.destroy()

sheet = workbook["sheet"]
p.PAUSE = 0.06
p.FAILSAFE = False
data = [[], [], [], [], []]
possibleSymbols = ["clover", "crown", "net", "snake", "double", "stack", "coin", "-"]
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
cursorPos = 5
imgDetectRetryNum = 0

for section in range(5):
    for row in range(2,210):
        row = [sheet[f"{alphabet[section*2]}{row}"].value, sheet[f"{alphabet[section*2+1]}{row}"].value]
        if row[0] is not None:
            row[0] = row[0].split()
            data[section].append(row)

def stop():
    _exit(0)
add_hotkey('escape', stop)

def scoreCheck(slots):
    score = 0
    if slots.count('coin') == 4:
        score = 5
    elif slots.count('coin') == 3:
        score = 3
    elif slots.count('stack') == 4:
        score = 15
    elif slots.count('stack') == 3:
        score = 9
    elif slots.count('crown') == 4:
        score = 100
    score += slots.count('clover')*10
    if 'snake' in slots:
        if 'net' in slots:
            score += slots.count('snake')*3
        else:
            score = 0
    score *= (2 ** slots.count('double'))
    return score

def detectSymbol(region):
    global possibleSymbols, imgDetectRetryNum, debug
    match = None
    bestScore = 0
    symbol = c.cvtColor(n.array(ImageGrab.grab(region)), c.COLOR_BGR2GRAY)
    for name in possibleSymbols:
        comparisonSymbol = n.load(f"symbols/{name}.npy")
        diffx = symbol.shape[0] - comparisonSymbol.shape[0]
        diffy = symbol.shape[1] - comparisonSymbol.shape[1]
        if diffx > 0:
            symbol = symbol[diffx//2:comparisonSymbol.shape[0]+diffx//2,:]
        elif diffx < 0:
            comparisonSymbol = comparisonSymbol[(-diffx)//2:symbol.shape[0]+(-diffx)//2,:]
        if diffy > 0:
            symbol = symbol[:,diffy//2:comparisonSymbol.shape[1]+diffy//2]
        elif diffy < 0:
            comparisonSymbol = comparisonSymbol[:,(-diffy)//2:symbol.shape[1]+(-diffy)//2]
        score, _ = ssim(symbol, comparisonSymbol, full=True)
        if score >= bestScore:
            bestScore = score
            match = name
    if debug:
        print(f'detected {match}, confidence {bestScore}')
    if bestScore < .1:
        print('img detection FAILED')
        if imgDetectRetryNum < 5:
            imgDetectRetryNum += 1
            sleep(.5)
            match = detectSymbol(region)
        else:
            root = tk.Tk()
            root.attributes('-topmost', True)
            root.geometry("1x1+0+5000")
            messagebox.showinfo("","Image detection failed. Program stopped.")
            root.destroy()
            _exit(0)
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
            for i in range(4):
                if symbols[i] == state[1]:
                    index = i
            break
    if reroll:
        rerollsUsed += 1
    return reroll, index

while True:
    if is_pressed('space'):
        break
    sleep(.05)
for _ in range(7):
    p.press('right')
while True:
    cursorPos = 5
    p.press('enter')
    pixel = p.pixel(colorCheckPixel[0], colorCheckPixel[1])
    counter = 0
    while pixel[0] > 30 or pixel[1] > 30 or pixel[2] > 30:
        sleep(0.05)
        if counter > 80:
            break
        else:
            counter += 1
        pixel = p.pixel(colorCheckPixel[0], colorCheckPixel[1])
    sleep(3.4)
    rerollsUsed = 0
    previousScore = 0
    
    while True:
        symbols = []
        for region in regions:
            symbols.append(detectSymbol((region)))
        if debug:
            print(f'detected symbols: {symbols}')
        reroll, index = rerollCheck(symbols)
        currentScore = scoreCheck(symbols)
        if currentScore != previousScore or debug:
            previousScore = currentScore
            sleep(1)
        if reroll:
            if debug:
                print(f'rerolling slot {index+1}')
            while cursorPos > index:
                p.press('left')
                cursorPos -= 1
            p.press('enter')
            for _ in range(8):
                p.press('right')
            cursorPos = 5
            sleep(1.1)
        else:
            if debug:
                print(f'pulling lever')
            break