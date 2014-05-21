# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from qgiseducationwidget import QGISEducationWidget
import os.path

from manage_bands import manage_bands
from working_layer import WorkingLayer
from terre_image_task import TerreImageProcessing
from terre_image_task import TerreImageDisplay
from processing_manager import ProcessingManager
import terre_image_utils
import time
#from supervisedclassification import SupervisedClassification


class QGISEducation:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface


    def initGui(self):
        """
        Initialisation on the widget interface
        """
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/qgiseducation/icon.png"),
            u"QGIS Education", self.iface.mainWindow())
        self.action.setWhatsThis("QGIS_Education")
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&QGISEducation", self.action)
        self.extra_menu()
        
        self.layer = None
        
        self.valuedockwidget = None
        self.dockOpened = False
        
        
        #self.classif_tool = SupervisedClassification()
        #print self.classif_tool

    def extra_menu(self):
        # find the Raster menu
        rasterMenu = None
        menu_bar = self.iface.mainWindow().menuBar()
        actions = menu_bar.actions()
    
        rasterText = QCoreApplication.translate( "QgisApp", "&TerreImage" )
    
        for a in actions:
            if a.menu() != None and a.menu().title() == rasterText:
                rasterMenu = a.menu()
                break
    
        if rasterMenu == None:
            # no Raster menu, create and insert it before the Help menu
            self.menu = QMenu( rasterText, self.iface.mainWindow() )
            lastAction = actions[ len( actions ) - 1 ]
            menu_bar.insertMenu( lastAction, self.menu )
        else:
            self.menu = rasterMenu
            self.menu.addSeparator()
    
        # projections menu (Warp (Reproject), Assign projection)
        self.processing_menu = QMenu( QCoreApplication.translate( "TerreImage", "Traitements" ), self.iface.mainWindow() )
        
        processings = {"NDVI":"Calcule le NDVI de l'image de travail", "NDTI":"Calcule le NDTI de l'image de travail",\
                       "Indice de brillance":"Calcule l'indice de brillance de l'image de travail", "KMEANS":"Calcule le kmeans sur l'image de travail",\
                       "Classif":"Ouvre le module de classification sur l'image de travail"}
        icons = {"NDVI":":/icons/warp.png", "NDTI":":icons/projection-add.png", "Indice de brillance":":/icons/warp.png", \
                 "KMEANS":":icons/projection-add.png", "Classif":":/icons/warp.png"}
        
        for key in processings.keys():
            action = QAction( QIcon(icons[key]),  QCoreApplication.translate( "TerreImage", key ), self.iface.mainWindow() )
            action.setStatusTip( QCoreApplication.translate( "TerreImage", processings[key]) )
            QObject.connect( action, SIGNAL( "triggered()" ), lambda who=key: self.do_process(who))
            self.processing_menu.addAction( action )
    
        self.angles = QAction( QIcon( ":icons/projection-add.png" ), QCoreApplication.translate( "TerreImage", "Angle spectral" ), self.iface.mainWindow() )
        self.angles.setStatusTip( QCoreApplication.translate( "TerreImage", "Calcule l'angle spectral pour la coordonnée pointée de l'image de travail" ) )
        QObject.connect( self.angles, SIGNAL( "triggered()" ), self.do_angles )
        #QObject.connect( self.angles, SIGNAL( "triggered()" ), lambda who="KMZ": self.do_process(who))

    
        self.processing_menu.addActions( [ self.angles ] )
      
        # conversion menu (Rasterize (Vector to raster), Polygonize (Raster to vector), Translate, RGB to PCT, PCT to RGB)
        self.visualization_menu = QMenu( QCoreApplication.translate( "TerreImage", "Visualisation" ), self.iface.mainWindow() )
    
        self.histo = QAction( QIcon( ":icons/24-to-8-bits.png" ), QCoreApplication.translate( "TerreImage", "Afficher l'histogramme" ), self.iface.mainWindow() )
        self.histo.setStatusTip( QCoreApplication.translate( "TerreImage", "Affiche l'histogramme de l'image de travail" ) )
        QObject.connect( self.histo, SIGNAL( "triggered()" ), self.do_histogram )
    
        self.values = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "Afficher les valeurs des pixels" ), self.iface.mainWindow() )
        self.values.setStatusTip( QCoreApplication.translate( "TerreImage", "Affiche les valeurs des pixels sous la douris pour toutes les images" ) )
        QObject.connect( self.values, SIGNAL( "triggered()" ), self.do_display_values )
    
        self.visualization_menu.addActions( [ self.histo, self.values ] )
    
    
        self.kmz = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "Export KMZ" ), self.iface.mainWindow() )
        self.kmz.setStatusTip( QCoreApplication.translate( "TerreImage", "Export the current view in KMZ" ) )
        #QObject.connect( self.kmz, SIGNAL( "triggered()" ), self.do_export_kmz )
        QObject.connect( self.kmz, SIGNAL( "triggered()" ), lambda who="KMZ": self.do_process(who)) #self.do_display_one_band )
                
        
        self.menu.addMenu( self.processing_menu )
        self.menu.addMenu( self.visualization_menu )
        self.menu.addActions([self.kmz])
        
#         if not self.analysisMenu.isEmpty():
#           self.menu.addMenu( self.analysisMenu )

    def extra_menu_visu( self, bands ):
        corres = { 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
        
        self.visualization_menu.clear()
        self.visualization_menu.addActions( [ self.histo, self.values ] )
        
        if bands['red'] != 0 and bands['green'] != 0 and bands['blue'] != 0:
            visu_band = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "Afficher en couleurs naturelles" ), self.iface.mainWindow() )
            visu_band.setStatusTip( QCoreApplication.translate( "TerreImage", "Afficher en couleurs naturelles" ) )
            QObject.connect( visu_band, SIGNAL( "triggered()" ), lambda who='nat': self.do_display_one_band(who)) #self.do_display_one_band )
            self.visualization_menu.addAction(visu_band)
            
        for i in range(self.layer.get_band_number()):
            y=[x for x in bands if bands[x]==i+1]
            if y :
                text = corres[y[0]]
                visu_band = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", text ), self.iface.mainWindow() )
                visu_band.setStatusTip( QCoreApplication.translate( "TerreImage", text ) )
                QObject.connect( visu_band, SIGNAL( "triggered()" ), lambda who=str(y[0]): self.do_display_one_band(who)) #self.do_display_one_band )
                self.visualization_menu.addAction(visu_band)


    def do_process(self, name):
        timeBegin = time.time()
        if not self.layer:
            self.layer = self.educationWidget.layer
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.layer, self.educationWidget.mirror_map_tool, name )
            self.qgis_education_manager.add_processing(my_processing)
        
        timeEnd = time.time()
        timeExec = timeEnd - timeBegin
        print "temps du " + str(name) + "  : " + str(timeExec)
    
    
    def do_angles(self):
        self.educationWidget.spectral_angles()
    
    
    def do_classif(self):
        pass

    def do_export_kmz(self):
        pass
    
    def do_display_one_band(self, who):
        print "who", who
        #manage_QGIS.display_one_band(self.layer, who, self.iface)
        my_process = TerreImageDisplay( self.iface, self.qgis_education_manager.working_directory, self.layer, self.educationWidget.mirror_map_tool, who )
        self.qgis_education_manager.add_processing(my_process)
        
        
    def do_histogram(self):
        pass
    
    def do_display_values(self):
        self.educationWidget.value_tool.show()



    def unload(self):
        """
        Defines the unload of the plugin
        """
        if self.valuedockwidget is not None:
            self.valuedockwidget.close()
            self.educationWidget.disconnectP()
            # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&QGISEducation", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        """
        Defines the behavior of the plugin
        """
        timeBegin = time.time()
        
        
        self.qgis_education_manager = ProcessingManager(self.iface)
        
        
        self.layer, bands  = self.qgis_education_manager.set_current_layer( )
        print "self.layer", self.layer
        timeEnd = time.time()
        timeExec = timeEnd - timeBegin
        print "temps de chargement : ", timeExec
        
        if self.layer and bands:
            if not self.dockOpened :
                # create the widget to display information
                self.educationWidget = QGISEducationWidget(self.iface)
                self.educationWidget.qgis_education_manager = self.qgis_education_manager
                
                # create the dockwidget with the correct parent and add the valuewidget
                self.valuedockwidget = QDockWidget("QGIS Education", self.iface.mainWindow() )
                self.valuedockwidget.setObjectName("QGIS Education")
                self.valuedockwidget.setWidget(self.educationWidget)
                
                # add the dockwidget to iface
                self.iface.addDockWidget(Qt.RightDockWidgetArea, self.valuedockwidget)

            self.educationWidget.layer = self.layer
            text = "Plan R <- BS_PIR \nPlan V <- BS_R \nPlan B <- BS_V"
            self.educationWidget.textEdit.setText(text)
            self.extra_menu_visu(bands)
            
            self.valuedockwidget.show()
            self.educationWidget.set_comboBox_sprectral_band_display()
            self.dockOpened = True


