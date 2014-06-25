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
from qgis.gui import QgsRubberBand, QgsMapToolPan, QgsMessageBar

from qgis.core import QGis, QgsPoint, QgsRaster, QgsMapLayerRegistry


from working_layer import WorkingLayer
from terre_image_task import TerreImageProcessing
from terre_image_task import TerreImageDisplay
import terre_image_utils
import terre_image_processing
from terre_image_histogram import TerreImageHistogram_multiband
from terre_image_histogram import TerreImageHistogram_monoband
from terre_image_manager import TerreImageManager
from processing_manager import ProcessingManager


import datetime
import os
from ptmaptool import ProfiletoolMapTool
from valuetool.valuewidget import ValueWidget

from spectral_angle import SpectralAngle

from DockableMirrorMap.dockableMirrorMapPlugin import DockableMirrorMapPlugin



#import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger( 'TerreImage_qgiseducationwidget' )
logger.setLevel(logging.INFO)


class Terre_Image_Dock_widget(QtGui.QDockWidget):
    __pyqtSignals__ = ("closed(PyQt_PyObject)")
    def __init__(self, title, parent):
        QtGui.QDockWidget.__init__(self, title, parent)
        
    def closeEvent(self, event):
        self.emit( QtCore.SIGNAL( "closed(PyQt_PyObject)" ), self )



class QGISEducationWidget(QtGui.QWidget, Ui_QGISEducation, QtCore.QObject):
    __pyqtSignals__ = ("valueChanged()")
    def __init__(self, iface):
        
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
                
        QtGui.QWidget.__init__(self)
        QtCore.QObject.__init__(self)
        self.setupUi(self)
        self.setupUi_extra()
        
        self.qgis_education_manager = TerreImageManager( self.iface )
        self.lineEdit_working_dir.setText(self.qgis_education_manager.working_directory)
        
        QtCore.QObject.connect(QgsMapLayerRegistry.instance(), QtCore.SIGNAL( "layerWillBeRemoved(QString)" ), self.layer_deleted)
        
        self.dock_histo_opened = False
        


     
    def setupUi_extra(self):
        """
        Initialize the interface
        """
        
        itemProcessing = [ "Traitements...", "NDVI", "NDTI", "Indice de brillance", "Angle Spectral" ]
        for index in range(len(itemProcessing)):
            item = itemProcessing[index]
            self.comboBox_processing.insertItem ( index, item )
        self.comboBox_processing.currentIndexChanged[str].connect(self.do_manage_processing)
        
        #fill histograms
        itemHistogrammes = [ "Histogrammes", "Image de travail" ]
        for index in range(len(itemHistogrammes)):
            item = itemHistogrammes[index]
            self.comboBox_histogrammes.insertItem ( index, item )
        self.comboBox_histogrammes.currentIndexChanged[str].connect(self.do_manage_histograms)
        
        self.pushButton_kmeans.clicked.connect(self.kmeans)
        self.pushButton_profil_spectral.clicked.connect(self.display_values)
        self.pushButton_working_dir.clicked.connect(self.define_working_dir)
        self.pushButton_status.clicked.connect(self.status)
        self.pushButton_histogramme.hide()
        self.pushButton_histogramme.clicked.connect(self.main_histogram)
        self.pushButton_plugin_classification.clicked.connect(self.plugin_classification)
        #self.pushButton_kmz.hide()
        self.pushButton_kmz.clicked.connect(self.export_kmz)
        
        self.label_a_s.hide()
        self.label_a_s_img.hide()
        self.label_a_s_img.setPixmap(QtGui.QPixmap(":/plugins/qgiseducation/legende.png"))
        
        
        
        
    def status(self):
        print( self.qgis_education_manager )
        print( "self.mirror_map_tool.dockableMirrors " + str(self.qgis_education_manager.mirror_map_tool.dockableMirrors) )
        print ProcessingManager()
        print ProcessingManager().get_processings_name()
        
        
    def plugin_classification(self):
        self.qgis_education_manager.classif_tool.show()
        self.qgis_education_manager.classif_tool.update_layers( ProcessingManager().get_qgis_working_layers() )
        
        
        
        
    def main_histogram(self):
        self.set_working_message(True)
        if not self.dock_histo_opened:
            self.hist = TerreImageHistogram_multiband(self.qgis_education_manager.layer, self.canvas) 
            self.histodockwidget = Terre_Image_Dock_widget("Histogrammes", self.iface.mainWindow() )
            self.histodockwidget.setObjectName("Histogrammes")
            self.histodockwidget.setWidget(self.hist)
            self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.histodockwidget)
            QtCore.QObject.connect( self.hist, QtCore.SIGNAL( "threshold(PyQt_PyObject)" ), self.histogram_threshold )
            QtCore.QObject.connect( self.histodockwidget, QtCore.SIGNAL( "closed(PyQt_PyObject)" ), self.histogram_closed )
        self.dock_histo_opened = True
        self.set_working_message(False)
        
        
    def histogram_closed(self):
        self.dock_histo_opened = False
        
        
    def histogram(self, layer_source, processing=None, specific_band=-1, hist=None):
        logger.debug( "self.histogram" )
        self.set_working_message(True)
        
        
        if hist == None:
            hist = TerreImageHistogram_monoband(layer_source, self.canvas, processing, specific_band)
        if hist.dock_opened == False:
            histodockwidget = Terre_Image_Dock_widget("Histogrammes", self.iface.mainWindow() )
            histodockwidget.setObjectName("Histogrammes")
            histodockwidget.setWidget(hist)
            histodockwidget.setFloating(True)
            histodockwidget.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
            QtCore.QObject.connect( hist, QtCore.SIGNAL( "threshold(PyQt_PyObject)" ), self.threshold_on_histogram )
            self.iface.addDockWidget(QtCore.Qt.BottomDockWidgetArea, histodockwidget)
            QtCore.QObject.connect( histodockwidget, QtCore.SIGNAL( "closed(PyQt_PyObject)" ), self.histogram_monoband_closed )
            hist.dock_opened = True
        
        
        self.set_working_message(False)
        return hist
    
    
    def histogram_monoband_closed(self):
        logger.info( "QObject.sender() " + str(QtCore.QObject.sender(self)) )
        logger.debug( QtCore.QObject.sender(self).widget() )
        QtCore.QObject.sender(self).widget().dock_opened = False
        
        
        
    def threshold_on_histogram(self, forms):
        logger.debug( "QObject.sender() " + str(QtCore.QObject.sender(self))) 
        logger.debug( "do processing args " + str(forms))
        who = QtCore.QObject.sender(self)
        
        if "Seuillage" in ProcessingManager().get_processings_name():
            processings_seuillage=ProcessingManager().processing_from_name("Seuillage")
            if processings_seuillage:
                processings_seuillage[0].mirror.close()
                QgsMapLayerRegistry.instance().removeMapLayer( processings_seuillage[0].output_working_layer.qgis_layer.id())
                
        self.set_working_message(True)
        my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, who.layer, self.qgis_education_manager.mirror_map_tool, "Seuillage", forms )
        #self.qgis_education_manager.add_processing(my_processing) # TODO : keep it ?
        self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
        self.set_working_message(False)
        
        
    def histogram_threshold(self, forms):
        logger.debug( "educationwidget forms: " +  str(forms))
        self.do_manage_processing("Seuillage", args=forms)
        
#     def histogram_stretching(self, values):
#         logger.debug( "histogram to stretch" + str(values))
#         manage_QGIS.custom_stretch(self.qgis_education_manager.layer.qgis_layer, values, self.canvas)
        
        
    def do_manage_histograms(self, text_changed):
        logger.debug( "text changed histogram: " + text_changed)
        if text_changed == "Image de travail":
            self.main_histogram()
        elif text_changed != "Histogrammes" and text_changed != "":
            # find the layer corresponding to the name
            process = self.qgis_education_manager.name_to_processing[text_changed]
            if process :
                specific_band = -1
                
                if text_changed == "Couleurs naturelles":
                    logger.debug( "text changed couleurs naturelles" )
                    self.set_working_message(True)
                    if not process.histogram:
                        hist = TerreImageHistogram_multiband(self.qgis_education_manager.layer, self.canvas, None, process)
                        process.histogram = hist
                        self.histogram(process.output_working_layer, process, specific_band, hist)
                else:
                    logger.debug("working layer" )
                    bs = ["rouge", "verte", "bleue", "pir", "nir"]
                    corres = {"rouge":process.layer.red, "verte":process.layer.green, "bleue":process.layer.blue, "pir":process.layer.pir, "mir":process.layer.mir}
                    logger.debug( "corres: " + str(corres) )
                    
                    for item in bs:
                        if item in text_changed:
                            logger.debug( "bande à afficher : " + str(corres[item]))
                            specific_band = corres[item]
                            
                            
                    logger.debug( "specific band: " + str(specific_band))
                    
                            
                            
                    if not process.histogram:
                        logger.debug( "process: " + str(process) + " " + str(type(process)))
                        logger.debug( "type(process.output_working_layer): " + str(type(process.output_working_layer)))
                        logger.debug( "histogram to display: " + str(process.output_working_layer.get_source()))
                        # display the histogram of the layer
                        
                        hist = self.histogram( process.output_working_layer, process, specific_band )
                        process.histogram = hist
                    else :
                        hist = self.histogram( process.output_working_layer, process, specific_band,  process.histogram)
        self.comboBox_histogrammes.setCurrentIndex( 0 )
                    
        
    def define_working_dir(self):
        output_dir = terre_image_utils.getOutputDirectory(self)
        self.qgis_education_manager.working_directory = output_dir
        
        
    def do_manage_processing(self, text_changed, args=None):
        #print "text_changed", text_changed
        if text_changed  == "Angle Spectral":
            print "text changed angle spectral"
            for item in self.iface.mapCanvas().scene().items():
                if isinstance(item, QgsRubberBand):
                    item.reset(QGis.Point)
            processings_spectral_angle=ProcessingManager().processing_from_name("Angle Spectral")
            if processings_spectral_angle:
                processings_spectral_angle[0].mirror.close()
                ProcessingManager().remove_processing(processings_spectral_angle) 
        if text_changed  == "Seuillage":
            if "Seuillage" in ProcessingManager().get_processings_name():
                processings_seuillage=ProcessingManager().processing_from_name("Seuillage")
                if processings_seuillage:
                    processings_seuillage[0].mirror.close()
                    ProcessingManager().remove_processing(processings_seuillage) 
        do_it = True
        logger.debug( "do processing args: " + str(args))
        if text_changed:
            if not text_changed == "Traitements...":
                if text_changed in ["NDVI", "NDTI", "Indice de brillance"]:
                    if text_changed in ProcessingManager().get_processings_name() :
                        do_it = False
                if text_changed in [ "Seuillage", "Angle Spectral" ]:
                    p = [process.processing_name for process in ProcessingManager().processings if process.processing_name==text_changed]
                    if p:
                        process = p[0]
                        try:
                            QgsMapLayerRegistry.instance().removeMapLayer( process.get_output_working_layer().qgis_layer.id())
                        except AttributeError:
                            print 'Failed to delete ', process
                    if text_changed == "Angle Spectral":
                        widget = self.iface.messageBar().createMessage("Terre Image", "Cliquez sur un point de l'image pour en obtenir son angle spectral...")
                        self.iface.messageBar().pushWidget(widget, QgsMessageBar.INFO)
                if do_it:
                    if not text_changed == "Angle Spectral":
                        self.set_working_message(True)
                    
                    
                    logger.debug( "text changed: " + text_changed)
                    my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.qgis_education_manager.layer, self.qgis_education_manager.mirror_map_tool, text_changed, args )
                    if text_changed == "Angle Spectral":
                        self.set_working_message(True)
                        self.label_a_s.show()
                        self.label_a_s_img.show()
                        self.qgis_education_manager.has_spectral_angle = True
                        QtCore.QObject.connect( my_processing, QtCore.SIGNAL( "display_ok()" ), lambda who=my_processing: self.processing_end_display(who) )
                    if not text_changed == "Angle Spectral":
                        self.qgis_education_manager.add_processing(my_processing)
                        self.set_combobox_histograms()
                        self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
                        self.set_working_message(False)
            self.comboBox_processing.setCurrentIndex( 0 )
            
        
    def processing_end_display(self, my_processing):
        logger.debug( "processing_end_display" )
        self.qgis_education_manager.add_processing(my_processing)
        self.set_combobox_histograms()
        self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
        self.set_working_message(False)
        
        
    def set_comboBox_sprectral_band_display( self ):
        if self.qgis_education_manager.layer:
            bands = self.qgis_education_manager.layer.bands
            corres = { 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
        
            self.comboBox_sprectral_band_display.clear()
            self.comboBox_sprectral_band_display.insertItem( 0, "Affichage des bandes spectrales..." )
            
            if self.qgis_education_manager.layer.has_natural_colors():
                logger.debug( "couleurs naturelles")
                self.comboBox_sprectral_band_display.insertItem( 1, "Afficher en couleurs naturelles" )
            
            for i in range(self.qgis_education_manager.layer.get_band_number()):
                y=[x for x in bands if bands[x]==i+1]
                if y :
                    text = corres[y[0]]
                    self.comboBox_sprectral_band_display.insertItem( i+2, text )
            self.comboBox_sprectral_band_display.currentIndexChanged[str].connect(self.do_manage_sprectral_band_display)
            
            
    def set_combobox_histograms(self):
        if self.qgis_education_manager:
            if self.qgis_education_manager.layer:
                process = ["Histogrammes", "Image de travail"] + [x for x in ProcessingManager().get_processings_name() if x not in ["KMEANS", "Seuillage"]]
                logger.debug( "process: " + str(process)) 
                
                self.comboBox_histogrammes.clear()
                
                for i in range(len(process)):
                    self.comboBox_histogrammes.insertItem( i, process[i] )
                self.comboBox_histogrammes.currentIndexChanged[str].connect(self.do_manage_histograms)
            
            
    def do_manage_sprectral_band_display(self, text_changed):
        do_it = True
        if text_changed and text_changed != "Affichage des bandes spectrales...":
            band_to_display = None
            corres = { 'nat':"Afficher en couleurs naturelles", 'red':"Afficher la bande rouge", 'green':"Afficher la bande verte", 'blue':"Afficher la bande bleue", 'pir':"Afficher la bande pir", 'mir':"Afficher la bande mir" }
            corres_name_view = { 'nat':"Couleurs naturelles", 'red':"Bande rouge", 'green':"Bande verte", 'blue':"Bande bleue", 'pir':"Bande pir", 'mir':"Bande mir" }
            for key in corres:
                if corres[key] == text_changed :
                    who = key
                    logger.debug( "do_manage_sprectral_band_display who: " + str(who))
                    if corres_name_view[who] in ProcessingManager().get_processings_name() :
                        do_it = False
                    #band_to_display = self.qgis_education_manager.layer.bands[key]
                    #manage_QGIS.display_one_band(self.qgis_education_manager.layer, who, self.iface)
                    if do_it :
                        my_processing = TerreImageDisplay( self.iface, self.qgis_education_manager.working_directory, self.qgis_education_manager.layer, self.qgis_education_manager.mirror_map_tool, who )
                        self.qgis_education_manager.add_processing(my_processing)
                        self.set_combobox_histograms()
                    break
            self.comboBox_sprectral_band_display.setCurrentIndex( 0 )
        
        
    def display_values(self):
        self.qgis_education_manager.display_values()

                 
    def kmeans(self):
        self.set_working_message(True)
        
        if self.qgis_education_manager.layer == None :
            logger.debug( "Aucune layer selectionnée" )
        else :
            nb_class = self.spinBox_kmeans.value()
            logger.debug( "nb_colass from spinbox: " + str(nb_class))
            my_processing = TerreImageProcessing( self.iface, self.qgis_education_manager.working_directory, self.qgis_education_manager.layer, self.qgis_education_manager.mirror_map_tool, "KMEANS", nb_class )
            self.qgis_education_manager.add_processing(my_processing)
            self.set_combobox_histograms()
            
            self.qgis_education_manager.value_tool.set_layers(ProcessingManager().get_working_layers())
            #terre_image_processing.kmeans(self.qgis_education_manager.layer, self.qgis_education_manager.working_directory, self.iface, nb_class)
            self.set_working_message(False)


    def export_kmz(self):
        self.set_working_message(True)
        files_to_export = [process.output_working_layer.get_source() for process in ProcessingManager().get_processings()]
        logger.debug( "files to export" + str(files_to_export))
        kmz = terre_image_processing.export_kmz( files_to_export, self.qgis_education_manager.working_directory )
        self.set_working_message(False)
    
#     def spectral_angles( self ):
#         self.angle_tool.get_point_for_angles(self.layer)


    def layer_deleted(self, layer_id):
        #logger.debug( str(layer_id) + " deleted")
        
        if "Angle_Spectral" in str(layer_id):
            #delete rubberband
            for item in self.iface.mapCanvas().scene().items():
                if isinstance(item, QgsRubberBand):
                    item.reset(QGis.Point)
            #hide legend
            self.label_a_s.hide()
            self.label_a_s_img.hide()
        
        
        if self.qgis_education_manager:
            logger.debug( "self.qgis_education_manager.layer.get_qgis_layer().id(): " +  str(self.qgis_education_manager.layer.get_qgis_layer().id()))
            if self.qgis_education_manager.layer.get_qgis_layer().id() == layer_id:
                self.disconnect_interface()
            else:
                self.qgis_education_manager.removing_layer(layer_id)
                
        ProcessingManager().remove_process_from_layer_id(layer_id)   
        self.set_combobox_histograms()

    def disconnect_interface(self):
        
        if self.qgis_education_manager:
            self.qgis_education_manager.disconnect()
        
        #histograms
        try :
            self.hist.close()
            self.hist = None
        except AttributeError:
            pass
        
        #rubberband
        if self.dock_histo_opened:
            # remove the dockwidget from iface
            self.iface.removeDockWidget(self.histodockwidget)

        
        # disable working layer
        self.qgis_education_manager = None
        self.emit( QtCore.SIGNAL("terminated()") )
        
        
    def set_working_message(self, set=True):
        if set :
            widget = self.iface.messageBar().createMessage("Terre Image", "Travail en cours...")
            self.iface.messageBar().pushWidget(widget, QgsMessageBar.INFO)
            self.iface.mainWindow().statusBar().showMessage("Terre Image : Travail en cours...")
            self.iface.messageBar().pushMessage("Terre Image", "Travail en cours...")
        else :
            self.iface.messageBar().popWidget()
            self.iface.messageBar().clearWidgets()
            self.iface.mainWindow().statusBar().clearMessage()
        
    def disconnectP(self):
        """
        Disconnection of signals, go back to the main interface
        """
        #self.changeActive(False)
        #QtCore.QObject.disconnect(self.canvas, SIGNAL( "keyPressed( QKeyEvent * )" ), self.pauseDisplay )
        self.iface.mainWindow().statusBar().showMessage( "" ) 
