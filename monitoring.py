import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading
import numpy as np
import argparse
from argcomplete.completers import ChoicesCompleter
from src.plot_event import plotEvent
from src.plot_histos import plotHistograms
from src.read_config import readConfig
from src.unscrambler import trigIdSort, bufferSort
from analyzer import applyCuts, averageADC
from src.read_file import getEventsTail
import tkinter as tk
from tkinter import ttk
from tkinter import * 
import PIL.Image
from time import sleep
import random
import glob
import shutil

import warnings
warnings.simplefilter("ignore", UserWarning)

plt.switch_backend('agg')
seconds = 0
spillID = 0
spillPath = ''
working = False
currentMax = 0
prevMax =''
started = False
spillWindow = 10


# Button is clicked
def startRun():
        global started
        print('Starting run!')
        started = True
        
# Button is clicked
def sync():
        global working
        if working:
                print(f'WAIT!')
        else:
                print('Syncronized with latest spill')
                global seconds
                seconds = -1

def findNextSpillID(outputDir):
        nextSpillID = 0
        while (f'Spill{nextSpillID}_list.txt' in os.listdir(f'{outputDir}/logs')):
                nextSpillID +=1
        return nextSpillID

# Get input from the text box
def getInputBoxValue():
	userInput = secondsBack.get()
	return userInput

def threadPlot(func, inputFilename, config, outputDir): 
        taskThread = threading.Thread(target=readSpill, args=(inputFilename, config, outputDir))
        taskThread.daemon = True
        taskThread.start()
    
def readSpill(inputFilename, config, outputDir):
    global spillWindow
    allEvents = getEventsTail(inputFilename, config, timeWindow = spillWindow, log = True, outPath = outputDir)
    passedEvents = applyCuts(allEvents, config)
    averageEvent = averageADC(passedEvents)
    runNumber = inputFilename.split('Run')[1].split('_')[0]
    global working
    global currentMax

    randomEvents = []
    while (len(randomEvents) < 2):
            i = random.randint(0, len(passedEvents)-1)
            if i not in randomEvents:
                    randomEvents.append(i)
                    plotEvent(passedEvents[i], outputDir, runNumber, len(allEvents), config, passingEvents = len(passedEvents), tag = f'Spill {spillID}')
            
            
    avgMap, maximumChannel = averageADC(passedEvents)
    plotEvent(avgMap, outputDir, runNumber, len(allEvents), config, avg=True, passingEvents = len(passedEvents), tag = f'Spill {spillID}') 
    plotHistograms(passedEvents, config, runNumber, outputDir, tag = f'Spill: {spillID}')
    currentMax=maximumChannel
    working = False

    
    
def loop(inputFilename, config, outputDir, labelList, root):
        global seconds
        global spillID
        global spillPath
        global working
        global currentMax
        global prevMax
        global started
        global spillWindow

        
        if started == False:
                var = tk.IntVar()
                button = Button(root, text='Start', bg='#A9A9A9', font=('arial', 20, 'normal'), command=lambda: var.set(1))
                button.place(x=400, y=380)
                button.wait_variable(var)
                startRun()
                root.geometry('1200x900')
                button.configure(text = "Sync", command = sync)
                labelList[0].config(text=f'Previous spill: XX')
                labelList[1].config(text=f'Collecting new spill...')
                
        seconds +=1
        if seconds > 9:
                labelList[1].config(text=f'Expecting a spill in {60- seconds} seconds')
        else:
                labelList[1].config(text=f'Collecting new spill{"."*(seconds%3+1)}')
        if working == False:
                labelList[5].config(text=f'')
                avgADC = makeImage(f'{spillPath}/average_ADC.png', 250, 400, root)
                labelList[2].configure(image=avgADC)
                labelList[2].image = avgADC
                labelList[2].place(x=54, y=34)
                
                sumHist = makeImage(f'{spillPath}/channel_sum_histogram.png', 530, 365, root)
                labelList[3].configure(image=sumHist)
                labelList[3].image = sumHist
                labelList[3].place(x=54, y=480)
                
                maxHistPath = f'{spillPath}/channel_{str(currentMax).zfill(2)}_histogram.png'
                maxHist = makeImage(maxHistPath, 530, 365, root)
                labelList[6].configure(image=maxHist)
                labelList[6].image = maxHist
                labelList[6].place(x=650, y=480)

                randomEventsPaths = glob.glob(f'{spillPath}/event*.png')
                randOne = makeImage(randomEventsPaths[0], 250, 400, root)
                labelList[7].configure(image=randOne)
                labelList[7].image = randOne
                labelList[7].place(x=650, y=34)

                randTwo = makeImage(randomEventsPaths[1], 250, 400, root)
                labelList[8].configure(image=randTwo)
                labelList[8].image = randTwo
                labelList[8].place(x=920, y=34)
                
        else:
                labelList[5].config(text=f'Producing last spill plots...')

        

        if seconds == spillWindow:
                spillID = findNextSpillID(outputDir)
                spillPath = f'{outputDir}/images/Spill{spillID}'
                os.makedirs(spillPath, exist_ok=True)
                labelList[0].config(text=f'Previous spill: {spillID}')
                labelList[5].config(text=f'Producing last spill plots...')

                if not working:
                        working = True
                        threadPlot(readSpill,inputFilename, config, f'{spillPath}')
        if seconds % 60 == 0:
                spillID = findNextSpillID(outputDir)
                labelList[0].config(text=f'Previous spill: {spillID}')
                labelList[1].config(text=f'Collecting new spill...')
                seconds = 0

                # Clear out old images, so the folder doesn't blow up
                if spillID % 49 == 0:
                        print("About to delete image files from spills older than 30!")
                        print(f'Save things you need to keep from {outputDir}/images/')
                if spillID % 25 == 0:
                        index = 0
                        imageDirs = sorted(glob.glob(f'{outputDir}/images/*'), key=os.path.getmtime)
                        while len(imageDirs) > 50:
                                shutil.rmtree(imageDirs[0])
                                imageDirs.pop(0)
                
        root.after(1000, loop, inputFilename, config, outputDir, labelList, root) 

def startGUI(inputFilename, config, outputDir):
        root = Tk()
        global seconds
        global spillID
        global spillPath
        global prevMax
        
        # Create tkinter window
        root.geometry('1000x500')
        root.configure(background='#A9A9A9')
        root.title('DarkQuest Testbeam DQM')
        
        canvas = tk.Canvas(root, width=1200, height=900, background='#A9A9A9')
        canvas.pack()
        
        labelList = []

        runNumber = inputFilename.split('Run')[1].split('_')[0]              
        Label(root, text=f'Run: {runNumber}', bg='#A9A9A9', font=('arial', 22, 'normal')).place(x=324, y=224)
        
        spillTag = Label(root, text=f'Previous spill: XX', bg='#A9A9A9', font=('arial', 16, 'normal'))
        spillTag.place(x=324, y=255)

        updateTag = Label(root, text=f'Press \'Start\' in time with the next spill', bg='#A9A9A9', font=('arial', 16, 'normal'), anchor="e")
        updateTag.place(x=324, y=280)

        workingTag = Label(root, text=f'', bg='#A9A9A9', font=('arial', 16, 'normal'), anchor="e")
        workingTag.place(x=324, y=305)

        avgADCL = Label(root, text='Last spill average ADCs', bg='#A9A9A9', font=('arial', 12, 'normal'),compound='bottom')
        histogramL = Label(root, text='Histogram of channel summed ADC', bg='#A9A9A9', font=('arial', 12, 'normal'), compound='bottom')
        histogramMaxL = Label(root, text='Histogram of channel with highest average ADC', bg='#A9A9A9', font=('arial', 12, 'normal'), compound='bottom')

        randOneL = Label(root, text='Random events', bg='#A9A9A9', font=('arial', 12, 'normal'), compound='bottom')
        randTwoL = Label(root, text=' ', bg='#A9A9A9', font=('arial', 12, 'normal'), compound='bottom')


        
        labelList.append(spillTag) # [0]
        labelList.append(updateTag) # [1]
        labelList.append(avgADCL) # [2]
        labelList.append(histogramL) # [3]
        labelList.append('buttonPlaceholder') # [4]
        labelList.append(workingTag) # [5]
        labelList.append(histogramMaxL) # [6]
        labelList.append(randOneL) # [7]
        labelList.append(randTwoL) # [8]

        # Generate first plot set
        readSpill(inputFilename, config, f'{spillPath}')
        labelList[0].config(text=f'Previous spill: XX')
        prevMax = f'{spillPath}/channel_{str(currentMax).zfill(2)}_histogram.png'

        root.after(1000, loop, inputFilename, config, outputDir, labelList, root)  # Schedule first check.        
        root.mainloop()        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Janus event list')
    parser.add_argument('-c', '--configFile', dest='configFile', type=str, help='The name of the .cfg file for the input run file', default=None)
    args = parser.parse_args()
    inputFilename = args.filename

    global spillID
    global spillPath
    
    config = {}
    if args.configFile is None:
        config = {
            'triggerThresh': 400,
            'vetoThresh': 400,
            'sumThresh': -1,
            'sumMax': 120000,
            'emcalCfg': [
                ['o', 'o', 'o', 'o'],
                ['o', 'o', 'o', 'o'],
                ['o', 'o', 'o', 'o'],
                ['o', 'o', 'o', 'o']
            ],
            'topHodoCfg': ['x', 'x','x', 'x'],
            'bottomHodoCfg': ['x', 'x','x', 'x'],
            'topHodoEnabled': False,
            'botHodoEnabled': False,
            'name': 'allChannel',
            'tag' : 'allChannel',
            'gain' : 'LG'
        }
    else:
        config = readConfig(args.configFile)

    runNumber = args.filename.split('Run')[1].split('_')[0]        
    outputDir = f'output/run{runNumber}_{config["name"]}_live'
    os.makedirs(f'{outputDir}/images', exist_ok=True)
    os.makedirs(f'{outputDir}/logs', exist_ok=True)

    spillID = findNextSpillID(outputDir)
    spillPath = f'{outputDir}/images/Spill{spillID}'
    os.makedirs(f'{spillPath}', exist_ok=True)
    
    startGUI(inputFilename, config, outputDir)


def makeImage(imagePath, xscale, yscale, root):
        # Show average ADC
        img = PIL.Image.open(imagePath)
        img = img.resize((xscale, yscale), PIL.Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img, master=root)
        return img_tk

if __name__ == "__main__":
    main()

