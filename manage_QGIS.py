# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2013-11-21
        copyright            : (C) 2013 by CS Systèmes d'Information
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
#import system libraries
import os
import random

# Import the PyQt
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPen, QColor

# import GDAL and QGIS libraries
from qgis.core import ( QGis, 
                        QgsMapLayerRegistry, 
                        QgsApplication, 
                        QgsMapLayer,
                        QgsRasterDataProvider,
                        QgsContrastEnhancement,
                        QgsRendererRangeV2,
                        QgsCsException,
                        QgsSymbolV2,
                        QgsVectorLayer,
                        QgsRasterLayer,
                        QgsRaster,
                        QgsGraduatedSymbolRendererV2,
                        QgsMultiBandColorRenderer
                        )


import terre_image_utils


def addVectorLayerToQGIS( vectorLayer, layername, legendInterface ):
    """
    Add a vector layer to QGIS
    
    Keyword arguments :
        vectorLayer    --    vector layer to add
        layername      --    name to display in QGIS
        indexGroup     --    index of the group in QGIS where to add the layer.
                             If None given, the layer is added at the root in QGIS.
                             By default, None. 
        color          --    If need to color laer with special method. By default False.
        colorByClasses --    Applies a specific lut to colorize field "classif" in vectorlayer
        fieldToColor   --    Field to be based to colorize the vector
        
    Example of use :
    myvector = "/home/user/myVectorLayer.shp"
    addVectorLayerToQGIS( myvector, os.path.basename(myvector), None, True)
    """
    vector = QgsVectorLayer( vectorLayer, layername, "ogr" )
    layerAdded = QgsMapLayerRegistry.instance().addMapLayer( vector )

      
def get_raster_layer( raster, name ):
    rasterLayer = QgsRasterLayer( raster, name )
    return rasterLayer



def add_qgis_raser_layer( rasterLayer, bands=None):
    if bands:
        print bands
        pir = bands['pir']
        red = bands['red']
        green = bands['green']
        print 'pir', pir
        print "red", red
        print "green", green
        if pir and red and green:
            renderer = rasterLayer.renderer()
            #rasterLayer.setDrawingStyle("MultiBandColor")
            renderer.setRedBand(pir)
            renderer.setGreenBand(red)
            renderer.setBlueBand(green)
            #rasterLayer.setRenderer( renderer )
        contrastForRasters( rasterLayer, 0, 0 )
    
    
    QgsMapLayerRegistry.instance().addMapLayer( rasterLayer )
      
      
def addRasterLayerToQGIS( raster, layername, iface = None ):
    """
    Add the given raster to qgis and improve contrast between min max
    
    Keyword arguments:
        raster        --    raster filename to add to QGIS
        layername     --    name to given to the raster layer for display
        indexGroup    --    index of the QGIS group where to move the layer
    """
    if layername == None :
        layername = os.path.basename( raster )
    
    rasterLayer = QgsRasterLayer( raster, layername )
    
    
    QgsMapLayerRegistry.instance().addMapLayer( rasterLayer )
    return rasterLayer
        

def contrastForRasters( theRasterLayer, minLayer, maxLayer ):
    """
    Applies a contrast between min and max. If given min and max are 0, then calculates the min and max from gdal.
    """
    # type of layer : raster, vector, other
    typeOfLayer = theRasterLayer.type()
     
    #take the layer renderer to get the min and max 
    layerRenderer = theRasterLayer.renderer() # for qgis > 1.9
    dataProvider = theRasterLayer.dataProvider()
     
    # the layer has to be a raster layer
    if typeOfLayer == 1 :
        if theRasterLayer.rasterType() == 0 and layerRenderer:
            #gray band
            #layerRenderer <qgis.core.QgsSingleBandGrayRenderer object at 0x514caf0>
            layerCE = layerRenderer.contrastEnhancement()
            # take the contrast enhancement of the layer threw the renderer
            if layerCE :
                layerCE.setContrastEnhancementAlgorithm(1) #qgis 1.9
                layerCE.setMinimumValue( minLayer )
                layerCE.setMaximumValue( maxLayer )
        elif theRasterLayer.rasterType() == 2  and layerRenderer:
            if minLayer == 0 and maxLayer == 0 :
                min1, max1, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(),0, 1)
                min2, max2, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(),0, 2)
                min3, max3, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(),0, 3)
                #print min1, max1, min2, max2, min3, max3
                layerCERed = layerRenderer.redContrastEnhancement()
                layerCEGreen = layerRenderer.greenContrastEnhancement()
                layerCEBlue = layerRenderer.blueContrastEnhancement()
                redEnhancement = QgsContrastEnhancement( dataProvider.dataType( 0 ) )
                greenEnhancement = QgsContrastEnhancement( dataProvider.dataType( 1 ) )
                blueEnhancement = QgsContrastEnhancement( dataProvider.dataType( 2 ) )
                if layerCERed and layerCEGreen and layerCEBlue:
                    #set stretch to min max
                    redEnhancement.setMinimumValue( min1 )
                    redEnhancement.setMaximumValue( max1 )
                    greenEnhancement.setMinimumValue( min2 )
                    greenEnhancement.setMaximumValue( max2 )
                    blueEnhancement.setMinimumValue( min3 )
                    blueEnhancement.setMaximumValue( max3 )
                    redEnhancement.setContrastEnhancementAlgorithm(1)
                    greenEnhancement.setContrastEnhancementAlgorithm(1)
                    blueEnhancement.setContrastEnhancementAlgorithm(1)
                    layerRenderer.setRedContrastEnhancement( redEnhancement )
                    layerRenderer.setGreenContrastEnhancement( greenEnhancement )
                    layerRenderer.setBlueContrastEnhancement( blueEnhancement )
        theRasterLayer.triggerRepaint()
        
        
        
def display_one_band( layer, keyword ): 
    corres = { 'red':"_bande_rouge", 'green':"_bande_verte", 'blue':"_bande_bleue", 'pir':"_bande_pir", 'mir':"_bande_mir" }
    
    rasterLayer = QgsRasterLayer( layer.get_source(), layer.name() + corres[keyword] )
    
    
    band = layer.bands[keyword]
    if band :
        print "band num:", band
        rasterLayer.setDrawingStyle("MultiBandSingleBandGray")
        renderer = rasterLayer.renderer()
        print renderer
        renderer.setGrayBand(band)
        
        #contrastForRasters( rasterLayer, 0, 0 )
        
        QgsMapLayerRegistry.instance().addMapLayer( rasterLayer )
        return rasterLayer
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    