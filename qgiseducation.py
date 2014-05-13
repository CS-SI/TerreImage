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
import terre_image_processing
import terre_image_utils


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
        
        self.dockOpened = False
        
        # create the widget to display information
        self.educationWidget = QGISEducationWidget(self.iface)
        self.working_directory = self.educationWidget.working_directory
        
        # create the dockwidget with the correct parent and add the valuewidget
        self.valuedockwidget = QDockWidget("QGIS Education", self.iface.mainWindow() )
        self.valuedockwidget.setObjectName("QGIS Education")
        self.valuedockwidget.setWidget(self.educationWidget)
        QObject.connect(self.valuedockwidget, SIGNAL('visibilityChanged ( bool )'), self.showHideDockWidget)
        
        # add the dockwidget to iface
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.valuedockwidget)
        #self.educationWidget.show()

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
    
        self.ndvi = QAction( QIcon(":/icons/warp.png"),  QCoreApplication.translate( "TerreImage", "NDVI" ), self.iface.mainWindow() )
        self.ndvi.setStatusTip( QCoreApplication.translate( "TerreImage", "Calcule le NDVI de l'image de travail") )
        QObject.connect( self.ndvi, SIGNAL( "triggered()" ), self.do_ndvi )
    
        self.ndti = QAction( QIcon( ":icons/projection-add.png" ), QCoreApplication.translate( "TerreImage", "NDTI" ), self.iface.mainWindow() )
        self.ndti.setStatusTip( QCoreApplication.translate( "TerreImage", "Calcule le NDTI de l'image de travail" ) )
        QObject.connect( self.ndti, SIGNAL( "triggered()" ), self.do_ndti )
    
        self.brightness = QAction( QIcon( ":icons/projection-add.png" ), QCoreApplication.translate( "TerreImage", "Indice de brillance" ), self.iface.mainWindow() )
        self.brightness.setStatusTip( QCoreApplication.translate( "TerreImage", "Calcule l'indice de brillance de l'image de travail" ) )
        QObject.connect( self.brightness, SIGNAL( "triggered()" ), self.do_brightness )
    
        self.angles = QAction( QIcon( ":icons/projection-add.png" ), QCoreApplication.translate( "TerreImage", "Angle spectral" ), self.iface.mainWindow() )
        self.angles.setStatusTip( QCoreApplication.translate( "TerreImage", "Calcule l'angle spectral pour la coordonnée pointée de l'image de travail" ) )
        QObject.connect( self.angles, SIGNAL( "triggered()" ), self.do_angles )
        
        self.kmeans = QAction( QIcon( ":icons/projection-add.png" ), QCoreApplication.translate( "TerreImage", "KMeans" ), self.iface.mainWindow() )
        self.kmeans.setStatusTip( QCoreApplication.translate( "TerreImage", "Calcule le kmeans sur l'image de travail" ) )
        QObject.connect( self.kmeans, SIGNAL( "triggered()" ), self.do_kmeans )
        
        self.classif = QAction( QIcon( ":icons/projection-add.png" ), QCoreApplication.translate( "TerreImage", "Classif" ), self.iface.mainWindow() )
        self.classif.setStatusTip( QCoreApplication.translate( "TerreImage", "Ouvre le module de classification sur l'image de travail" ) )
        QObject.connect( self.classif, SIGNAL( "triggered()" ), self.do_classif )
    
    
        self.processing_menu.addActions( [ self.ndvi, self.ndti, self.brightness, self.angles, self.kmeans, self.classif ] )
    
        # conversion menu (Rasterize (Vector to raster), Polygonize (Raster to vector), Translate, RGB to PCT, PCT to RGB)
        self.visualization_menu = QMenu( QCoreApplication.translate( "TerreImage", "Visualisation" ), self.iface.mainWindow() )
    

        self.polygonize = QAction( QIcon(":/icons/polygonize.png"), QCoreApplication.translate( "TerreImage", "Polygonize (Raster to vector)" ), self.iface.mainWindow() )
        self.polygonize.setStatusTip( QCoreApplication.translate( "TerreImage", "Produces a polygon feature layer from a raster") )
        #QObject.connect( self.polygonize, SIGNAL( "triggered()" ), self.doPolygonize )
        #self.visualization_menu.addAction( self.polygonize )
    
        self.translate = QAction( QIcon(":/icons/translate.png"), QCoreApplication.translate( "TerreImage", "Translate (Convert format)" ), self.iface.mainWindow() )
        self.translate.setStatusTip( QCoreApplication.translate( "TerreImage", "Converts raster data between different formats") )
        #QObject.connect( self.translate, SIGNAL( "triggered()" ), self.doTranslate )
    
        self.paletted = QAction( QIcon( ":icons/24-to-8-bits.png" ), QCoreApplication.translate( "TerreImage", "RGB to PCT" ), self.iface.mainWindow() )
        self.paletted.setStatusTip( QCoreApplication.translate( "TerreImage", "Convert a 24bit RGB image to 8bit paletted" ) )
        #QObject.connect( self.paletted, SIGNAL( "triggered()" ), self.doPaletted )
    
        self.rgb = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "PCT to RGB" ), self.iface.mainWindow() )
        self.rgb.setStatusTip( QCoreApplication.translate( "TerreImage", "Convert an 8bit paletted image to 24bit RGB" ) )
        #QObject.connect( self.rgb, SIGNAL( "triggered()" ), self.doRGB )
    
        #self.visualization_menu.addActions( [ self.translate, self.paletted, self.rgb ] )
    
        # extraction menu (Clipper, Contour)
        self.extractionMenu = QMenu( QCoreApplication.translate( "TerreImage", "Extraction" ), self.iface.mainWindow() )
    
        self.contour = QAction( QIcon(":/icons/contour.png"), QCoreApplication.translate( "TerreImage", "Contour" ), self.iface.mainWindow() )
        self.contour.setStatusTip( QCoreApplication.translate( "TerreImage", "Builds vector contour lines from a DEM") )
        #QObject.connect( self.contour, SIGNAL( "triggered()" ), self.doContour )
        #self.extractionMenu.addAction( self.contour )
    
        self.clipper = QAction( QIcon( ":icons/raster-clip.png" ), QCoreApplication.translate( "TerreImage", "Clipper" ), self.iface.mainWindow() )
        #self.clipper.setStatusTip( QCoreApplication.translate( "GdalTools", "Converts raster data between different formats") )
        #QObject.connect( self.clipper, SIGNAL( "triggered()" ), self.doClipper )
    
        #self.extractionMenu.addActions( [ self.clipper ] )
        self.kmz = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "Export KMZ" ), self.iface.mainWindow() )
        self.kmz.setStatusTip( QCoreApplication.translate( "TerreImage", "Export the current view in KMZ" ) )
        QObject.connect( self.kmz, SIGNAL( "triggered()" ), self.do_export_kmz )
        
        
        self.menu.addMenu( self.processing_menu )
        self.menu.addMenu( self.visualization_menu )
        self.menu.addMenu( self.extractionMenu )
        self.menu.addActions([self.kmz])
        
#         if not self.analysisMenu.isEmpty():
#           self.menu.addMenu( self.analysisMenu )


    def do_ndvi(self):
        if not self.layer:
            self.layer = self.educationWidget.layer
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            terre_image_processing.ndvi(self.layer, self.working_directory, self.iface)
                
                 
    def do_ndti(self):
        if not self.layer:
            self.layer = self.educationWidget.layer
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            terre_image_processing.ndti(self.layer, self.working_directory, self.iface)
            
    def do_brightness(self):
        if not self.layer:
            self.layer = self.educationWidget.layer
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            terre_image_processing.brightness(self.layer, self.working_directory, self.iface)
    
    def do_angles(self):
        pass
    
    def do_kmeans(self):
        if not self.layer:
            self.layer = self.educationWidget.layer
        if self.layer == None :
            print "Aucune layer selectionnée"
        else :
            terre_image_processing.kmeans(self.layer, self.working_directory, self.iface)
    
    def do_classif(self):
        pass

    def do_export_kmz(self):
        pass

    def unload(self):
        """
        Defines the unload of the plugin
        """
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
        self.layer = terre_image_utils.get_workinglayer_on_opening( self.iface )
        self.educationWidget.layer = self.layer
        
        #if dock not already opened, open the dock and all the necessary thing (model,doProfile...)
        if self.dockOpened == False:
            self.educationWidget.show()
            # add the dockwidget to iface
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.valuedockwidget)
            self.dockOpened = True
        else :
            self.educationWidget.hide()
            self.dockOpened = False
            self.iface.removeDockWidget(self.valuedockwidget)


    def showHideDockWidget( self ):
        """
        Change the state of the widget, and run the connections of signals of the widget
        """
#         if self.valuedockwidget.isVisible() and self.educationWidget.cbxActive.isChecked():
#             state = Qt.Checked
#         else:
#             state = Qt.Unchecked
#         self.educationWidget.changeActive( state )
        pass