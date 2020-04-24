import klayout.db as pya
from zeropdk.layout.polygons import layout_path
from zeropdk.layout import layout_box
import numpy as np
from functions import *

layout = pya.Layout()
layout.dbu = 0.001
TOP = layout.create_cell("TOP")

workingLayer = layout.layer(4,0) 
chipBorder = layout.layer(7,0)
maskBorder = layout.layer(10,0)
outputLayer = layout.layer(1,0)
sourceLayer = layout.layer(3,0)
port1Layer = layout.layer(2,0)
port2Layer = layout.layer(5,0)

ex = pya.DVector(1,0)
ey = pya.DVector(0,1)

upperRegion = pya.Region()
lowerRegion = pya.Region()
feedlineRegion = pya.Region()
lowZRegion = pya.Region()
highZRegion = pya.Region()

#insert chip/mask border
chipWidth = 11000
chipLength = 19000
layout_box(TOP, chipBorder, -chipLength/2*ey, chipWidth*ex + chipLength/2*ey, ex)

maskWidth = 11600
maskHeight = 19600
layout_box(TOP, maskBorder, -300*ex - maskHeight/2*ey, (chipWidth+300)*ex + maskHeight/2*ey, ex)

upperWGBondPadHeight = 450
upperWGBondPadLength = 300
lowerWGBondPadHeight = upperWGBondPadHeight - 200
lowerWGBondPadLength = upperWGBondPadLength
upperRegionFeedlineWidth = 160
lowerRegionFeedlineWidth = 100
introFeedlineLength = 600
feedlineBendRadius = 350

#creating bond pad boxed on left
cpwStraight(layout, TOP, workingLayer, [0*ex, upperWGBondPadLength*ex], upperWGBondPadHeight, lowerWGBondPadHeight, upperRegion, lowerRegion)
deltaY = 0
#-------------------------------------BEGIN FEED LINE-------------------------------------------------------------------------------------------#

#bond pad tapers
taperPoints = [300*ex, 425*ex, 550*ex]
upperTaperWidths = [450, 305, 160]
lowerTaperWidths = [250, 175, 100]
cpwStraight(layout, TOP, workingLayer, taperPoints, upperTaperWidths, lowerTaperWidths, upperRegion, lowerRegion) 

#CPW straight to first bend
cpwStraight(layout, TOP, workingLayer, [550*ex, (550+introFeedlineLength)*ex], upperRegionFeedlineWidth, lowerRegionFeedlineWidth, upperRegion, lowerRegion)

#CPW bend on feedline
arcCoord1 = (550+introFeedlineLength) * ex
arcCoord2 = arcCoord1 - 2*feedlineBendRadius*ey
bendPoints = [arcCoord1, arcCoord1 + feedlineBendRadius*ex, arcCoord2 + feedlineBendRadius*ex, arcCoord2]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionFeedlineWidth, lowerRegionFeedlineWidth, feedlineBendRadius, upperRegion, lowerRegion)
deltaY = deltaY + 2*feedlineBendRadius

#CPW straight after 1st bend
cpwStraight(layout, TOP, workingLayer, [arcCoord2, arcCoord2-55*ex], upperRegionFeedlineWidth, lowerRegionFeedlineWidth, upperRegion, lowerRegion)

#2nd CPW bend
bendEndPoint = arcCoord2-55*ex-(feedlineBendRadius*ex)-feedlineBendRadius*ey
bendPoints = [arcCoord2-55*ex, arcCoord2-55*ex-(feedlineBendRadius*ex), bendEndPoint]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionFeedlineWidth, lowerRegionFeedlineWidth, feedlineBendRadius, upperRegion, lowerRegion)
deltaY = deltaY + feedlineBendRadius

#end feedline with straight
cpwStraight(layout, TOP, workingLayer, [bendEndPoint, bendEndPoint-4500*ey], upperRegionFeedlineWidth, lowerRegionFeedlineWidth, upperRegion, lowerRegion)
feedlineEndPoint = bendEndPoint - 4500*ey
deltaY = deltaY + 4500

#Bragg mirrors
braggPinW = 80
braggNegW = 5
upperRegionBraggPinW = 80 + (2*5)
lowerRegionBraggPinW = 80
braggTaperLength = 20

#taper to Bragg mirror
taperPoints = [feedlineEndPoint, feedlineEndPoint - 10*ey, feedlineEndPoint - 20*ey]
upperTaperWidths = [160, 125, 90]
lowerTaperWidths = [lowerRegionFeedlineWidth, 90, 80]
cpwStraight(layout, TOP, workingLayer, taperPoints, upperTaperWidths, lowerTaperWidths, upperRegion, lowerRegion)
deltaY = deltaY + 20

feedlineRegion = upperRegion - lowerRegion

#-----END FEEDLINE, BEGIN 1ST LOW Z PERIOD------------------------------------------------------------------------------------------------------------------#

#intro low Z period
lowZLength = 16993.4 #why?
braggBendRadius = 250
lowZStraightLength = lowZLength/3 - np.pi*braggBendRadius
highZLength = 13020.7
highZStraightLength = highZLength/2 - np.pi*braggBendRadius
introLowZBegin = feedlineEndPoint - (20*ey) - (lowZStraightLength/2*ey)
cpwStraight(layout, TOP, workingLayer, [feedlineEndPoint-20*ey, feedlineEndPoint-20*ey-(lowZStraightLength/2*ey)], upperRegionBraggPinW, lowerRegionBraggPinW, upperRegion, lowerRegion)

#1st low Z bend
introLowZEnd = introLowZBegin + 2*braggBendRadius*ex
bendPoints = [introLowZBegin, introLowZBegin - braggBendRadius*ey, introLowZEnd - braggBendRadius*ey, introLowZEnd]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, lowerRegionBraggPinW, braggBendRadius, upperRegion, lowerRegion)
cpwStraight(layout, TOP, workingLayer, [introLowZEnd, introLowZEnd + lowZStraightLength*ey], upperRegionBraggPinW, lowerRegionBraggPinW, upperRegion, lowerRegion)

#2nd low Z bend
secondLowZBendBegin = introLowZEnd + lowZStraightLength * ey
secondLowZBendEnd = secondLowZBendBegin + 2*braggBendRadius * ex
bendPoints = [secondLowZBendBegin, secondLowZBendBegin + braggBendRadius*ey, secondLowZBendEnd+braggBendRadius*ey, secondLowZBendEnd]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, lowerRegionBraggPinW, braggBendRadius, upperRegion, lowerRegion)
cpwStraight(layout, TOP, workingLayer, [secondLowZBendEnd, secondLowZBendEnd-lowZStraightLength*ey], upperRegionBraggPinW, lowerRegionBraggPinW, upperRegion, lowerRegion)

#3rd low Z bend
thirdLowZBendBegin = introLowZEnd + 2*braggBendRadius*ex
thirdLowZBendEnd = thirdLowZBendBegin + 2*braggBendRadius*ex
bendPoints = [thirdLowZBendBegin, thirdLowZBendBegin - braggBendRadius*ey, thirdLowZBendEnd - braggBendRadius*ey, thirdLowZBendEnd]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, lowerRegionBraggPinW, braggBendRadius, upperRegion, lowerRegion)
cpwStraight(layout, TOP, workingLayer, [thirdLowZBendEnd, thirdLowZBendEnd + (lowZStraightLength/2*ey)], upperRegionBraggPinW, lowerRegionBraggPinW, upperRegion, lowerRegion)

lowZBraggRegion = upperRegion-lowerRegion-feedlineRegion

#-----------------------END 1ST LOW Z, BEGIN 1ST HIGH Z PERIOD---------------------------------------------------------------------------------------------#

#1st high Z region
firstHighZBegin = thirdLowZBendEnd + (lowZStraightLength/2*ey)
firstHighZBendBegin = firstHighZBegin + highZStraightLength/2*ey
firstHighZBendEnd = firstHighZBendBegin + 2*braggBendRadius*ex
highZNegW = 10
cpwStraight(layout, TOP, workingLayer, [firstHighZBegin, firstHighZBendBegin], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)

bendPoints = [firstHighZBendBegin, firstHighZBendBegin + braggBendRadius*ey, firstHighZBendEnd + braggBendRadius*ey, firstHighZBendEnd]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, highZNegW, braggBendRadius, upperRegion, lowerRegion)

secondHighZBendBegin = firstHighZBendEnd - highZStraightLength*ey
cpwStraight(layout, TOP, workingLayer, [firstHighZBendEnd, secondHighZBendBegin], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)

secondHighZBendEnd = secondHighZBendBegin + 2*braggBendRadius*ex
bendPoints = [secondHighZBendBegin, secondHighZBendBegin - braggBendRadius*ey, secondHighZBendEnd - braggBendRadius*ey, secondHighZBendEnd]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, highZNegW, braggBendRadius, upperRegion, lowerRegion)

firstHighZRegionEnd = secondHighZBendEnd + highZStraightLength/2*ey
cpwStraight(layout, TOP, workingLayer, [secondHighZBendEnd, firstHighZRegionEnd], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)

highZBraggRegion = upperRegion-lowerRegion-feedlineRegion-lowZBraggRegion

#----------------------------------------------------end of Bragg - cavity feedline--------------------------------------------------------------#
highZHoriz = 911
highZVert = 4320
highZAdjust = 2413+25
highZEndVert = 500

cavityFeedBegin = feedlineEndPoint - (20*ey) + 36*braggBendRadius*ex
cavityFeedBendBegin = cavityFeedBegin - lowZStraightLength/2*ey
cavityFeedBendEnd = cavityFeedBendBegin + 2*braggBendRadius*ex
bendPoints = [cavityFeedBendBegin, cavityFeedBendBegin - braggBendRadius*ey, cavityFeedBendEnd - braggBendRadius*ey, cavityFeedBendEnd]
cpwStraight(layout, TOP, workingLayer, [cavityFeedBegin, cavityFeedBendBegin], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, highZNegW, braggBendRadius, upperRegion, lowerRegion)
cavityFeedStraightEnd = cavityFeedBendEnd + (highZVert + highZAdjust)*ey
cpwStraight(layout, TOP, workingLayer, [cavityFeedBendEnd, cavityFeedStraightEnd], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)

cavityFeedFirstBendEnd = cavityFeedStraightEnd - braggBendRadius*ex + braggBendRadius*ey
bendPoints = [cavityFeedStraightEnd, cavityFeedStraightEnd + braggBendRadius*ey, cavityFeedFirstBendEnd]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, highZNegW, braggBendRadius, upperRegion, lowerRegion)

secondBendCavityBegin = cavityFeedFirstBendEnd - highZHoriz*ex
secondBendCavityEnd = secondBendCavityBegin - braggBendRadius*ex + braggBendRadius*ey
bendPoints = [secondBendCavityBegin, secondBendCavityBegin - braggBendRadius*ex, secondBendCavityEnd]
cpwStraight(layout, TOP, workingLayer, [cavityFeedFirstBendEnd, secondBendCavityBegin], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, highZNegW, braggBendRadius, upperRegion, lowerRegion)

vertStraightEnd = secondBendCavityEnd + highZEndVert*ey
cpwStraight(layout, TOP, workingLayer, [secondBendCavityEnd, vertStraightEnd], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)

thirdBendEnd = vertStraightEnd + braggBendRadius*ey - braggBendRadius*ex
bendPoints = [vertStraightEnd, vertStraightEnd + braggBendRadius*ey, thirdBendEnd]
cpwBend(layout, TOP, workingLayer, bendPoints, upperRegionBraggPinW, highZNegW, braggBendRadius, upperRegion, lowerRegion)

cavityFeedlineEnd = thirdBendEnd - highZEndVert*ex
cpwStraight(layout, TOP, workingLayer, [thirdBendEnd, cavityFeedlineEnd], upperRegionBraggPinW, highZNegW, upperRegion, lowerRegion)

#cavity to Bragg taper
taperPoints = [cavityFeedlineEnd, cavityFeedlineEnd - 5*ex]
upperTaperWidths = [upperRegionBraggPinW, 11]
lowerTaperWidths = [highZNegW, 3]
cpwStraight(layout, TOP, workingLayer, taperPoints, upperTaperWidths, lowerTaperWidths, upperRegion, lowerRegion)

cavityFeedlineRegion = upperRegion-lowerRegion-feedlineRegion-lowZBraggRegion-highZBraggRegion

#--------------------CAVITY---------------------------------------------------------------------------------------------------------------------------------#
La = 804    #from KRoh, figure out why
Lv = 300
cavityStraightLength = 2350
Lh = 2150

cavityIntroEnd = cavityFeedlineEnd - 5*ex - La*ex
upperPinW = 11
cPinW = 3

layout_path(TOP, port1Layer, [cavityFeedlineEnd - 5*ex - 10*ey, cavityFeedlineEnd - 5*ex + 10*ey], 0)

cpwStraight(layout, TOP, workingLayer, [cavityFeedlineEnd-5*ex, cavityIntroEnd], upperPinW, cPinW, upperRegion, lowerRegion)

bendPoints = [cavityIntroEnd, cavityIntroEnd - braggBendRadius*ex, cavityIntroEnd - braggBendRadius*ex - braggBendRadius*ey]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

cavityVertEnd = cavityIntroEnd - braggBendRadius*ex - braggBendRadius*ey - Lv*ey
cpwBend(layout, TOP, workingLayer, [cavityIntroEnd - braggBendRadius*ex - braggBendRadius*ey, cavityVertEnd], upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

bendPoints = [cavityVertEnd, cavityVertEnd-braggBendRadius*ey, cavityVertEnd-braggBendRadius*ey-braggBendRadius*ex]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

cavityStraightBegin = cavityVertEnd - braggBendRadius*ey-braggBendRadius*ex
cavityStraightEnd = cavityStraightBegin - cavityStraightLength*ex
cpwStraight(layout, TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW, cPinW, upperRegion, lowerRegion)

bendPoints = [cavityStraightEnd, cavityStraightEnd - braggBendRadius*ex, cavityStraightEnd - braggBendRadius*ex + braggBendRadius*ey]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

cavityStraightBegin = cavityStraightEnd - braggBendRadius*ex + braggBendRadius*ey
cavityStraightEnd = cavityStraightBegin + Lv*ey
cpwStraight(layout, TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW, cPinW, upperRegion, lowerRegion)

bendPoints = [cavityStraightEnd, cavityStraightEnd + braggBendRadius*ey, cavityStraightEnd + braggBendRadius*ex + braggBendRadius*ey]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

cavityHorizBegin = cavityStraightEnd + braggBendRadius*ex + braggBendRadius*ey
cavityHorizEnd = cavityHorizBegin + Lh*ex
cpwStraight(layout, TOP, workingLayer, [cavityHorizBegin, cavityHorizEnd], upperPinW, cPinW, upperRegion, lowerRegion)

cavityStraightBegin = cavityHorizEnd + braggBendRadius*ex + braggBendRadius*ey
bendPoints = [cavityHorizEnd, cavityHorizEnd + braggBendRadius*ex, cavityStraightBegin]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

cavityStraightEnd = cavityStraightBegin + Lv*ey
cpwStraight(layout, TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW, cPinW, upperRegion, lowerRegion)

cavityStraightBegin = cavityStraightEnd + braggBendRadius*ey - braggBendRadius*ex
bendPoints = [cavityStraightEnd, cavityStraightEnd + braggBendRadius*ey, cavityStraightBegin]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

cavityStraightEnd = cavityStraightBegin - cavityStraightLength*ex
cpwStraight(layout, TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW, cPinW, upperRegion, lowerRegion)

#--------THOMAS - this is where the bend posing a problem is --------------------------------------------------#
cavityStraightBegin = cavityStraightEnd - braggBendRadius*ex - braggBendRadius*ey
bendPoints = [cavityStraightEnd, cavityStraightEnd - braggBendRadius*ex, cavityStraightBegin]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)
#--------------------end---------------------------------------------------------------------------------------#

cavityStraightEnd = cavityStraightBegin - Lv*ey + 1.5*ey
cpwStraight(layout, TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW, cPinW, upperRegion, lowerRegion)

cavityStraightBegin = cavityStraightEnd - braggBendRadius*ex - braggBendRadius*ey
bendPoints = [cavityStraightEnd, cavityStraightEnd - braggBendRadius*ey, cavityStraightBegin]
cpwBend(layout, TOP, workingLayer, bendPoints, upperPinW, cPinW, braggBendRadius, upperRegion, lowerRegion)

#cheesing it
cavityStraightEnd = 2911*ex + 1.5*ey

layout_path(TOP, sourceLayer, [cavityStraightEnd -10*ex - 75 * ey, cavityStraightEnd -10*ex + 75 * ey], 0)
layout_path(TOP, port2Layer, [cavityStraightEnd - 10*ey, cavityStraightEnd + 10*ey], 0)

cpwStraight(layout, TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW, cPinW, upperRegion, lowerRegion)

cavityRegion = upperRegion-lowerRegion-feedlineRegion-lowZBraggRegion-highZBraggRegion-cavityFeedlineRegion

#-----TRANSFORM 1ST HIGH Z, LOW Z TO NEW POSITIONS----------------------------------------------------------------------------------------------------------#
TOP.shapes(outputLayer).insert(feedlineRegion)
tFeed = pya.DCplxTrans(1, 180, False, 11000000, 0)
translatedFeed = feedlineRegion.transformed(tFeed)
TOP.shapes(outputLayer).insert(translatedFeed)

TOP.shapes(outputLayer).insert(lowZBraggRegion)
tLow1 = pya.DCplxTrans(1, 0, True, 10000*braggBendRadius, -2000*deltaY)
translatedLow1 = lowZBraggRegion.transformed(tLow1)
TOP.shapes(outputLayer).insert(translatedLow1)
tLow2 = pya.DCplxTrans(1, 0, True, 30000*braggBendRadius, -2000*deltaY)
translatedLow2 = lowZBraggRegion.transformed(tLow2)
tLow3 = pya.DCplxTrans(1, 0, False, 20000*braggBendRadius, 0)
translatedLow3 = lowZBraggRegion.transformed(tLow3)
TOP.shapes(outputLayer).insert(translatedLow3)
TOP.shapes(outputLayer).insert(translatedLow2)

TOP.shapes(outputLayer).insert(highZBraggRegion)
tHigh = pya.DCplxTrans(1, 0, True, 10000*braggBendRadius, -2000*deltaY)
translatedHigh = highZBraggRegion.transformed(tHigh)
tHigh2 = pya.DCplxTrans(1, 0, False, 20000*braggBendRadius, 0)
translatedHigh2 = highZBraggRegion.transformed(tHigh2)
TOP.shapes(outputLayer).insert(translatedHigh)
TOP.shapes(outputLayer).insert(translatedHigh2)

#create/transform Bragg region, why the hell isn't this working
braggRegion = lowZBraggRegion + highZBraggRegion + translatedLow1 + translatedLow2 + translatedLow3 + translatedHigh + translatedHigh2 
tBragg = pya.DCplxTrans(2000*braggBendRadius, 2000*deltaY)
translatedBragg = braggRegion.transformed(tBragg)
TOP.shapes(outputLayer).insert(translatedBragg)

TOP.shapes(outputLayer).insert(cavityFeedlineRegion)
tCavity = pya.DCplxTrans(1, 180, False, 11000000-10000, 0)
translatedCavity = cavityFeedlineRegion.transformed(tCavity)
TOP.shapes(outputLayer).insert(translatedCavity)

TOP.shapes(outputLayer).insert(cavityRegion)

print(deltaY)
print(2*deltaY)

layout.clear_layer(workingLayer)

layout.write('project_debug.gds')
del layout, TOP
