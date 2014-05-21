# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2014-05-06
        copyright            : (C) 2014 by CNES
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

import terre_image_processing


class SpectralAngle():
    
    def __init__(self, iface, working_dir, layer):
        self.iface = iface
        self.working_directory = working_dir
        if layer :
            self.layer = layer
        self.canvas = self.iface.mapCanvas()
        
        self.tool = ProfiletoolMapTool(self.iface.mapCanvas())        #the mouselistener
        print "self.tool", self.tool
        self.pointstoDraw = None    #Polyline in mapcanvas CRS analysed
        self.maptool = self.canvas.mapTool()
        #self.get_point_for_angles()


    def angles(self, x, y):
        if self.layer :
            terre_image_processing.angles(self.layer, self.working_directory, self.iface, x, y)
        self.tool.deactivate()
        self.deactivate()
        self.canvas.setMapTool(self.maptool)
                    
                    
                    
    
    def get_point_for_angles(self, layer):
        self.layer = layer
        print "get point for angles"
        QtCore.QObject.connect(self.tool, QtCore.SIGNAL("canvas_clicked"), self.rightClicked)
        
        #init the mouse listener comportement and save the classic to restore it on quit
        self.canvas.setMapTool(self.tool)
        
        print "listener set"
        
        #init the temp layer where the polyline is draw
        self.polygon = False
        self.rubberband = QgsRubberBand(self.canvas, self.polygon)
        self.rubberband.setWidth(10)
        self.rubberband.setColor(QtGui.QColor(QtCore.Qt.yellow))
        #init the table where is saved the poyline
        self.pointstoDraw = []
        self.pointstoCal = []
        
    def deactivate(self):        #enable clean exit of the plugin
        QtCore.QObject.disconnect(self.tool, QtCore.SIGNAL("canvas_clicked"), self.rightClicked)
        #self.rubberband.reset(self.polygon)
        
        
    def rightClicked(self,position):    #used to quit the current action
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"],position["y"])
        newPoints = [[mapPos.x(), mapPos.y()]]
        #if newPoints == self.lastClicked: return # sometimes a strange "double click" is given

        self.rubberband.reset(self.polygon)
        self.rubberband.reset(QGis.Point)
        self.rubberband.addPoint(QgsPoint(mapPos.x(),mapPos.y()))
        #create new vlayer ???
        self.angles(mapPos.x(),mapPos.y())
        self.toolPan = QgsMapToolPan( self.canvas )
        self.canvas.setMapTool( self.toolPan )
 