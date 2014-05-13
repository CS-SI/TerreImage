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
import manage_QGIS


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
    
        self.histo = QAction( QIcon( ":icons/24-to-8-bits.png" ), QCoreApplication.translate( "TerreImage", "Afficher l'histogramme" ), self.iface.mainWindow() )
        self.histo.setStatusTip( QCoreApplication.translate( "TerreImage", "Affiche l'histogramme de l'image de travail" ) )
        QObject.connect( self.histo, SIGNAL( "triggered()" ), self.do_histogram )
    
        self.values = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "Afficher les valeurs des pixels" ), self.iface.mainWindow() )
        self.values.setStatusTip( QCoreApplication.translate( "TerreImage", "Affiche les valeurs des pixels sous la douris pour toutes les images" ) )
        QObject.connect( self.values, SIGNAL( "triggered()" ), self.do_display_values )
    
        self.visualization_menu.addActions( [ self.histo, self.values ] )
    
    
        #self.extractionMenu.addActions( [ self.clipper ] )
        self.kmz = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "Export KMZ" ), self.iface.mainWindow() )
        self.kmz.setStatusTip( QCoreApplication.translate( "TerreImage", "Export the current view in KMZ" ) )
        QObject.connect( self.kmz, SIGNAL( "triggered()" ), self.do_export_kmz )
        
        
        self.menu.addMenu( self.processing_menu )
        self.menu.addMenu( self.visualization_menu )
        self.menu.addActions([self.kmz])
        
#         if not self.analysisMenu.isEmpty():
#           self.menu.addMenu( self.analysisMenu )

    def extra_menu_visu( self, bands ):
        corres = { 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
        
            
        for i in range(self.layer.get_band_number()):
            y=[x for x in bands if bands[x]==i+1]
            if y :
                text = corres[y[0]]
                visu_band = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", text ), self.iface.mainWindow() )
                visu_band.setStatusTip( QCoreApplication.translate( "TerreImage", "Export the current view in KMZ" ) )
                QObject.connect( visu_band, SIGNAL( "triggered()" ), lambda who=str(y[0]): self.do_display_one_band(who)) #self.do_display_one_band )
                self.visualization_menu.addAction(visu_band)



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
        self.educationWidget.spectral_angles()
    
    def do_kmeans(self):
        print "kmeans signal"
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
    
    def do_display_one_band(self, who):
        print "who", who
        manage_QGIS.display_one_band(self.layer, who)

    
    def do_histogram(self):
        pass
    
    def do_display_values(self):
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
        self.layer, bands  = terre_image_utils.get_workinglayer_on_opening( self.iface )
        if self.layer :
            self.educationWidget.layer = self.layer
            self.extra_menu_visu(bands)
        
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