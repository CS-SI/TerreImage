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
from terre_image_task import TerreImageProcessing
from terre_image_task import TerreImageDisplay
import terre_image_utils

from processing_manager import ProcessingManager


import datetime
import os
from ptmaptool import ProfiletoolMapTool
from valuetool.valuewidget import ValueWidget

from spectral_angle import SpectralAngle

from DockableMirrorMap.dockableMirrorMapPlugin import DockableMirrorMapPlugin

class QGISEducationWidget(QtGui.QWidget, Ui_QGISEducation):
    def __init__(self, iface):
        
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
                
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        self.setupUi_extra()
        
        self.qgis_education_manager = ProcessingManager( self.iface )
        self.lineEdit_working_dir.setText(self.qgis_education_manager.working_directory)
        
        self.value_tool = ValueWidget( self.iface ) #, self )
        #creating a dock widget
        # create the dockwidget with the correct parent and add the valuewidget
        self.valuedockwidget = QtGui.QDockWidget("Values", self.iface.mainWindow() )
        self.valuedockwidget.setObjectName("Values")
        self.valuedockwidget.setWidget(self.value_tool)
        self.iface.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.valuedockwidget)
        self.valuedockwidget.hide()
        
        
        print self.value_tool
        
        self.layer = None
        
        self.mirror_map_tool = DockableMirrorMapPlugin(self.iface)
        self.mirror_map_tool.initGui()
        
        self.angle_tool = SpectralAngle(self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool)


     
    def setupUi_extra(self):
        """
        Initialize the interface
        """
        
        itemProcessing = [ "", "NDVI", "NDTI", "Indice de brillance", "Angle Spectral" ]
        for index in range(len(itemProcessing)):
            item = itemProcessing[index]
            self.comboBox_processing.insertItem ( index, item )
        self.comboBox_processing.currentIndexChanged[str].connect(self.do_manage_processing)
            
        
        
        self.pushButton_kmeans.clicked.connect(self.kmeans)
        self.pushButton_profil_spectral.clicked.connect(self.display_values)
        self.pushButton_working_dir.clicked.connect(self.define_working_dir)
        
    def define_working_dir(self):
        output_dir = terre_image_utils.getOutputDirectory(self)
        self.qgis_education_manager.working_directory = output_dir
        
        
    def do_manage_processing(self, text_changed):
        if text_changed:
            print "text changed", text_changed
            print "self.layer", self.layer
            my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool, text_changed )
            self.qgis_education_manager.add_processing(my_processing)
            self.comboBox_processing.setCurrentIndex( 0 )
            self.value_tool.set_layers(self.qgis_education_manager.layers_for_value_tool)
        
        
        
    def set_comboBox_sprectral_band_display( self ):
        if self.layer:
            bands = self.layer.bands
            corres = { 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
        
            self.comboBox_sprectral_band_display.clear()
            self.comboBox_sprectral_band_display.insertItem( 0, "" )
            
            if self.layer.has_natural_colors():
                print "couleurs naturelles"
                self.comboBox_sprectral_band_display.insertItem( 1, "Afficher en couleurs naturelles" )
            
            for i in range(self.layer.get_band_number()):
                y=[x for x in bands if bands[x]==i+1]
                if y :
                    text = corres[y[0]]
                    self.comboBox_sprectral_band_display.insertItem( i+2, text )
            self.comboBox_sprectral_band_display.currentIndexChanged[str].connect(self.do_manage_sprectral_band_display)
            
            
    def do_manage_sprectral_band_display(self, text_changed):
        if text_changed:
            band_to_display = None
            corres = { 'nat':"Afficher en couleurs naturelles", 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
            for key in corres:
                if corres[key] == text_changed :
                    who = key
                    #band_to_display = self.layer.bands[key]
                    #manage_QGIS.display_one_band(self.layer, who, self.iface)
                    my_processing = TerreImageDisplay( self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool, who )
                    self.qgis_education_manager.add_processing(my_processing)
                    break
            self.comboBox_sprectral_band_display.setCurrentIndex( 0 )
        
        
    def display_values(self):
        self.valuedockwidget.show()
        self.value_tool.changeActive( QtCore.Qt.Checked )
        self.value_tool.cbxActive.setCheckState( QtCore.Qt.Checked )
        self.value_tool.set_layers(self.qgis_education_manager.layers_for_value_tool)
                 
    def kmeans(self):
        
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            nb_class = self.spinBox_kmeans.value()
            print "nb_colass from spinbox", nb_class
            my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool, "KMEANS", nb_class )
            self.qgis_education_manager.add_processing(my_processing)
            
            self.value_tool.set_layers(self.qgis_education_manager.layers_for_value_tool)
            #terre_image_processing.kmeans(self.layer, self.qgis_education_manager.working_directory, self.iface, nb_class)
        
        
    def working_layer(self):
        self.layer = terre_image_utils.working_layer(self.canvas)
        if self.layer:
            self.label_working_layer.setText(self.layer.name())
            
        
    
#     def spectral_angles( self ):
#         self.angle_tool.get_point_for_angles(self.layer)

   
        
        
    def disconnectP(self):
        """
        Disconnection of signals, go back to the main interface
        """
        #self.changeActive(False)
        #QtCore.QObject.disconnect(self.canvas, SIGNAL( "keyPressed( QKeyEvent * )" ), self.pauseDisplay )
        self.iface.mainWindow().statusBar().showMessage( "" ) 
