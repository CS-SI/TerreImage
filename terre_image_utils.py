# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-05-13
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
import datetime
import shutil

from working_layer import WorkingLayer
from manage_bands import manage_bands
import manage_QGIS
import terre_image_processing
from terre_image_constant import TerreImageConstant
from processing_manager import ProcessingManager


from PyQt4.QtGui import QFileDialog, QMessageBox
from PyQt4.QtCore import QDir, QSettings

from osgeo import gdal
import subprocess

#import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger( 'Terre_Image_Utils' )
logger.setLevel(logging.INFO)

def fill_default_directory( ):
    """
    Creates working directory 
    Fills the output directory line edit if ui given
    """
    datetimeNow = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    currentDirectory = os.path.join( os.getenv("HOME"), "TerreImage", datetimeNow )
    if not os.path.exists( currentDirectory ):
        os.makedirs( currentDirectory )
    return currentDirectory, datetimeNow


def getOutputDirectory( ui ):
    """
    Opens a dialog to get the output directory
    """
    if ui.lineEdit_working_dir.text():
        path = ui.lineEdit_working_dir.text()
    else:
        path = QDir.currentPath()
    outputDirectory = ""
    dirDest = QFileDialog.getExistingDirectory( None, str( "Répertoire de destination des fichiers de TerreImage" ), path )
    if dirDest :
        ui.lineEdit_working_dir.setText( dirDest )
        outputDirectory = dirDest
        update_subdirectories( outputDirectory )
        
    return str( outputDirectory )


def update_subdirectories( outputDirectory ):
    """
    Create sub directories for the processings:
    
        Classification : this directory will contain the results of the classification
        KMZ            : this directory will contain the internal files generated by KMZ Export
        KMEans         : this directory will contain the internal files of the kmeans process
    """
    sub = ['Classification', 'Internal']
    for item in sub: 
        if not os.path.exists( os.path.join(outputDirectory, item) ):
            os.makedirs( os.path.join(outputDirectory, item) )
    
    

def working_layer(canvas):
    source = canvas.currentLayer().source()
    layer = WorkingLayer(source, canvas.currentLayer())
    
    
    #self.layer = self.canvas.currentLayer()
    if layer :
        #self.define_bands(self.layer)
        #manage_bands()
        #self.red, self.green, self.blue, self.pir, self.mir = manage_bands().get_values()
        red, green, blue, pir, mir = manage_bands().get_values()
        
        bands = { 'red':red, 'green':green, 'blue':blue, 'pir':pir, 'mir':mir }
        layer.set_bands(bands)
        
        
        logger.debug( str(red) + " " + str(green) + " " + str(blue) + " " + str(pir) + " " + str(mir))
        return layer
        
def set_current_layer(iface):
    layer, bands  = get_workinglayer_on_opening( iface )
    if layer:
        working_directory = os.path.join(os.path.dirname(layer.source_file), "working_directory")
        update_subdirectories(working_directory)
        if not os.path.exists( working_directory ):
            os.makedirs( working_directory )
        ProcessingManager().working_layer = layer
        #self.classif_tool.set_layers(ProcessingManager().get_qgis_working_layers(), self.layer.get_qgis_layer(), self.layer.band_invert)
        #self.classif_tool.set_directory(self.working_directory)
        #self.classif_tool.setupUi()
        #layers_for_value_tool.append(layer ) #.get_qgis_layer())
        logger.debug( "working directory" + working_directory )
    
        return layer, bands, working_directory
    return None, None, None
        
def get_workinglayer_on_opening(iface):
    settings = QSettings()
    lastFolder = settings.value("terre_image_lastFolder")
    
    if lastFolder:
        path = lastFolder
    else:
        path = QDir.currentPath()
        
        
    fileOpened = unicode(QFileDialog.getOpenFileName( None, "Selectionner un fichier raster", path ))
    
    settings.setValue("terre_image_lastFolder", os.path.dirname(fileOpened))
    settings.sync()
    
    print type(fileOpened)
    

    if fileOpened:
#         try:
#             str(fileOpened)
#         except UnicodeEncodeError:
#             QMessageBox.warning( None , "Erreur", u'L\'image que vous essayez d\'ouvrir contient un ou des caractères spéciaux. La version actuelle du plugin ne gère pas ce type de fichiers.', QMessageBox.Ok )
#             return None, None
#         else:
#             if fileOpened.find(" ") != -1:
#                 QMessageBox.warning( None , "Attention", u'L\'image que vous essayez d\'ouvrir contient un ou plusieurs espaces. Les traitements sur cette image provoqueront une erreur.'.encode('utf8'), QMessageBox.Ok )
            
            
        if fileOpened.endswith( ".qgs" ):
            #open new qgis project
            pass
        else :
            raster_layer = manage_QGIS.get_raster_layer(fileOpened, os.path.splitext(os.path.basename(fileOpened))[0])
             
            type_image = terre_image_processing.get_sensor_id(fileOpened)
            logger.debug( "type_image " + str(type_image) )
            layer = WorkingLayer( fileOpened, raster_layer )
            layer.set_type(type_image)
            #self.layer = self.canvas.currentLayer()
            if layer :
                #self.define_bands(self.layer)
                #manage_bands()
                #self.red, self.green, self.blue, self.pir, self.mir = manage_bands().get_values()
                red, green, blue, pir, mir = manage_bands(type_image, layer.get_band_number()).get_values()
                
                if red != -1 or green != -1 or blue != -1 or pir != -1 or mir != -1:
                    all_set = True
                    bands = { 'red':red, 'green':green, 'blue':blue, 'pir':pir, 'mir':mir }
#                         for i in bands.values():
#                             if bands.values().count(i) > 1:
#                                 doublon = True
#                                 break
#                         if not doublon :
                    for i in range(1,layer.get_band_number()+1):
                        if not i in bands.values():
                            all_set=False
                    if all_set:
                        
                    
                        layer.set_bands(bands)
                        
                        logger.debug( str(red) + " " + str(green) + " " + str(blue) + " " + str(pir) + " " + str(mir))
                        
                        cst = TerreImageConstant()
                        cst.index_group = cst.iface.legendInterface().addGroup( "Terre Image", True, None )
                        
                        
                        manage_QGIS.add_qgis_raser_layer(raster_layer, iface.mapCanvas(), bands)
                        compute_overviews(fileOpened)
                        return layer, bands
                    else:
                        QMessageBox.warning( None , "Erreur", u'Il y a un problème dans la définition des bandes spectrales.', QMessageBox.Ok )
                        return None, None
                else:
                    return None, None
    else:
        return None, None
    
def restore_working_layer( filename, bands, type ):
    raster_layer = manage_QGIS.get_raster_layer(filename, os.path.splitext(os.path.basename(filename))[0])
    layer = WorkingLayer( filename, raster_layer )
    layer.set_type(type)
    layer.set_bands(bands)
    return layer, bands
    
    
    
def computeStatistics( OneFeature, i, j=None, nodata=True ):
    """
    From the given feature, computes its statistics
    
    Keyword Arguments :
        OneFeature    --    raster layer to analyze
        i             --    only for debugging
    """
    
    logger.debug("one feature : " + OneFeature )
    
    #saving the feature only for testing
    outOne = OneFeature + str( i ) + ".tif" 
    shutil.copy( OneFeature, outOne )
    logger.debug( outOne )
    #/testing
    
    dataset = gdal.Open(str(OneFeature), gdal.GA_ReadOnly)
    # dataset  : GDALDataset
    if dataset is None:
        print "Error : Opening file ", OneFeature
    else :
        if j == None :
            band = dataset.GetRasterBand(1)
        else :
            band = dataset.GetRasterBand(j)
        if nodata :
            band.SetNoDataValue(0)
        stats = band.ComputeStatistics(False)
        
        logger.debug( "Feature " + str(i) + " : " )
        logger.debug( stats )
        return stats
        
    dataset = None
    return None    
    
    
def compute_overviews(filename):
    if not os.path.isfile(filename + ".ovr"):
        command = "gdaladdo "
        command += " -ro "
        command += "\"" + filename + "\""
        command += " 2 4 8 16"
        logger.debug( "command to run" + command)
        fused_command = command.split(" ")
        #os.system(command)
        subprocess.call(fused_command)
    
    
        
        