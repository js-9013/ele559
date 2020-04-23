import klayout.db as pya
from zeropdk.layout import layout_box
from zeropdk.layout import layout_waveguide
from zeropdk.layout import bezier_optimal
from zeropdk.layout.waveguide_rounding import layout_waveguide_from_points
import numpy as np

layout = pya.Layout()
layout.dbu = 1
TOP = layout.create_cell("TOP")

workingLayer =  pya.LayerInfo(4,0)   
chipBorder = pya.LayerInfo(7,0)
maskBorder = pya.LayerInfo(10,0)
outputLayer = pya.LayerInfo(1,0)
sourceLayer = pya.LayerInfo(3,0)
portsLayer = pya.LayerInfo(2,0)

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
upperRegion.insert(layout_box(TOP, workingLayer, -(upperWGBondPadHeight/2)*ey, (upperWGBondPadLength)*ex + (upperWGBondPadHeight/2)*ey, ex))
lowerRegion.insert(layout_box(TOP, workingLayer, -(lowerWGBondPadHeight/2)*ey, (lowerWGBondPadLength)*ex + (lowerWGBondPadHeight/2)*ey, ex))
deltaY = 0
#-------------------------------------BEGIN FEED LINE-------------------------------------------------------------------------------------------#

#bond pad tapers
taperPoints = [300*ex, 425*ex, 550*ex]
upperTaperWidths = [450, 305, 160]
lowerTaperWidths = [250, 175, 100]
upperRegion.insert(layout_waveguide(TOP, workingLayer, taperPoints, upperTaperWidths))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, taperPoints, lowerTaperWidths))

#CPW straight to first bend
upperRegion.insert(layout_waveguide(TOP, workingLayer, [550*ex, (550 + introFeedlineLength)*ex], upperRegionFeedlineWidth))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [550*ex, (550 + introFeedlineLength)*ex], lowerRegionFeedlineWidth))

#CPW bend on feedline
arcCoord1 = (550+introFeedlineLength) * ex
arcCoord2 = arcCoord1 - 2*feedlineBendRadius*ey
bendPoints = [arcCoord1, arcCoord1 + feedlineBendRadius*ex, arcCoord2 + feedlineBendRadius*ex, arcCoord2] 
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionFeedlineWidth, feedlineBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, lowerRegionFeedlineWidth, feedlineBendRadius))
deltaY = deltaY + 2*feedlineBendRadius

#CPW straight after 1st bend
upperRegion.insert(layout_waveguide(TOP, workingLayer, [arcCoord2, arcCoord2-55*ex], upperRegionFeedlineWidth))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [arcCoord2, arcCoord2-55*ex], lowerRegionFeedlineWidth))

#2nd CPW bend
bendEndPoint = arcCoord2-55*ex-(feedlineBendRadius*ex)-feedlineBendRadius*ey
bendPoints = [arcCoord2-55*ex, arcCoord2-55*ex-(feedlineBendRadius*ex), bendEndPoint]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionFeedlineWidth, feedlineBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, lowerRegionFeedlineWidth, feedlineBendRadius))
deltaY = deltaY + feedlineBendRadius

#end feedline with straight
upperRegion.insert(layout_waveguide(TOP, workingLayer, [bendEndPoint, bendEndPoint-4500*ey], upperRegionFeedlineWidth, feedlineBendRadius))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [bendEndPoint, bendEndPoint-4500*ey], lowerRegionFeedlineWidth, feedlineBendRadius))
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
upperRegion.insert(layout_waveguide(TOP, workingLayer, taperPoints, upperTaperWidths))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, taperPoints, lowerTaperWidths))
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
upperRegion.insert(layout_waveguide(TOP, workingLayer, [feedlineEndPoint - 20 * ey, feedlineEndPoint - (20*ey) - (lowZStraightLength/2*ey)], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [feedlineEndPoint - 20*ey, feedlineEndPoint - (20*ey) - (lowZStraightLength/2*ey)], lowerRegionBraggPinW))

#1st low Z bend
introLowZEnd = introLowZBegin + 2*braggBendRadius*ex
bendPoints = [introLowZBegin, introLowZBegin - braggBendRadius*ey, introLowZEnd - braggBendRadius*ey, introLowZEnd]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, lowerRegionBraggPinW, braggBendRadius))
upperRegion.insert(layout_waveguide(TOP, workingLayer, [introLowZEnd, introLowZEnd + lowZStraightLength*ey], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [introLowZEnd, introLowZEnd + lowZStraightLength*ey], lowerRegionBraggPinW))

#2nd low Z bend
secondLowZBendBegin = introLowZEnd + lowZStraightLength * ey
secondLowZBendEnd = secondLowZBendBegin + 2*braggBendRadius * ex
bendPoints = [secondLowZBendBegin, secondLowZBendBegin + braggBendRadius*ey, secondLowZBendEnd+braggBendRadius*ey, secondLowZBendEnd]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, lowerRegionBraggPinW, braggBendRadius))
upperRegion.insert(layout_waveguide(TOP, workingLayer, [secondLowZBendEnd, secondLowZBendEnd - lowZStraightLength*ey], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [secondLowZBendEnd, secondLowZBendEnd - lowZStraightLength*ey], lowerRegionBraggPinW))

#3rd low Z bend
thirdLowZBendBegin = introLowZEnd + 2*braggBendRadius*ex
thirdLowZBendEnd = thirdLowZBendBegin + 2*braggBendRadius*ex
bendPoints = [thirdLowZBendBegin, thirdLowZBendBegin - braggBendRadius*ey, thirdLowZBendEnd - braggBendRadius*ey, thirdLowZBendEnd]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, lowerRegionBraggPinW, braggBendRadius))
upperRegion.insert(layout_waveguide(TOP, workingLayer, [thirdLowZBendEnd, thirdLowZBendEnd + (lowZStraightLength/2*ey)], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [thirdLowZBendEnd, thirdLowZBendEnd + (lowZStraightLength/2*ey)], lowerRegionBraggPinW))

lowZBraggRegion = upperRegion-lowerRegion-feedlineRegion

#-----------------------END 1ST LOW Z, BEGIN 1ST HIGH Z PERIOD---------------------------------------------------------------------------------------------#

#1st high Z region
firstHighZBegin = thirdLowZBendEnd + (lowZStraightLength/2*ey)
firstHighZBendBegin = firstHighZBegin + highZStraightLength/2*ey
firstHighZBendEnd = firstHighZBendBegin + 2*braggBendRadius*ex
highZNegW = 10
upperRegion.insert(layout_waveguide(TOP, workingLayer, [firstHighZBegin, firstHighZBendBegin], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [firstHighZBegin, firstHighZBendBegin], highZNegW))
bendPoints = [firstHighZBendBegin, firstHighZBendBegin + braggBendRadius*ey, firstHighZBendEnd + braggBendRadius*ey, firstHighZBendEnd]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, highZNegW, braggBendRadius))
secondHighZBendBegin = firstHighZBendEnd - highZStraightLength*ey
upperRegion.insert(layout_waveguide(TOP, workingLayer, [firstHighZBendEnd, secondHighZBendBegin], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [firstHighZBendEnd, secondHighZBendBegin], highZNegW))
secondHighZBendEnd = secondHighZBendBegin + 2*braggBendRadius*ex
bendPoints = [secondHighZBendBegin, secondHighZBendBegin - braggBendRadius*ey, secondHighZBendEnd - braggBendRadius*ey, secondHighZBendEnd]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, highZNegW, braggBendRadius))
firstHighZRegionEnd = secondHighZBendEnd + highZStraightLength/2*ey
upperRegion.insert(layout_waveguide(TOP, workingLayer, [secondHighZBendEnd, firstHighZRegionEnd], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [secondHighZBendEnd, firstHighZRegionEnd], highZNegW))

highZBraggRegion = upperRegion-lowerRegion-feedlineRegion-lowZBraggRegion

#end of Bragg - cavity feedline
highZHoriz = 911
highZVert = 4320
highZAdjust = 2413+25
highZEndVert = 500

cavityFeedBegin = feedlineEndPoint - (20*ey) + 36*braggBendRadius*ex
cavityFeedBendBegin = cavityFeedBegin - lowZStraightLength/2*ey
cavityFeedBendEnd = cavityFeedBendBegin + 2*braggBendRadius*ex
bendPoints = [cavityFeedBendBegin, cavityFeedBendBegin - braggBendRadius*ey, cavityFeedBendEnd - braggBendRadius*ey, cavityFeedBendEnd]
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedBegin, cavityFeedBendBegin], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedBegin, cavityFeedBendBegin], highZNegW))
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, highZNegW, braggBendRadius))
cavityFeedStraightEnd = cavityFeedBendEnd + (highZVert + highZAdjust)*ey
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedBendEnd, cavityFeedStraightEnd], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedBendEnd, cavityFeedStraightEnd], highZNegW))

cavityFeedFirstBendEnd = cavityFeedStraightEnd - braggBendRadius*ex + braggBendRadius*ey
bendPoints = [cavityFeedStraightEnd, cavityFeedStraightEnd + braggBendRadius*ey, cavityFeedFirstBendEnd]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, highZNegW, braggBendRadius))

secondBendCavityBegin = cavityFeedFirstBendEnd - highZHoriz*ex
secondBendCavityEnd = secondBendCavityBegin - braggBendRadius*ex + braggBendRadius*ey
bendPoints = [secondBendCavityBegin, secondBendCavityBegin - braggBendRadius*ex, secondBendCavityEnd]
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedFirstBendEnd, secondBendCavityBegin], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedFirstBendEnd, secondBendCavityBegin], highZNegW))
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, highZNegW, braggBendRadius))

vertStraightEnd = secondBendCavityEnd + highZEndVert*ey
upperRegion.insert(layout_waveguide(TOP, workingLayer, [secondBendCavityEnd, vertStraightEnd], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [secondBendCavityEnd, vertStraightEnd], highZNegW))

thirdBendEnd = vertStraightEnd + braggBendRadius*ey - braggBendRadius*ex
bendPoints = [vertStraightEnd, vertStraightEnd + braggBendRadius*ey, thirdBendEnd]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionBraggPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, highZNegW, braggBendRadius))

cavityFeedlineEnd = thirdBendEnd - highZEndVert*ex
upperRegion.insert(layout_waveguide(TOP, workingLayer, [thirdBendEnd, cavityFeedlineEnd], upperRegionBraggPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [thirdBendEnd, cavityFeedlineEnd], highZNegW))

#cavity to Bragg taper
taperPoints = [cavityFeedlineEnd, cavityFeedlineEnd - 5*ex]
upperTaperWidths = [upperRegionBraggPinW, 11]
lowerTaperWidths = [highZNegW, 3]
upperRegion.insert(layout_waveguide(TOP, workingLayer, taperPoints, upperTaperWidths))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, taperPoints, lowerTaperWidths))

cavityFeedlineRegion = upperRegion-lowerRegion-feedlineRegion-lowZBraggRegion-highZBraggRegion

#--------------------CAVITY---------------------------------------------------------------------------------------------------------------------------------#
La = 804    #from KRoh, figure out why
Lv = 300
cavityStraightLength = 2350
Lh = 2150

cavityIntroEnd = cavityFeedlineEnd - 5*ex - La*ex
upperPinW = 11
cPinW = 3

layout_path(TOP, portsLayer, [cavityFeedlineEnd - 5*ex - 10*ey, cavityFeedlineEnd - 5*ex + 10*ey], 0)

upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedlineEnd - 5*ex, cavityIntroEnd], upperPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityFeedlineEnd - 5*ex, cavityIntroEnd], cPinW))
bendPoints = [cavityIntroEnd, cavityIntroEnd - braggBendRadius*ex, cavityIntroEnd - braggBendRadius*ex - braggBendRadius*ey]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))
cavityVertEnd = cavityIntroEnd - braggBendRadius*ex - braggBendRadius*ey - Lv*ey
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, [cavityIntroEnd - braggBendRadius*ex - braggBendRadius*ey, cavityVertEnd], upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, [cavityIntroEnd - braggBendRadius*ex - braggBendRadius*ey, cavityVertEnd], cPinW, braggBendRadius))
bendPoints = [cavityVertEnd, cavityVertEnd-braggBendRadius*ey, cavityVertEnd-braggBendRadius*ey-braggBendRadius*ex]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))
cavityStraightBegin = cavityVertEnd - braggBendRadius*ey-braggBendRadius*ex
cavityStraightEnd = cavityStraightBegin - cavityStraightLength*ex
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], cPinW))
bendPoints = [cavityStraightEnd, cavityStraightEnd - braggBendRadius*ex, cavityStraightEnd - braggBendRadius*ex + braggBendRadius*ey]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))
cavityStraightBegin = cavityStraightEnd - braggBendRadius*ex + braggBendRadius*ey
cavityStraightEnd = cavityStraightBegin + Lv*ey
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], cPinW))
bendPoints = [cavityStraightEnd, cavityStraightEnd + braggBendRadius*ey, cavityStraightEnd + braggBendRadius*ex + braggBendRadius*ey]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))

cavityHorizBegin = cavityStraightEnd + braggBendRadius*ex + braggBendRadius*ey
cavityHorizEnd = cavityHorizBegin + Lh*ex
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityHorizBegin, cavityHorizEnd], upperPinW)) 
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityHorizBegin, cavityHorizEnd], cPinW))

cavityStraightBegin = cavityHorizEnd + braggBendRadius*ex + braggBendRadius*ey
bendPoints = [cavityHorizEnd, cavityHorizEnd + braggBendRadius*ex, cavityStraightBegin]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))

cavityStraightEnd = cavityStraightBegin + Lv*ey
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], cPinW))

cavityStraightBegin = cavityStraightEnd + braggBendRadius*ey - braggBendRadius*ex
bendPoints = [cavityStraightEnd, cavityStraightEnd + braggBendRadius*ey, cavityStraightBegin]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))

cavityStraightEnd = cavityStraightBegin - cavityStraightLength*ex
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], cPinW))

cavityStraightBegin = cavityStraightEnd - braggBendRadius*ex - braggBendRadius*ey
bendPoints = [cavityStraightEnd, cavityStraightEnd - braggBendRadius*ex, cavityStraightBegin]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))

cavityStraightEnd = cavityStraightBegin - Lv*ey + 1.5*ey
upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], cPinW))

cavityStraightBegin = cavityStraightEnd - braggBendRadius*ex - braggBendRadius*ey
bendPoints = [cavityStraightEnd, cavityStraightEnd - braggBendRadius*ey, cavityStraightBegin]
upperRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperPinW, braggBendRadius))
lowerRegion.insert(layout_waveguide_from_points(TOP, workingLayer, bendPoints, cPinW, braggBendRadius))

#cheesing it
cavityStraightEnd = 2911*ex + 1.5*ey

layout_path(TOP, sourceLayer, [cavityStraightEnd -10*ex - 10 * ey, cavityStraightEnd -10*ex + 10 * ey], 0)
layout_path(TOP, portsLayer, [cavityStraightEnd - 10*ey, cavityStraightEnd + 10*ey], 0)

upperRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], upperPinW))
lowerRegion.insert(layout_waveguide(TOP, workingLayer, [cavityStraightBegin, cavityStraightEnd], cPinW))

cavityRegion = upperRegion-lowerRegion-feedlineRegion-lowZBraggRegion-highZBraggRegion-cavityFeedlineRegion

#-----TRANSFORM 1ST HIGH Z, LOW Z TO NEW POSITIONS----------------------------------------------------------------------------------------------------------#
TOP.shapes(outputLayer).insert(feedlineRegion)
tFeed = pya.DCplxTrans(1, 180, False, 11000-10, 0)
translatedFeed = feedlineRegion.transformed(tFeed)
TOP.shapes(outputLayer).insert(translatedFeed)

TOP.shapes(outputLayer).insert(lowZBraggRegion)
tLow1 = pya.DCplxTrans(1, 0, 'true', 10*braggBendRadius, -2*deltaY)
translatedLow1 = lowZBraggRegion.transformed(tLow1)
tLow2 = pya.DCplxTrans(1, 0, 'false', 30*braggBendRadius, -2*deltaY)
translatedLow2 = lowZBraggRegion.transformed(tLow2)
tLow3 = pya.DCplxTrans(1, 0, 'false', 10*braggBendRadius, -2*deltaY)
translatedLow3 = translatedLow1.transformed(tLow3)
TOP.shapes(outputLayer).insert(translatedLow1)
TOP.shapes(outputLayer).insert(translatedLow2)
TOP.shapes(outputLayer).insert(translatedLow3)

TOP.shapes(outputLayer).insert(highZBraggRegion)
tHigh = pya.DCplxTrans(1,0, 'true', 10*braggBendRadius, -2*deltaY)
translatedHigh = highZBraggRegion.transformed(tHigh)
tHigh2 = pya.DCplxTrans(1, 0, 'true', 10*braggBendRadius, -2*deltaY)
translatedHigh2 = translatedHigh.transformed(tHigh2)
TOP.shapes(outputLayer).insert(translatedHigh)
TOP.shapes(outputLayer).insert(translatedHigh2)

#create/transform Bragg region, why the hell isn't this working
braggRegion = lowZBraggRegion + highZBraggRegion + translatedLow1 + translatedLow2 + translatedLow3 + translatedHigh + translatedHigh2
tBragg = pya.DCplxTrans(2*braggBendRadius, 2*deltaY)
translatedBragg = braggRegion.transformed(tBragg)
TOP.shapes(outputLayer).insert(translatedBragg)

TOP.shapes(outputLayer).insert(cavityFeedlineRegion)
tCavity = pya.DCplxTrans(1, 180, False, 11000-10, 0)
translatedCavity = cavityFeedlineRegion.transformed(tCavity)
TOP.shapes(outputLayer).insert(translatedCavity)

TOP.shapes(outputLayer).insert(cavityRegion)

print(deltaY)
print(2*deltaY)

layout.write('project.gds')
del layout, TOP
