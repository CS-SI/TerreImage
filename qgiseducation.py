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
from qgis.gui import QgsMessageBar

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
from terre_image_constant import TerreImageConstant
#from supervisedclassification import SupervisedClassification


class QGISEducation:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        
        
        self.constants = TerreImageConstant()
        self.constants.QGISInterface = self.iface
        self.constants.QGISCanvas = self.iface.mapCanvas()
        self.constants.QGISLegendInterface = self.iface.legendInterface()


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
        #self.extra_menu()
        
        self.qgisedudockwidget = None
        self.dockOpened = False
        self.educationWidget = None
        
        
        QObject.connect(self.iface, SIGNAL("projectRead()"), self.onProjectLoaded)
        QObject.connect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.onWriteProject)
        QObject.connect(self.iface, SIGNAL("newProjectCreated()"), self.newProject)        
    
        
        
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
                       "Angle spectral":"Calcule l'angle spectral pour la coordonnée pointée de l'image de travail", "Classif":"Ouvre le module de classification sur l'image de travail"}
        icons = {"NDVI":":/icons/warp.png", "NDTI":":icons/projection-add.png", "Indice de brillance":":/icons/warp.png", \
                 "KMEANS":":icons/projection-add.png", "Angle spectral":":/icons/warp.png", "Classif":":icons/projection-add.png"}
        
        for key in processings.keys():
            action = QAction( QIcon(icons[key]),  QCoreApplication.translate( "TerreImage", key ), self.iface.mainWindow() )
            action.setStatusTip( QCoreApplication.translate( "TerreImage", processings[key]) )
            QObject.connect( action, SIGNAL( "triggered()" ), lambda who=key: self.do_process(who))
            self.processing_menu.addAction( action )

      
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
        print "bands", bands
        corres = { 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
        
        self.visualization_menu.clear()
        self.visualization_menu.addActions( [ self.histo, self.values ] )
        
        if self.qgis_education_manager.layer.has_natural_colors():
            visu_band = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", "Afficher en couleurs naturelles" ), self.iface.mainWindow() )
            visu_band.setStatusTip( QCoreApplication.translate( "TerreImage", "Afficher en couleurs naturelles" ) )
            QObject.connect( visu_band, SIGNAL( "triggered()" ), lambda who='nat': self.do_display_one_band(who)) #self.do_display_one_band )
            self.visualization_menu.addAction(visu_band)
            
        for i in range(self.qgis_education_manager.layer.get_band_number()):
            y=[x for x in bands if bands[x]==i+1]
            if y :
                text = corres[y[0]]
                visu_band = QAction( QIcon( ":icons/8-to-24-bits.png" ), QCoreApplication.translate( "TerreImage", text ), self.iface.mainWindow() )
                visu_band.setStatusTip( QCoreApplication.translate( "TerreImage", text ) )
                QObject.connect( visu_band, SIGNAL( "triggered()" ), lambda who=str(y[0]): self.do_display_one_band(who)) #self.do_display_one_band )
                self.visualization_menu.addAction(visu_band)


    def do_process(self, name):
        timeBegin = time.time()
        if self.qgis_education_manager.layer == None :
            print "Aucune layer selectionnée"
        else :
            my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.qgis_education_manager.layer, self.educationWidget.mirror_map_tool, name )
            self.qgis_education_manager.add_processing(my_processing)
            self.qgisedudockwidget.set_combobox_histograms()
            
        
        self.educationWidget.value_tool.set_layers(self.qgis_education_manager.layers_for_value_tool)
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
        #manage_QGIS.display_one_band(self.qgis_education_manager.layer, who, self.iface)
        my_process = TerreImageDisplay( self.iface, self.qgis_education_manager.working_directory, self.qgis_education_manager.layer, self.educationWidget.mirror_map_tool, who )
        self.qgis_education_manager.add_processing(my_process)
        self.qgisedudockwidget.set_combobox_histograms()
        
        
    def do_histogram(self):
        pass
    
    def do_display_values(self):
        self.educationWidget.display_values()



    def unload(self):
        """
        Defines the unload of the plugin
        """
        self.unload_interface()
            # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&QGISEducation", self.action)
        self.iface.removeToolBarIcon(self.action)

    def unload_interface(self):
        if self.qgisedudockwidget is not None:
            self.qgisedudockwidget.close()
            self.educationWidget.disconnectP()



    def set_working_message(self, set=True):
        if set :
            widget = self.iface.messageBar().createMessage("Terre Image", "Travail en cours...")
            self.iface.messageBar().pushWidget(widget, QgsMessageBar.INFO)
            self.iface.mainWindow().statusBar().showMessage("Terre Image : Travail en cours...")
            self.iface.messageBar().pushMessage("Terre Image", "Travail en cours...")
        else :
            self.iface.messageBar().clearWidgets()
            self.iface.mainWindow().statusBar().clearMessage()

    # run method that performs all the real work
    
    def run(self):
        """
        Defines the behavior of the plugin
        """
        

        
        timeBegin = time.time()
        self.set_working_message(True)
        
        self.iface.newProject( True )
        
        self.constants.index_group = self.iface.legendInterface().addGroup( "Terre Image", True, None )
        print self.constants.index_group
        
        self.qgis_education_manager = ProcessingManager(self.iface)
        
        
        _, bands  = self.qgis_education_manager.set_current_layer( )
        print "self.layer", self.qgis_education_manager.layer
        timeEnd = time.time()
        timeExec = timeEnd - timeBegin
        print "temps de chargement : ", timeExec
        
        self.show_education_widget(bands)
        
        
        self.set_working_message(False)
            
    
    def show_education_widget(self, bands):
        if self.qgis_education_manager.layer and bands:

            if not self.dockOpened :
                # create the widget to display information
                self.educationWidget = QGISEducationWidget(self.iface)
                QObject.connect( self.educationWidget, SIGNAL( "terminated()" ), self.unload_interface )
                self.educationWidget.qgis_education_manager = self.qgis_education_manager
                self.educationWidget.lineEdit_working_dir.setText(self.qgis_education_manager.working_directory)
                
                # create the dockwidget with the correct parent and add the valuewidget
                self.qgisedudockwidget = QDockWidget("QGIS Education", self.iface.mainWindow() )
                self.qgisedudockwidget.setObjectName("QGIS Education")
                self.qgisedudockwidget.setWidget(self.educationWidget)
                
                # add the dockwidget to iface
                self.iface.addDockWidget(Qt.RightDockWidgetArea, self.qgisedudockwidget)

            text = "Plan R <- BS_PIR \nPlan V <- BS_R \nPlan B <- BS_V"
            self.educationWidget.textEdit.setText(text)
            #self.extra_menu_visu(bands)
            
            self.qgisedudockwidget.show()
            self.educationWidget.set_comboBox_sprectral_band_display()
            self.dockOpened = True        
            
            
    def newProject(self):
        if self.educationWidget is not None:
            self.educationWidget.disconnect_interface()
            if self.qgisedudockwidget is not None:
                self.qgisedudockwidget.close()
                self.educationWidget.disconnectP()
                self.dockOpened = False

    def onWriteProject(self, domproject):
        if self.qgis_education_manager.layer is None:
            return

        QgsProject.instance().writeEntry( "QGISEducation", "/working_layer", self.qgis_education_manager.layer.source_file )
        # write band orders
        QgsProject.instance().writeEntry( "QGISEducation", "/working_layer_bands", str(self.qgis_education_manager.layer.bands) )
        print str(self.qgis_education_manager.layer.bands)
        QgsProject.instance().writeEntry( "QGISEducation", "/working_layer_type", self.qgis_education_manager.layer.type )
        QgsProject.instance().writeEntry( "QGISEducation", "/working_directory", self.qgis_education_manager.working_directory )
        p = []
        for process in self.qgis_education_manager.processings:
            p.append(process.processing_name)
            
        QgsProject.instance().writeEntry( "QGISEducation", "/process", str(p) )
        

    def onProjectLoaded(self):
        # restore mirrors?
        wl, ok = QgsProject.instance().readEntry("QGISEducation", "/working_layer")
        if not ok or wl is None:
            return
        
        bands, ok = QgsProject.instance().readEntry("QGISEducation", "/working_layer_bands")
        print "is ok", ok
        print bands
        
        # TODO interpreter bands
        type, ok = QgsProject.instance().readEntry("QGISEducation", "/working_layer_type")
        
        working_dir, ok = QgsProject.instance().readEntry("QGISEducation", "/working_directory")
        
        self.qgis_education_manager = ProcessingManager( self.iface )
        self.qgis_education_manager.restore_processing_manager(wl, eval(bands), type, working_dir)
        
        process, ok = QgsProject.instance().readEntry("QGISEducation", "/process")
        print eval(process)
        
        self.show_education_widget(bands)
        
        for i in process:
            if i in[ "NDVI", "NDTI", "Indice de brillance", "Kmeans" ]:
                self.educationWidget.do_manage_processing( i )
                
            else:
                self.educationWidget.do_manage_sprectral_band_display(i)
        
        
        
        
        

        
        #restore all process ?
        

#         # remove all mirrors
#         self.removeDockableMirrors()
# 
#         mirror2lids = {}
#         # load mirrors
#         for i in range(num):
#             if num >= 2:
#                 if i == 0: 
#                     prevFlag = self.iface.mapCanvas().renderFlag()
#                     self.iface.mapCanvas().setRenderFlag(False)
#                 elif i == num-1:
#                     self.iface.mapCanvas().setRenderFlag(True)
# 
#             from dockableMirrorMap import DockableMirrorMap
#             dockwidget = DockableMirrorMap(self.iface.mainWindow(), self.iface)
# 
#             minsize = dockwidget.minimumSize()
#             maxsize = dockwidget.maximumSize()
# 
#             # restore position
#             floating, ok = QgsProject.instance().readBoolEntry("DockableMirrorMap", "/mirror%s/floating" % i)
#             if ok: 
#                 dockwidget.setFloating( floating )
#                 position, ok = QgsProject.instance().readEntry("DockableMirrorMap", "/mirror%s/position" % i)
#                 if ok: 
#                     try:
#                         if floating:
#                             parts = position.split(" ")
#                             if len(parts) >= 2:
#                                 dockwidget.move( int(parts[0]), int(parts[1]) )
#                         else:
#                             dockwidget.setLocation( int(position) )
#                     except ValueError:
#                         pass
# 
#             # restore geometry
#             dockwidget.setFixedSize( dockwidget.geometry().width(), dockwidget.geometry().height() )
#             size, ok = QgsProject.instance().readEntry("DockableMirrorMap", "/mirror%s/size" % i)
#             if ok:
#                 try:
#                     parts = size.split(" ")
#                     dockwidget.setFixedSize( int(parts[0]), int(parts[1]) )
#                 except ValueError:
#                     pass                
# 
#             scaleFactor, ok = QgsProject.instance().readDoubleEntry("DockableMirrorMap", "/mirror%s/scaleFactor" % i, 1.0)
#             if ok: dockwidget.getMirror().scaleFactor.setValue( scaleFactor )
# 
#             # get layer list
#             layerIds, ok = QgsProject.instance().readListEntry("DockableMirrorMap", "/mirror%s/layers" % i)
#             if ok: dockwidget.getMirror().setLayerSet( layerIds )
# 
#             self.addDockWidget( dockwidget )
#             dockwidget.setMinimumSize(minsize)
#             dockwidget.setMaximumSize(maxsize)
