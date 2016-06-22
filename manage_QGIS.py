# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerreImage
                                 A QGIS plugin
                              -------------------
        begin                : 2013-11-21
        copyright            : (C) 2013-2016 by CS Systèmes d'Information
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

# import QGIS libraries
from qgis.core import (QgsMapLayerRegistry,
                       QgsMapLayer,
                       QgsContrastEnhancement,
                       QgsRasterLayer,
                       QgsRaster,
                       )

# import project libraries
from terre_image_constant import TerreImageConstant

# import logging for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_manageQGIS')
logger.setLevel(logging.INFO)


def get_raster_layer(raster, name):
    raster_layer = QgsRasterLayer(raster, name)
    return raster_layer


def add_qgis_raster_layer(raster_layer, canvas, bands = None):
    """
    Add the main working layer to QGIS
    Args:
        raster_layer:
        canvas:
        bands:

    Returns:

    """
    index_group = TerreImageConstant().index_group
    logger.debug("index_group: " + str(index_group))

    if bands:
        if raster_layer.rasterType() == 2:
            logger.debug(bands)
            pir = bands['pir']
            red = bands['red']
            green = bands['green']
            logger.debug('pir: ' + str(pir))
            logger.debug("red: " + str(red))
            logger.debug("green: " + str(green))
            if pir and red and green:
                renderer = raster_layer.renderer()
                renderer.setRedBand(pir)
                renderer.setGreenBand(red)
                renderer.setBlueBand(green)
            histogram_stretching(raster_layer, canvas)

    QgsMapLayerRegistry.instance().addMapLayer(raster_layer)
    TerreImageConstant().legendInterface.moveLayer(raster_layer, index_group)


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

    if layername == None:
        layername = os.path.basename(raster)

    raster_layer = QgsRasterLayer(raster, layername)
    histogram_stretching(raster_layer, iface.mapCanvas())

    QgsMapLayerRegistry.instance().addMapLayer(raster_layer)
    TerreImageConstant().legendInterface.moveLayer(raster_layer, index_group)
    return raster_layer


def histogram_stretching(raster_layer, canvas):
    # histogramStretch( true, QgsRaster::ContrastEnhancementCumulativeCut );
    # the_limits =QgsRaster::ContrastEnhancementCumulativeCut
    #   QgsRectangle myRectangle;
    #   if ( visibleAreaOnly )
    #     myRectangle = mMapCanvas->mapRenderer()->outputExtentToLayerExtent( myRasterLayer, mMapCanvas->extent() );
    #
    #   myRasterLayer->setContrastEnhancement( QgsContrastEnhancement::StretchToMinimumMaximum, the_limits, myRectangle );
    #
    #   myRasterLayer->setCacheImage( NULL );
    #   mMapCanvas->refresh();
    the_limits = QgsRaster.ContrastEnhancementCumulativeCut
    logger.debug("the_limits " + str(the_limits))
    raster_layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, the_limits)
    raster_layer.setCacheImage(None)
    canvas.refresh()
    canvas.repaint()


def histogram_stretching_for_threshold(raster_layer, canvas):
    # histogramStretch( true, QgsRaster::ContrastEnhancementCumulativeCut );
    # the_limits =QgsRaster::ContrastEnhancementCumulativeCut
    #   QgsRectangle myRectangle;
    #   if ( visibleAreaOnly )
    #     myRectangle = mMapCanvas->mapRenderer()->outputExtentToLayerExtent( myRasterLayer, mMapCanvas->extent() );
    #
    #   myRasterLayer->setContrastEnhancement( QgsContrastEnhancement::StretchToMinimumMaximum, the_limits, myRectangle );
    #
    #   myRasterLayer->setCacheImage( NULL );
    #   mMapCanvas->refresh();
    the_limits = QgsRaster. ContrastEnhancementMinMax
    logger.debug("the_limits " + str(the_limits))
    raster_layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, the_limits)
    raster_layer.setCacheImage(None)
    canvas.refresh()
    canvas.repaint()


def get_min_max_via_qgis(the_raster_layer, num_band):
    #     my_raster_stats = the_raster_layer.data_provider().bandStatistics( num_band )#, 2, 98  )
    #     my_min = my_raster_stats.minimumValue
    #     my_max = my_raster_stats.maximumValue
    #
    #     data_p = the_raster_layer.data_provider()
    my_min, my_max = the_raster_layer.data_provider().cumulativeCut(num_band, 0.2, 0.98)
    #     min, max = data_p.cumulativeCut(num_band, 0.02, 0.98)
    #     logger.debug("qgis min max :" + str(my_min) + str(my_max))
    #     logger.debug("min max 2 : " + str(min) + str(max))
    return my_min, my_max


def display_one_band(layer, keyword, iface):
    """
    Display the colored composition of the given keyword.
    Could be natural colors, or single band color.
    Args:
        layer:
        keyword:
        iface:

    Returns:

    """
    index_group = TerreImageConstant().index_group
    logger.debug("keyword " + str(keyword))
    corres = {'red': "_bande_rouge", 'green': "_bande_verte", 'blue': "_bande_bleue",
              'pir': "_bande_pir", 'mir': "_bande_mir", "nat": "_couleurs_naturelles"}

    raster_layer = QgsRasterLayer(layer.get_source(), layer.name() + corres[keyword])

    if keyword == 'nat':
        logger.debug("display on natural colors")
        band_red = layer.bands['red']
        band_green = layer.bands['green']
        band_blue = layer.bands['blue']
        renderer = raster_layer.renderer()
        renderer.setRedBand(band_red)
        renderer.setGreenBand(band_green)
        renderer.setBlueBand(band_blue)
        histogram_stretching(raster_layer, iface.mapCanvas())
        QgsMapLayerRegistry.instance().addMapLayer(raster_layer)
        TerreImageConstant().legendInterface.moveLayer(raster_layer, index_group)
        return raster_layer
    else:
        band = layer.bands[keyword]
        if band:
            logger.debug("band num: " + str(band))
            raster_layer.setDrawingStyle("MultiBandSingleBandGray")
            renderer = raster_layer.renderer()
            logger.debug(renderer)
            renderer.setGrayBand(band)

            histogram_stretching(raster_layer, iface.mapCanvas())
            QgsMapLayerRegistry.instance().addMapLayer(raster_layer)
            TerreImageConstant().legendInterface.moveLayer(raster_layer, index_group)
            return raster_layer


def custom_stretch(the_raster_layer, values, canvas, mono = False):
    """
    Applies a contrast between min and max. If given min and max are 0, then calculates the min and max from gdal.

    Args:
        the_raster_layer:
        values:
        canvas:
        mono:

    Returns:

    """
    logger.info("custom stretch: values")
    logger.info(values)

    # type of layer : raster, vector, other
    type_of_layer = the_raster_layer.type()

    # take the layer renderer to get the min and max
    layer_renderer = the_raster_layer.renderer()  # for qgis > 1.9
    data_provider = the_raster_layer.dataProvider()

    # the layer has to be a raster layer
    if type_of_layer == 1:
        if (the_raster_layer.rasterType() == 0 or mono) and layer_renderer:
            min_layer, max_layer = values[0]
            # gray band
            # layer_renderer <qgis.core.QgsSingleBandGrayRenderer object at 0x514caf0>
            gray_enhancement = QgsContrastEnhancement(data_provider.dataType(1))
            # take the contrast enhancement of the layer threw the renderer
            if gray_enhancement:
                gray_enhancement.setContrastEnhancementAlgorithm(1)  # qgis 1.9
                gray_enhancement.setMinimumValue(min_layer)
                gray_enhancement.setMaximumValue(max_layer)
                layer_renderer.setContrastEnhancement(gray_enhancement)

        elif the_raster_layer.rasterType() == 2 and layer_renderer:
            min_red, max_red = values[0]
            min_green, max_green = values[1]
            min_blue, max_blue = values[2]
            logger.debug("red : " + str(min_red) + " " + str(max_red))
            logger.debug("green : " + str(min_green) + " " + str(max_green))
            logger.debug("blue : " + str(min_blue) + " " + str(max_blue))

            red_enhancement = QgsContrastEnhancement(data_provider.dataType(1))
            green_enhancement = QgsContrastEnhancement(data_provider.dataType(2))
            blue_enhancement = QgsContrastEnhancement(data_provider.dataType(3))
            logger.debug("red_enhancement : " + str(red_enhancement))
            logger.debug("green_enhancement : " + str(green_enhancement))
            logger.debug("blue_enhancement : " + str(blue_enhancement))

            # set stretch to min max
            red_enhancement.setMinimumValue(min_red)
            red_enhancement.setMaximumValue(max_red)
            green_enhancement.setMinimumValue(min_green)
            green_enhancement.setMaximumValue(max_green)
            blue_enhancement.setMinimumValue(min_blue)
            blue_enhancement.setMaximumValue(max_blue)
            logger.debug("red (1): {} {}".format(red_enhancement.minimumValue(), red_enhancement.maximumValue()))
            logger.debug("green (1): {} {}".format(green_enhancement.minimumValue(), green_enhancement.maximumValue()))
            logger.debug("blue (1): {} {}".format(blue_enhancement.minimumValue(), blue_enhancement.maximumValue()))
            red_enhancement.setContrastEnhancementAlgorithm(1)
            green_enhancement.setContrastEnhancementAlgorithm(1)
            blue_enhancement.setContrastEnhancementAlgorithm(1)
            logger.debug("red (2): {} {}".format(red_enhancement.minimumValue(), red_enhancement.maximumValue()))
            logger.debug("green (2): {} {}".format(green_enhancement.minimumValue(), green_enhancement.maximumValue()))
            logger.debug("blue (2): {} {}".format(blue_enhancement.minimumValue(), blue_enhancement.maximumValue()))

            layer_renderer.setRedContrastEnhancement(red_enhancement)  # , QgsRaster.ContrastEnhancementCumulativeCut)
            layer_renderer.setGreenContrastEnhancement(green_enhancement)  #,QgsRaster.ContrastEnhancementCumulativeCut)
            layer_renderer.setBlueContrastEnhancement(blue_enhancement)  #, QgsRaster.ContrastEnhancementCumulativeCut)

            red_enhancement_debug = layer_renderer.redContrastEnhancement()
            green_enhancement_debug = layer_renderer.greenContrastEnhancement()
            blue_enhancement_debug = layer_renderer.blueContrastEnhancement()
            logger.debug("red (3): {} {}".format(red_enhancement_debug.minimumValue(),
                                                 red_enhancement_debug.maximumValue()))
            logger.debug("green (3): {} {}".format(green_enhancement_debug.minimumValue(),
                                                   green_enhancement_debug.maximumValue()))
            logger.debug("blue (3): {} {}".format(blue_enhancement_debug.minimumValue(),
                                                  blue_enhancement_debug.maximumValue()))

        the_raster_layer.setCacheImage(None)
        the_raster_layer.triggerRepaint()
    canvas.refresh()
    canvas.repaint()


def get_raster_layers():
    """
    Get raster layers loaded in QGIS
    Returns: a list of raster layers

    """
    canvas = TerreImageConstant().canvas

    rasterlayers = []

    for i in range(canvas.layerCount()):
        layer = canvas.layer(i)
        if layer is not None and layer.isValid() and layer.type() == QgsMapLayer.RasterLayer:
            rasterlayers.append(layer)
    return rasterlayers
