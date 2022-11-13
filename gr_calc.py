import os
import time
import math

#import numpy as np

class flightData:
    def __init__(self, fileName):
        self.pilotName = ''
        self.PGName = '' 
        self.timeList = []
        self.latitude = []
        self.longitude = []
        self.gpsEle = []
        self.pressEle = []
        self.nStartFlight = 0
        self.nEndFlight = 0

        self.lat_rad = []
        self.lon_rad = []
        self.d = []
        self.dt = []
        self.Vkmh = []
        self.Vms = []
        self.Vmean = 0
        self.GRDiff = []
        self.dist = 0
        self.dAlt = 0
        self.GR = 0
        self.GRAvrg = 0
        self.Vavg = 0
        self.deltaEle = []
        self.flightTime = "" 
        self.dTime = []
        self.n = 0

        fileRead = open(fileName,'r')
        Lines = fileRead.readlines()
        self.igcData = []
        for line in Lines:
            if (line[0]=="B"):
                self.igcData.append(line.rstrip())
        self.bLen = 0
        self.bLen = len(self.igcData)
        pn = os.path.splitext(fileName)[0].split('\\')
        self.pilotName = pn[-1]
        self.runCalculation()

    def runCalculation(self):
        self.getTimeFromBStrings()
        self.getCoordinates()
        self.getEle()
        self.getDistanceSpeed()
        self.getStartEnd()
        self.getGR()

    #get times from igc data
    def getTimeFromBStrings (self):
        for i in self.igcData:
            curTime = time.strptime(i[1:7],"%H%M%S")
            self.timeList.append(curTime)

    def getCoordinates (self):
        for i in self.igcData:
            #get latitude
            curGrad = int(i[7:9])
            curMin = int(i[9:14])
            coordinates = (curGrad + (curMin/60000))
            self.latitude.append(coordinates)
            self.lat_rad.append(coordinates * math.pi / 180)

            #get longitude
            curGrad = int(i[16:18])
            curMin = int(i[18:23])
            coordinates = (curGrad + (curMin/60000))
            self.longitude.append(coordinates)
            self.lon_rad.append(coordinates * math.pi / 180)

    def getEle (self):
        for i in self.igcData:
            curEle = int(i[25:30])
            self.gpsEle.append(curEle)
            curEle = int(i[30:35])
            self.pressEle.append(curEle)

    def getDistanceSpeed (self):
        for i in range(len(self.igcData)):
            acosVal = math.sin(self.lat_rad[i-1]) * math.sin(self.lat_rad[i]) + math.cos(self.lat_rad[i-1]) * math.cos(self.lat_rad[i]) * math.cos(self.lon_rad[i] - self.lon_rad[i-1])
            # distance between two points, m
            if (acosVal) <= 1 and (acosVal >= -1):
                self.d.append(math.acos(acosVal) * 6371000)
            else:
                self.d.append(0)
            # delta time in seconds
            self.dt.append(((self.timeList[i].tm_hour*3600 + self.timeList[i].tm_min*60 + self.timeList[i].tm_sec) - (self.timeList[i - 1].tm_hour*3600 + self.timeList[i - 1].tm_min*60 + self.timeList[i - 1].tm_sec)))
            if (self.dt[i] > 0):
                # speed between two points, km/h
                self.Vkmh.append((self.d[i]/1000)/(self.dt[i]/3600))
                # speed between two points, m/s
                self.Vms.append((self.d[i])/self.dt[i])
            else:
                self.Vkmh.append(0)
                self.Vms.append(0)

    def getStartEnd (self):
        for i in range(len(self.igcData)):
            if (self.Vkmh[i] > 8) and (self.nStartFlight == 0):
                self.nStartFlight = i
            if (self.Vkmh[i] < 9) and (self.nStartFlight > 0):
                self.nEndFlight = i
        self.n = self.nEndFlight - self.nStartFlight
        start = (self.timeList[self.nStartFlight].tm_hour*3600 + self.timeList[self.nStartFlight].tm_min*60 + self.timeList[self.nStartFlight].tm_sec)
        end = (self.timeList[self.nEndFlight].tm_hour*3600 + self.timeList[self.nEndFlight].tm_min*60 + self.timeList[self.nEndFlight].tm_sec)
        self.flightTime = time.gmtime(end - start)
        #self.Vmean = sum(self.Vkmh[self.nStartFlight,self.nEndFlight])/int(self.n)

    def getGR(self):
        self.dist = 0
        self.dAlt = self.pressEle[self.nStartFlight] - self.pressEle[self.nEndFlight]
        for i in range (self.nStartFlight, self.nEndFlight):
            self.dTime.append(self.dt)
            self.dist = self.dist + self.d[i]
        self.GR = self.dist / self.dAlt

fileList = []
curDir = os.getcwd()
for path in os.listdir(curDir):
    if os.path.isfile(os.path.join(curDir,path)):
        filename, file_extension = os.path.splitext(path)
        if (file_extension == ".igc"):
            fileList.append(os.path.join(curDir,path))

var = [flightData(fileList[i]) for i in range(len(fileList))]
print ("{:25s}".format(str("File name")) + "Distance\tAlti\tGR\t\tStartTime\tLandTime\tairtime")
for i in var:
    print("{:25s}".format((i.pilotName))
    + "{:f}".format(i.dist) + '\t' 
    + str(i.dAlt) + '\t'
    + "{:3f}".format(i.GR) + '\t'
    + str(i.timeList[i.nStartFlight].tm_hour).zfill(2) +":"+ str(i.timeList[i.nStartFlight].tm_min).zfill(2) + ":" +str(i.timeList[i.nStartFlight].tm_sec).zfill(2) + '\t'
    + str(i.timeList[i.nEndFlight].tm_hour).zfill(2) +":"+ str(i.timeList[i.nEndFlight].tm_min).zfill(2) + ":" +str(i.timeList[i.nEndFlight].tm_sec).zfill(2) +'\t'
    #+ str(i.flightTime)
    + str(i.flightTime.tm_hour).zfill(2) +":"+ str(i.flightTime.tm_min).zfill(2) + ":" +str(i.flightTime.tm_sec).zfill(2) +'\t'
    #+ str(i.dist/)

    )