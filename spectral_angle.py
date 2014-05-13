# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2014-05-06
        copyright            : (C) 2014 by CS Systèmes d'Information
        email                : alexia.mondot@c-s.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 """

import os

from qgis.gui import QgsRubberBand, QgsMapToolPan
from qgis.core import QGis, QgsPoint, QgsRaster

from PyQt4 import QtCore, QtGui

from ptmaptool import ProfiletoolMapTool


class SpectralAngle():
    
    def __init__(self, iface, layer):
        self.iface = iface
        self.layer = layer
        self.canvas = self.iface.mapCanvas()
        
        self.tool = ProfiletoolMapTool(self.iface.mapCanvas())        #the mouselistener
        print "self.tool", self.tool
        self.pointstoDraw = None    #Polyline in mapcanvas CRS analysed
        self.maptool = self.canvas.mapTool()
        self.get_point_for_angles()


    def angles(self, x, y):
        if self.layer :
            ident = self.layer.dataProvider().identify(QgsPoint(x, y), QgsRaster.IdentifyFormatValue )
            print ident
            if ident is not None :
                attr = ident.results()
                print attr
                if len(attr) == self.layer.bandCount():
                    formula = "\"acos("
                    num = []
                    denom = []
                    fact = []
                    #acos((im1b1*1269+im1b2*1060+im1b3*974+im1b4*1576)/
                    #(sqrt((1269*1269+1060*1060+974*974+1576*1576)*
                    #(im1b1*im1b1+im1b2*im1b2+im1b3*im1b3+im1b4*im1b4))))
                    for index in range( 1,self.layer.bandCount()+1 ):
                        current_band = "im1b" + str(index)
                        band_value = attr[index]
                        num.append( current_band + "*" + str(band_value)  )
                        denom.append(str(band_value) + "*" + str(band_value) )
                        fact.append(current_band + "*" + current_band)
                    
                    formula += "(" + "+".join(num) + ")/"
                    formula += "(sqrt("
                    formula += "(" + "+".join(denom) + ")*"
                    formula += "(" + "+".join(fact) + ")"
                    formula += "))"
                    formula += ")\""
                    
                    print "num", num
                    print "denom", denom
                    print "fact", fact
                    print "formula", formula
                    
                    
                    image_in = self.layer.source()
                    output_filename = os.path.join( self.working_directory, os.path.basename(os.path.splitext(image_in)[0]) + "_angles" + str(x) + "_" + str(y) + os.path.splitext(image_in)[1])
                    OTBApplications.bandmath_cli( [image_in], formula, output_filename )
                    rlayer = manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_angles" + str(x) + "_" + str(y), self.iface )
                    manage_QGIS.contrastForRasters( rlayer, 0, 0.5)
        self.tool.deactivate()
        self.deactivate()
        self.canvas.setMapTool(self.maptool) 
                    
                    
                    
                    
    
    def get_point_for_angles(self):
        print "get point for angles"
        QtCore.QObject.connect(self.tool, QtCore.SIGNAL("canvas_clicked"), self.rightClicked)
        
        #init the mouse listener comportement and save the classic to restore it on quit
        self.canvas.setMapTool(self.tool)
        
        print "listener set"
        
        #init the temp layer where the polyline is draw
        self.polygon = False
        self.rubberband = QgsRubberBand(self.canvas, self.polygon)
        self.rubberband.setWidth(2)
        self.rubberband.setColor(QtGui.QColor(QtCore.Qt.red))
        #init the table where is saved the poyline
        self.pointstoDraw = []
        self.pointstoCal = []
        
    def deactivate(self):        #enable clean exit of the plugin
        QtCore.QObject.disconnect(self.tool, QtCore.SIGNAL("canvas_clicked"), self.rightClicked)
        self.rubberband.reset(self.polygon)
        
        
    def rightClicked(self,position):    #used to quit the current action
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
        newPoints = [[mapPos.x(), mapPos.y()]]
        #if newPoints == self.lastClicked: return # sometimes a strange "double click" is given

        self.rubberband.reset(self.polygon)
        self.rubberband.reset(QGis.Point)
        self.rubberband.addPoint(QgsPoint(mapPos.x(),mapPos.y()))
        #create new vlayer ???
        self.angles(mapPos.x(),mapPos.y())
 