# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducationDialog
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-04-30
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

from PyQt4 import QtCore, QtGui
from ui_qgiseducation import Ui_QGISEducation
# create the dialog for zoom to point
import OTBApplications
from qgis.gui import QgsRubberBand, QgsMapToolPan

from qgis.core import QGis, QgsPoint, QgsRaster


from working_layer import WorkingLayer
import terre_image_processing
import terre_image_utils
import manage_QGIS


import datetime
import os
from ptmaptool import ProfiletoolMapTool
from valuewidget import ValueWidget

from spectral_angle import SpectralAngle

class QGISEducationWidget(QtGui.QWidget, Ui_QGISEducation):
    def __init__(self, iface):
        
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
                
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.setupUi_extra()
        
        self.working_directory, _ = terre_image_utils.fill_default_directory()
        self.value_tool = ValueWidget( self.iface, self )
        
        self.tool = ProfiletoolMapTool(self.iface.mapCanvas())        #the mouselistener
        print "self.tool", self.tool
        self.pointstoDraw = None    #Polyline in mapcanvas CRS analysed
        self.maptool = self.canvas.mapTool()
        self.get_point_for_angles()
        self.layer = None
     
    def setupUi_extra(self):
        """
        Initialize the interface
        """
        self.pushButton_working_layer.hide()
        self.label.hide()
        self.label_working_layer.hide()
        self.groupBox.hide()
        self.pushButton_brightness.clicked.connect(self.brightness)
        self.pushButton_ndti.clicked.connect(self.ndti)
        self.pushButton_ndvi.clicked.connect(self.ndvi)
        self.pushButton_working_layer.clicked.connect(self.working_layer)
        self.pushButton_angle.clicked.connect(self.spectral_angles)
        
        
    def brightness(self):
        if not self.layer :
            print "Aucune layer selectionnée"
        else :
            terre_image_processing.brightness(self.layer, self.working_directory, self.iface)
               
    
    def ndvi(self):
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            terre_image_processing.ndti(self.layer, self.working_directory, self.iface)
                
                 
    def ndti(self):
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            terre_image_processing.ndti(self.layer, self.working_directory, self.iface)

        
        
    def working_layer(self):
        self.layer = terre_image_utils.working_layer(self.canvas)
#         source = self.canvas.currentLayer().source()
#         self.layer = WorkingLayer(source, self.canvas.currentLayer())
#         
#         
#         #self.layer = self.canvas.currentLayer()
#         if self.layer :
#             #self.define_bands(self.layer)
#             #manage_bands()
#             #self.red, self.green, self.blue, self.pir, self.mir = manage_bands().get_values()
#             red, green, blue, pir, mir = manage_bands().get_values()
#             
#             bands = { 'red':red, 'green':green, 'blue':blue, 'pir':pir, 'mir':mir }
#             self.layer.set_bands(bands)
#             
#             
#             print red, green, blue, pir, mir
        if self.layer:
            self.label_working_layer.setText(self.layer.name())
            
        
    
    def spectral_angles( self ):
        self.get_point_for_angles()
#         if self.layer :
#             angle_tool = SpectralAngle(self.iface, self.layer)
        
   
    def angles(self, x, y):
        if self.layer :
            terre_image_processing.angles(self.layer, self.working_directory, self.iface, x, y)
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
   
        
        
    def disconnectP(self):
        """
        Disconnection of signals, go back to the main interface
        """
        #self.changeActive(False)
        #QtCore.QObject.disconnect(self.canvas, SIGNAL( "keyPressed( QKeyEvent * )" ), self.pauseDisplay )
        self.iface.mainWindow().statusBar().showMessage( "" ) 
