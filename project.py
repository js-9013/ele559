import klayout.db as pya
from zeropdk.layout import layout_box
from zeropdk.layout import layout_waveguide
from zeropdk.layout.waveguide_rounding import layout_waveguide_from_points

layout = pya.Layout()
layout.dbu = 1
TOP = layout.create_cell("TOP")

workingLayer =  pya.LayerInfo(4,0)   
chipBorder = pya.LayerInfo(2,0)
maskBorder = pya.LayerInfo(3,0)
outputLayer = pya.LayerInfo(1,0)    

ex = pya.DVector(1,0)
ey = pya.DVector(0,1)

upperRegion = pya.Region()
lowerRegion = pya.Region()

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
arcXCoord = 550+introFeedlineLength+feedlineBendRadius
bendPoints = [arcXCoord*ex, arcXCoord*ex - feedlineBendRadius*ey, arcXCoord*ex - 2*feedlineBendRadius*ey] 
(layout_waveguide_from_points(TOP, workingLayer, bendPoints, upperRegionFeedlineWidth, feedlineBendRadius))
(layout_waveguide_from_points(TOP, workingLayer, bendPoints, lowerRegionFeedlineWidth, feedlineBendRadius))   
        
result = upperRegion - lowerRegion
TOP.shapes(outputLayer).insert(result)

layout.write('project.gds')
del layout, TOP


