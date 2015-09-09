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
# import system libraries
import os

# Import the PyQt
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QColor

# import GDAL and QGIS libraries
from qgis.core import (QgsMapLayerRegistry,
                        QgsMapLayer,
                        QgsContrastEnhancement,
                        QgsVectorLayer,
                        QgsRasterLayer,
                        QgsRaster,
                        QgsField,
                        QgsFeature,
                        QgsGeometry,
                        )

import terre_image_utils
from terre_image_constant import TerreImageConstant

# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_manageQGIS')
logger.setLevel(logging.INFO)



# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_manageQGIS')
logger.setLevel(logging.DEBUG)


def addVectorLayerToQGIS(vectorLayer, layername, legendInterface):
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
    vector = QgsVectorLayer(vectorLayer, layername, "ogr")
    layerAdded = QgsMapLayerRegistry.instance().addMapLayer(vector)


def get_raster_layer(raster, name):
    rasterLayer = QgsRasterLayer(raster, name)
    return rasterLayer


def add_qgis_raser_layer(rasterLayer, canvas, bands=None):
    index_group = TerreImageConstant().index_group
    logger.debug("index_group: " + str(index_group))

    if bands:
        if rasterLayer.rasterType() == 2:
            logger.debug(bands)
            pir = bands['pir']
            red = bands['red']
            green = bands['green']
            logger.debug('pir: ' + str(pir))
            logger.debug("red: " + str(red))
            logger.debug("green: " + str(green))
            if pir and red and green:
                renderer = rasterLayer.renderer()
                # rasterLayer.setDrawingStyle("MultiBandColor")
                renderer.setRedBand(pir)
                renderer.setGreenBand(red)
                renderer.setBlueBand(green)
                # rasterLayer.setRenderer( renderer )
            # contrastForRasters( rasterLayer, 0, 0, [pir, red, green] )
            histogram_stretching(rasterLayer, canvas)


    QgsMapLayerRegistry.instance().addMapLayer(rasterLayer)
    TerreImageConstant().legendInterface.moveLayer(rasterLayer, index_group)


def addRasterLayerToQGIS(raster, layername, iface=None):
    """
    Add the given raster to qgis and improve contrast between min max

    Keyword arguments:
        raster        --    raster filename to add to QGIS
        layername     --    name to given to the raster layer for display
        indexGroup    --    index of the QGIS group where to move the layer
    """
    index_group = TerreImageConstant().index_group
    if not index_group:
        index_group = 0

    logger.debug("index_group: " + str(index_group))

    if layername == None :
        layername = os.path.basename(raster)

    rasterLayer = QgsRasterLayer(raster, layername)
    histogram_stretching(rasterLayer, iface.mapCanvas())

    QgsMapLayerRegistry.instance().addMapLayer(rasterLayer)
    TerreImageConstant().legendInterface.moveLayer(rasterLayer, index_group)
    return rasterLayer


def histogram_stretching(raster_layer, canvas):
# histogramStretch( true, QgsRaster::ContrastEnhancementCumulativeCut );
# theLimits =QgsRaster::ContrastEnhancementCumulativeCut
#   QgsRectangle myRectangle;
#   if ( visibleAreaOnly )
#     myRectangle = mMapCanvas->mapRenderer()->outputExtentToLayerExtent( myRasterLayer, mMapCanvas->extent() );
#
#   myRasterLayer->setContrastEnhancement( QgsContrastEnhancement::StretchToMinimumMaximum, theLimits, myRectangle );
#
#   myRasterLayer->setCacheImage( NULL );
#   mMapCanvas->refresh();
    theLimits = QgsRaster.ContrastEnhancementCumulativeCut
    logger.debug("theLimits " + str(theLimits))
    raster_layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, theLimits)
    raster_layer.setCacheImage(None)
    canvas.refresh()
    canvas.repaint()


def histogram_stretching_for_threshold(raster_layer, canvas):
# histogramStretch( true, QgsRaster::ContrastEnhancementCumulativeCut );
# theLimits =QgsRaster::ContrastEnhancementCumulativeCut
#   QgsRectangle myRectangle;
#   if ( visibleAreaOnly )
#     myRectangle = mMapCanvas->mapRenderer()->outputExtentToLayerExtent( myRasterLayer, mMapCanvas->extent() );
#
#   myRasterLayer->setContrastEnhancement( QgsContrastEnhancement::StretchToMinimumMaximum, theLimits, myRectangle );
#
#   myRasterLayer->setCacheImage( NULL );
#   mMapCanvas->refresh();
    theLimits = QgsRaster. ContrastEnhancementMinMax
    logger.debug("theLimits " + str(theLimits))
    raster_layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, theLimits)
    raster_layer.setCacheImage(None)
    canvas.refresh()
    canvas.repaint()

def get_min_max_via_qgis(theRasterLayer, num_band):
#     my_raster_stats = theRasterLayer.dataProvider().bandStatistics( num_band )#, 2, 98  )
#     my_min = my_raster_stats.minimumValue
#     my_max = my_raster_stats.maximumValue
#
    data_p = theRasterLayer.dataProvider()
    my_min, my_max = theRasterLayer.dataProvider().cumulativeCut(num_band, 0.2, 0.98);
    min, max = data_p.cumulativeCut(num_band, 0.02, 0.98)
    logger.debug("qgis min max :" + str(my_min) + str(my_max))
    logger.debug("min max 2 : " + str(min) + str(max))
    return my_min, my_max


def contrastForRasters(theRasterLayer, minLayer, maxLayer, band=None):
    """
    Applies a contrast between min and max. If given min and max are 0, then calculates the min and max from gdal.
    """
    # type of layer : raster, vector, other
    typeOfLayer = theRasterLayer.type()

    # take the layer renderer to get the min and max
    layerRenderer = theRasterLayer.renderer()  # for qgis > 1.9
    dataProvider = theRasterLayer.dataProvider()

    # the layer has to be a raster layer
    if typeOfLayer == 1 :
        if theRasterLayer.rasterType() == 0 and layerRenderer:
            # gray band
            # layerRenderer <qgis.core.QgsSingleBandGrayRenderer object at 0x514caf0>
            layerCE = layerRenderer.contrastEnhancement()
            # take the contrast enhancement of the layer threw the renderer
            if layerCE :
                layerCE.setContrastEnhancementAlgorithm(3)  # qgis 1.9
                layerCE.setMinimumValue(minLayer)
                layerCE.setMaximumValue(maxLayer)
        elif theRasterLayer.rasterType() == 2  and layerRenderer:
            if minLayer == 0 and maxLayer == 0 :
                if band:
                    min1, max1 = get_min_max_via_qgis(theRasterLayer, band[0])
                    min2, max2 = get_min_max_via_qgis(theRasterLayer, band[1])
                    min3, max3 = get_min_max_via_qgis(theRasterLayer, band[2])

# #                     min1, max1, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(),0, band[0])
# #                     min2, max2, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(),0, band[1])
# #                     min3, max3, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(),0, band[2])
# #                     #print min1, max1, min2, max2, min3, max3
                else:
                    min1, max1, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(), 0, 1)
                    min2, max2, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(), 0, 2)
                    min3, max3, _, _ = terre_image_utils.computeStatistics(theRasterLayer.source(), 0, 3)

                redEnhancement = QgsContrastEnhancement(dataProvider.dataType(0))
                greenEnhancement = QgsContrastEnhancement(dataProvider.dataType(1))
                blueEnhancement = QgsContrastEnhancement(dataProvider.dataType(2))
                # set stretch to min max
                redEnhancement.setMinimumValue(min1)
                redEnhancement.setMaximumValue(max1)
                greenEnhancement.setMinimumValue(min2)
                greenEnhancement.setMaximumValue(max2)
                blueEnhancement.setMinimumValue(min3)
                blueEnhancement.setMaximumValue(max3)
                redEnhancement.setContrastEnhancementAlgorithm(3)
                greenEnhancement.setContrastEnhancementAlgorithm(3)
                blueEnhancement.setContrastEnhancementAlgorithm(3)
                layerRenderer.setRedContrastEnhancement(redEnhancement)  # , QgsRaster.ContrastEnhancementCumulativeCut  )
                layerRenderer.setGreenContrastEnhancement(greenEnhancement)  # , QgsRaster.ContrastEnhancementCumulativeCut  )
                layerRenderer.setBlueContrastEnhancement(blueEnhancement)  # , QgsRaster.ContrastEnhancementCumulativeCut  )
        theRasterLayer.triggerRepaint()


def display_one_band(layer, keyword, iface):
    index_group = TerreImageConstant().index_group
    logger.debug("keyword " + str(keyword))
    corres = { 'red':"_bande_rouge", 'green':"_bande_verte", 'blue':"_bande_bleue", 'pir':"_bande_pir", 'mir':"_bande_mir", "nat":"_couleurs_naturelles" }

    rasterLayer = QgsRasterLayer(layer.get_source(), layer.name() + corres[keyword])

    if keyword == 'nat':
        logger.debug("display on natural colors")
        band_red = layer.bands['red']
        band_green = layer.bands['green']
        band_blue = layer.bands['blue']
        renderer = rasterLayer.renderer()
        # rasterLayer.setDrawingStyle("MultiBandColor")
        renderer.setRedBand(band_red)
        renderer.setGreenBand(band_green)
        renderer.setBlueBand(band_blue)
        # rasterLayer.setRenderer( renderer )
        # contrastForRasters( rasterLayer, 0, 0, [pir, red, green] )
        histogram_stretching(rasterLayer, iface.mapCanvas())
        QgsMapLayerRegistry.instance().addMapLayer(rasterLayer)
        TerreImageConstant().legendInterface.moveLayer(rasterLayer, index_group)
        return rasterLayer
    else:

        band = layer.bands[keyword]
        if band :
            logger.debug("band num: " + str(band))
            rasterLayer.setDrawingStyle("MultiBandSingleBandGray")
            renderer = rasterLayer.renderer()
            logger.debug(renderer)
            renderer.setGrayBand(band)

            # contrastForRasters( rasterLayer, 0, 0 )
            histogram_stretching(rasterLayer, iface.mapCanvas())
            QgsMapLayerRegistry.instance().addMapLayer(rasterLayer)
            TerreImageConstant().legendInterface.moveLayer(rasterLayer, index_group)
            return rasterLayer


def show_clicked_point(point, name, iface, vl=None):
    """ Displays the extent from the listeOfPoints

        Keyword arguments:
            listPoints        --    list of point to draw the extent
            name              --    name of the layer to display the extent name_extent
            indexGroupProduct --    index of the product group in qgis where to move the layers
    """
    canvas = iface.mapCanvas()

    # set True to set a define color to the extent and the world
    setColor = False

    # create layer
    # if vl == None :
    vl = QgsVectorLayer("Point?crs=epsg:4326", name, "memory")
    pr = vl.dataProvider()

    # add fields
    pr.addAttributes([ QgsField("spectral_angle", QVariant.String) ])

    # add a feature
    fet = QgsFeature()

    geometry = QgsGeometry.fromPoint(point)

    # fet.setGeometry( qgis.core.QgsGeometry.fromPolygon( qgis.core.QgsGeometry.\
    # QgsPolygon(4.45 43.95, 4.45 44.400433068, 5.000403625 44.400433068,5.000403625 43.95) ) )
    fet.setGeometry(geometry)

    # ( 4.45, 43.95 ) to (5.000403625, 44.400433068 )
    pr.addFeatures([ fet ])

    # set color to the extent
    if setColor:
        if vl.isUsingRendererV2():
            # new symbology - subclass of qgis.core.QgsFeatureRendererV2 class
            rendererV2 = vl.rendererV2()
            symbol = rendererV2.symbol()
            for i in xrange(symbol.symbolLayerCount()):
                symbol.symbolLayer(i).setColor(QColor(168, 255, 0))


    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    vl.updateExtents()

    layersAdded = QgsMapLayerRegistry.instance().addMapLayers([vl])
    return vl


def custom_stretch(theRasterLayer, values, canvas, mono=False):
    """
    Applies a contrast between min and max. If given min and max are 0, then calculates the min and max from gdal.
    """
#     logger.info("#######################")
    logger.info("custom stretch: values")
    logger.info(values)

    # print "custom stretch"
    # print canvas
    # print "layer :", theRasterLayer

    # type of layer : raster, vector, other
    typeOfLayer = theRasterLayer.type()

    # take the layer renderer to get the min and max
    layerRenderer = theRasterLayer.renderer()  # for qgis > 1.9
    dataProvider = theRasterLayer.dataProvider()

    # print "values", values
    # the layer has to be a raster layer
    if typeOfLayer == 1 :
        if (theRasterLayer.rasterType() == 0 or mono) and layerRenderer:
            min_layer, max_layer = values[0]
            # gray band
            # layerRenderer <qgis.core.QgsSingleBandGrayRenderer object at 0x514caf0>
            grayEnhancement = QgsContrastEnhancement(dataProvider.dataType(1))
            # take the contrast enhancement of the layer threw the renderer
            if grayEnhancement :
                grayEnhancement.setContrastEnhancementAlgorithm(1)  # qgis 1.9
                grayEnhancement.setMinimumValue(min_layer)
                grayEnhancement.setMaximumValue(max_layer)
                layerRenderer.setContrastEnhancement(grayEnhancement)

        elif theRasterLayer.rasterType() == 2  and layerRenderer:
            # print "layer 3 bandes"
            min_red, max_red = values[0]
            min_green, max_green = values[1]
            min_blue, max_blue = values[2]
            logger.debug("red : " + str(min_red) + " " + str(max_red))
            logger.debug("green : " + str(min_green) + " " + str(max_green))
            logger.debug("blue : " + str(min_blue) + " " + str(max_blue))

            redEnhancement = QgsContrastEnhancement(dataProvider.dataType(1))
            greenEnhancement = QgsContrastEnhancement(dataProvider.dataType(2))
            blueEnhancement = QgsContrastEnhancement(dataProvider.dataType(3))
            logger.debug("redEnhancement : " + str(redEnhancement))
            logger.debug("greenEnhancement : " + str(greenEnhancement))
            logger.debug("blueEnhancement : " + str(blueEnhancement))

            # set stretch to min max
            redEnhancement.setMinimumValue(min_red)
            redEnhancement.setMaximumValue(max_red)
            greenEnhancement.setMinimumValue(min_green)
            greenEnhancement.setMaximumValue(max_green)
            blueEnhancement.setMinimumValue(min_blue)
            blueEnhancement.setMaximumValue(max_blue)
            logger.debug("red (1): " + str(redEnhancement.minimumValue()) + " " + str(redEnhancement.maximumValue()))
            logger.debug("green (1): " + str(greenEnhancement.minimumValue()) + " " + str(greenEnhancement.maximumValue()))
            logger.debug("blue (1): " + str(blueEnhancement.minimumValue()) + " " + str(blueEnhancement.maximumValue()))
            redEnhancement.setContrastEnhancementAlgorithm(1)
            greenEnhancement.setContrastEnhancementAlgorithm(1)
            blueEnhancement.setContrastEnhancementAlgorithm(1)
            logger.debug("red (2): " + str(redEnhancement.minimumValue()) + " " + str(redEnhancement.maximumValue()))
            logger.debug("green (2): " + str(greenEnhancement.minimumValue()) + " " + str(greenEnhancement.maximumValue()))
            logger.debug("blue (2): " + str(blueEnhancement.minimumValue()) + " " + str(blueEnhancement.maximumValue()))

            # print "blue enhancement", blueEnhancement
            # print "blue max", blueEnhancement.maximumValue()
            # print "blue min", blueEnhancement.minimumValue()

            layerRenderer.setRedContrastEnhancement(redEnhancement)  # , QgsRaster.ContrastEnhancementCumulativeCut  )
            layerRenderer.setGreenContrastEnhancement(greenEnhancement)  # , QgsRaster.ContrastEnhancementCumulativeCut  )
            layerRenderer.setBlueContrastEnhancement(blueEnhancement)  # , QgsRaster.ContrastEnhancementCumulativeCut  )

            # print "layer renderer"
            redEnhancement_debug = layerRenderer.redContrastEnhancement()
            greenEnhancement_debug = layerRenderer.greenContrastEnhancement()
            blueEnhancement_debug = layerRenderer.blueContrastEnhancement()
            logger.debug("red (3): " + str(redEnhancement_debug.minimumValue()) + " " + str(redEnhancement_debug.maximumValue()))
            logger.debug("green (3): " + str(greenEnhancement_debug.minimumValue()) + " " + str(greenEnhancement_debug.maximumValue()))
            logger.debug("blue (3): " + str(blueEnhancement_debug.minimumValue()) + " " + str(blueEnhancement_debug.maximumValue()))

        # print "end"
        theRasterLayer.setCacheImage(None)
        theRasterLayer.triggerRepaint()
        # print "2"
    canvas.refresh()
    canvas.repaint()
    # print "3"
    # TODO : pourquoi lorsqu'on fait un histogramme sur la bande pir, on a pour affichage des précédentes valeurs:
    # layer renderer <qgis._core.QgsSingleBandGrayRenderer object at 0x7fdd144558a0>
    # theRasterLayer 2
#     print "layer renderer", layerRenderer
#     print "theRasterLayer", theRasterLayer.rasterType()
#     if typeOfLayer == 1:
#         if theRasterLayer.rasterType() == 2 and layerRenderer:
#             redEnhancement_debug = layerRenderer.redContrastEnhancement()
#             greenEnhancement_debug = layerRenderer.greenContrastEnhancement()
#             blueEnhancement_debug = layerRenderer.blueContrastEnhancement()
#             logger.debug("red end: " + str(redEnhancement_debug.minimumValue()) + " " + str(redEnhancement_debug.maximumValue()))
#             logger.debug("green end: " + str(greenEnhancement_debug.minimumValue()) + " " + str(greenEnhancement_debug.maximumValue()))
#             logger.debug("blue end: " + str(blueEnhancement_debug.minimumValue()) + " " + str(blueEnhancement_debug.maximumValue()))
#     logger.info("#######################")


def get_raster_layers():
    canvas = TerreImageConstant().QGISCanvas

    rasterlayers = []

    for i in range(canvas.layerCount()):
        layer = canvas.layer(i)
        if (layer != None and layer.isValid() and layer.type() == QgsMapLayer.RasterLayer):
            rasterlayers.append(layer)
    return rasterlayers
