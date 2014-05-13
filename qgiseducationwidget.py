# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducationDialog
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-04-30
        copyright            : (C) 2014 by CS SI
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


from manage_bands import manage_bands
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
        
        self.working_directory, _ = self.fill_default_directory()
        self.value_tool = ValueWidget( self.iface, self )
        
        self.tool = ProfiletoolMapTool(self.iface.mapCanvas())        #the mouselistener
        print "self.tool", self.tool
        self.pointstoDraw = None    #Polyline in mapcanvas CRS analysed
        self.maptool = self.canvas.mapTool()
        self.get_point_for_angles()
     
    def setupUi_extra(self):
        """
        Initialize the interface
        """
        self.pushButton_brightness.clicked.connect(self.brightness)
        self.pushButton_ndti.clicked.connect(self.ndti)
        self.pushButton_ndvi.clicked.connect(self.ndvi)
        self.pushButton_working_layer.clicked.connect(self.working_layer)
        self.pushButton_angle.clicked.connect(self.spectral_angles)
        
        
    def brightness(self):
        if not self.layer :
            print "Aucune layer selectionnée"
        else :
            print "brightness"    
               
    
    def ndvi(self):
        #NDVI= (PIR-R)/(PIR+R)
        if not self.layer :
            print "Aucune layer selectionnée"
        else :
            if self.pir and self.red :
                image_in = self.layer.source()
                print "image_in", image_in
                print self.working_directory
                output_filename = os.path.join( self.working_directory, 
                                                os.path.basename(os.path.splitext(image_in)[0]) + "_ndvi" + os.path.splitext(image_in)[1]
                                              )
                print output_filename
                layer_pir = "im1b" + str(self.pir)
                layer_red = "im1b" + str(self.red)
                expression = "\"(" + layer_pir + "-" + layer_red + ")/(" + layer_pir + "+" + layer_red + ")\""
                print expression
                print "image_in", image_in
                OTBApplications.bandmath_cli( [image_in], expression, output_filename )
                manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_ndvi", self.iface )
                
                 
    def ndti(self):
        #SQRT(R+0.5)
        if not self.layer :
            print "Aucune layer selectionnée"
        else :
            if self.red :
                image_in = self.layer.source()
                print "image_in", image_in
                output_filename = os.path.join( self.working_directory, os.path.basename(os.path.splitext(image_in)[0]) + "_ndti" + os.path.splitext(image_in)[1])
                print output_filename
                layer_red = "im1b" + str(self.red)
                expression = "\"sqrt(" + layer_red + "+0.5)\""
                print expression
                print "image_in", image_in
                OTBApplications.bandmath_cli( [image_in], expression, output_filename )
                manage_QGIS.addRasterLayerToQGIS( output_filename, os.path.basename(os.path.splitext(image_in)[0]) + "_ndti", self.iface )
        
        
    def working_layer(self):
        self.layer = self.canvas.currentLayer()
        if self.layer :
            #self.define_bands(self.layer)
            #manage_bands()
            self.red, self.green, self.blue, self.pir, self.mir = manage_bands().get_values()
            print self.red, self.green, self.blue, self.pir, self.mir
            self.label_working_layer.setText(self.layer.name())
            
            
    def define_bands(self, layer_qgis):
        """
        Dialog boxes with the user to get the resolution and the red, green, blue bands.
        """
        erreur = False
        
        def move_at_end( list, element ):
            list.remove(element)
            list.append(element)
        
        
        bands = []
        for band_number in range(layer_qgis.bandCount()):
            bands.append("band " + str(band_number +1))
        
        
        testqt, ok = QtGui.QInputDialog.getItem(None, "Red", "Choose the red band", bands, False)
    
        if ok:
            red = str( testqt )[5:]
            move_at_end(bands, testqt)
        else:
            erreur = True
            
        testqt, ok = QtGui.QInputDialog.getItem(None, "Green", "Choose the green band", bands, False)
    
        if ok:
            green = str( testqt )[5:]
            move_at_end(bands, testqt)
        else:
            erreur = True
            
        testqt, ok = QtGui.QInputDialog.getItem(None, "Blue", "Choose the blue band", bands, False)
    
        if ok:
            blue = str( testqt )[5:]
            move_at_end(bands, testqt)
        else:
            erreur = True
            
        testqt, ok = QtGui.QInputDialog.getItem(None, "IR", "Choose the IF band", bands, False)
    
        if ok:
            ir = str( testqt )[5:]
            move_at_end(bands, testqt)
        else:
            erreur = True
            
        if not erreur : 
            return str( red ), str( green ), str( blue ), str(ir)
        else :
            return None, None, None, None
        
    
    def spectral_angles( self ):
        self.get_point_for_angles()
#         if self.layer :
#             angle_tool = SpectralAngle(self.iface, self.layer)
        
   
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
   
        
        
    def fill_default_directory( self ):
        """
        Creates working directory 
        Fills the output directory line edit if ui given
        """
        datetimeNow = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        currentDirectory = os.path.join( os.getenv("HOME"), "TerreImage", datetimeNow )
        if not os.path.exists( currentDirectory ):
            os.makedirs( currentDirectory )
        return currentDirectory, datetimeNow
        
    def disconnectP(self):
        """
        Disconnection of signals, go back to the main interface
        """
        #self.changeActive(False)
        #QtCore.QObject.disconnect(self.canvas, SIGNAL( "keyPressed( QKeyEvent * )" ), self.pauseDisplay )
        self.iface.mainWindow().statusBar().showMessage( "" ) 
