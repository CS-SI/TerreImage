# -*- coding: utf-8 -*-
"""
/***************************************************************************
         Value Tool       - A QGIS plugin to get values at the mouse pointer
                             -------------------
    begin                : 2008-08-26
    copyright            : (C) 2008 by G. Picard
                         : (C) 2014 by CNES
    email                :
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.

 History:
 -Add TerreImage improvements
 -Improve quality
 -change dic.haskey(mykey) to mykey in dic
"""
# from __future__ import unicode_literals


import gdalconst
import qgis.gui
from PyQt4 import QtCore, QtGui
from osgeo import osr, gdal
from qgis.core import (QGis,
                       QgsMapLayer,
                       QgsRasterDataProvider,
                       QgsRaster,
                       QgsCsException,
                       QgsPoint,
                       QgsCoordinateTransform,
                       QgsRasterBandStats,
                       QgsRectangle)

from PyQt4.QtCore import SIGNAL, QObject, QSize, Qt
from PyQt4.QtGui import QWidget, QBrush, QPen, QTableWidgetItem, QFileDialog

from ptmaptool import ProfiletoolMapTool_ValueTool
from terre_image_curve import TerreImageCurve
from ui_valuewidgetbase import Ui_ValueWidgetBase as Ui_Widget

# test if matplotlib >= 1.0
hasmpl = True
try:
    import matplotlib
    from matplotlib.ticker import MultipleLocator
    from matplotlib.ticker import MaxNLocator
    # import matplotlib.pyplot as plt
    # import matplotlib.ticker as ticker
    # from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
except:
    hasmpl = False
if hasmpl:
    if int(matplotlib.__version__[0]) < 1:
        hasmpl = False

# import logging for debug messages
from TerreImage import terre_image_logging
logger = terre_image_logging.configure_logger()


class ValueWidgetGraph(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called

        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def clear(self):
        self.axes.clear()

    def plot(self, x, y, color, marker='o'):
        # logger.debug("x {}; y {}".format(x, y))
        options = '"' + color + marker + '"'
        # logger.debug("options {}
        self.axes.plot(x, y, color + marker)
        xtext = self.axes.set_xlabel('Bandes')  # returns a Text instance
        ytext = self.axes.set_ylabel('Valeur')
        self.axes.figure.canvas.draw()
        xa = self.axes.get_xaxis()

        xa.set_major_locator(MaxNLocator(integer=True))





    def update_plot(self):
        self.axes.figure.canvas.draw()

    def plot_line(self, line):
#         try:
#             eval(line)
#         except SyntaxError:
#             logger.error("Erreur display")
#         else:
#             xtext = self.axes.set_xlabel('Bande') # returns a Text instance
#             ytext = self.axes.set_ylabel('Valeur')
#             self.axes.figure.canvas.draw()
        eval(line)
        xtext = self.axes.set_xlabel('Bandes')  # returns a Text instance
        ytext = self.axes.set_ylabel('Valeur')
        self.axes.figure.canvas.draw()

    # def plot_extra(self, xs, ys, colors, markers):
    #    if len(xs)   ==  len(ys)   ==  len(colors)   ==  len(markers) :



class ValueWidget(QWidget, Ui_Widget):

    def __init__(self, iface):

        self.hasmpl = hasmpl
        self.layerMap = dict()
        self.statsChecked = False
        self.ymin = 0
        self.ymax = 250

        # Statistics (>=1.9)
        self.statsSampleSize = 2500000
        self.stats = {}  # stats per layer

        # custom the displayed layers
        self.layers_to_display = None
        self.the_layer_to_display = None
        self.saved_curves = []

        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.legend = self.iface.legendInterface()

        QWidget.__init__(self)
        self.setupUi(self)
        self.setupUi_extra()

        # self.tool = ProfiletoolMapTool_ValueTool(self.iface.mapCanvas())
        self.maptool = self.canvas.mapTool()
        self.tool = None

        self.lines_mpl = None

        QObject.connect(self.cbxActive, SIGNAL("stateChanged(int)"), self.changeActive)
        QObject.connect(self.cbxGraph, SIGNAL("stateChanged(int)"), self.changePage)
        QObject.connect(self.canvas, SIGNAL("keyPressed( QKeyEvent * )"), self.pauseDisplay)
        QObject.connect(self.plotSelector, SIGNAL("currentIndexChanged ( int )"), self.changePlot)
        QObject.connect(self.pushButton_get_point, SIGNAL("clicked()"), self.on_get_point_button)
        QObject.connect(self.pushButton_csv, SIGNAL("clicked()"), self.export_csv)
        QObject.connect(self.checkBox_hide_current, SIGNAL("stateChanged(int)"), self.update_plot)
        numvalues = None


    def setupUi_extra(self):

        # make interface easier
        self.cbxActive.hide()
        self.plotSelector.hide()
        self.groupBox_saved_layers.hide()
        self.graphControls.hide()
        self.graphControls.setVisible(False)

        # plot
        self.plotSelector.setVisible(False)
        self.cbxStats.setVisible(False)
        if QGis.QGIS_VERSION_INT >= 10900:
            # stats by default because estimated are fast
            self.cbxStats.setChecked(True)
        self.graphControls.setVisible(False)
        self.groupBox_saved_layers.setVisible(False)
        self.pushButton_get_point.hide()
        self.checkBox_hide_current.setVisible(False)
        if self.hasmpl:
            self.plotSelector.addItem('mpl')
        self.plotSelector.setCurrentIndex(0)
        if  not self.hasmpl:
            # self.plotSelector.setVisible(False)
            self.plotSelector.setEnabled(False)

        # Page 3 - matplotlib
        self.mplLine = None  # make sure to invalidate when layers change
        if self.hasmpl:
            # mpl stuff
            # should make figure light gray
            self.sc_1 = ValueWidgetGraph(self, width=5, height=4, dpi=100)
            self.figure = plt.figure()
            self.canvas_mpl = FigureCanvas(self.figure)
            self.ax = self.figure.add_subplot(111)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.stackedWidget.addWidget(self.sc_1)
        self.stackedWidget.addWidget(self.canvas_mpl)
        self.stackedWidget.setCurrentIndex(0)

    def disconnect(self):
        self.changeActive(False)
        self.changeActive(Qt.Unchecked)
        QObject.disconnect(self.canvas, SIGNAL("keyPressed( QKeyEvent * )"), self.pauseDisplay)
        self.saved_curves = []
        QObject.disconnect(self.cbxActive, SIGNAL("stateChanged(int)"), self.changeActive)
        QObject.disconnect(self.cbxGraph, SIGNAL("stateChanged(int)"), self.changePage)
        QObject.disconnect(self.canvas, SIGNAL("keyPressed( QKeyEvent * )"), self.pauseDisplay)
        QObject.disconnect(self.plotSelector, SIGNAL("currentIndexChanged ( int )"), self.changePlot)
        QObject.disconnect(self.pushButton_get_point, SIGNAL("clicked()"), self.on_get_point_button)
        QObject.disconnect(self.pushButton_csv, SIGNAL("clicked()"), self.export_csv)
        QObject.disconnect(self.checkBox_hide_current, SIGNAL("stateChanged(int)"), self.update_plot)

    def pauseDisplay(self, e):
        pass

    def keyPressEvent(self, e):
        pass

    def set_layers(self, list_of_layers_to_display):
        temp_list = []
        nrow = 0
        if list_of_layers_to_display:
            self.the_layer_to_display = list_of_layers_to_display[0]
            for layer in list_of_layers_to_display:
                if layer is not None:
                    try:
                        layer_temp = layer.get_qgis_layer()
                    except:
                        temp_list.append(layer)
                        nrow += layer.bandCount()
                    else:
                        temp_list.append(layer_temp)
                        nrow += layer_temp.bandCount()
            self.layers_to_display = temp_list
            self.tableWidget.setRowCount(nrow)

    def changePage(self, state):
        if (state == Qt.Checked):
            self.groupBox_saved_layers.setVisible(True)
            self.checkBox_hide_current.setVisible(True)
            self.pushButton_get_point.show()
            # WARNING !!!
            self.stackedWidget.setCurrentIndex(2)
        else:
            self.groupBox_saved_layers.setVisible(False)
            self.plotSelector.setVisible(False)
            if QGis.QGIS_VERSION_INT < 10900:
                self.cbxStats.setVisible(False)
            self.graphControls.setVisible(False)
            # self.groupBox_saved_layers.setVisible( False )
            self.checkBox_hide_current.setVisible(False)
            self.pushButton_get_point.hide()
            self.stackedWidget.setCurrentIndex(0)

    def changePlot(self):
        self.changePage(self.cbxActive.checkState())

    def changeActive(self, state):
        if (state == Qt.Checked):
            # QObject.connect(self.canvas, SIGNAL("layersChanged ()"), self.invalidatePlot)
            if QGis.QGIS_VERSION_INT >= 10300:  # for QGIS >= 1.3
                QObject.connect(self.canvas, SIGNAL("xyCoordinates(const QgsPoint &)"), self.printValue)
            else:
                QObject.connect(self.canvas, SIGNAL("xyCoordinates(QgsPoint &)"), self.printValue)
        else:
            # QObject.disconnect(self.canvas, SIGNAL("layersChanged ()"), self.invalidatePlot)
            if QGis.QGIS_VERSION_INT >= 10300:  # for QGIS >= 1.3
                QObject.disconnect(self.canvas, SIGNAL("xyCoordinates(const QgsPoint &)"), self.printValue)
            else:
                QObject.disconnect(self.canvas, SIGNAL("xyCoordinates(QgsPoint &)"), self.printValue)

    def get_raster_layers(self):

        needextremum = self.cbxGraph.isChecked()  # if plot is checked

        # count the number of requires rows and remember the raster layers
        nrow = 0
        rasterlayers = []
        layersWOStatistics = []

        for i in range(self.canvas.layerCount()):
            layer = self.canvas.layer(i)
            if (layer is not None and layer.isValid() and layer.type() == QgsMapLayer.RasterLayer):
                if QGis.QGIS_VERSION_INT >= 10900:  # for QGIS >= 1.9
                    if not layer.dataProvider():
                        continue
                    if not layer.dataProvider().capabilities() & QgsRasterDataProvider.IdentifyValue:
                        continue

                    nrow += layer.bandCount()
                    rasterlayers.append(layer)

                else:  # < 1.9
                    if layer.providerKey() == "wms":
                        continue

                    if layer.providerKey() == "grassraster":
                        nrow += 1
                        rasterlayers.append(layer)
                    else:  # normal raster layer
                        nrow += layer.bandCount()
                        rasterlayers.append(layer)
                # check statistics for each band
                if needextremum:
                    for i in range(1, layer.bandCount() + 1):
                        if QGis.QGIS_VERSION_INT >= 10900:  # for QGIS >= 1.9
                            has_stats = self.getStats(layer, i) is not None
                        else:
                            has_stats = layer.hasStatistics(i)
                        if not layer.id() in self.layerMap and not has_stats\
                           and layer not in layersWOStatistics:
                            layersWOStatistics.append(layer)

        if layersWOStatistics and not self.statsChecked:
            self.calculateStatistics(layersWOStatistics)
        # create the row if necessary
        self.tableWidget.setRowCount(nrow)

        # TODO - calculate the min/max values only once, instead of every time!!!
        # keep them in a dict() with key=layer.id()
        return rasterlayers

    def printValue(self, position):

        coordx = "0"
        coordy = "0"

        if self.canvas.layerCount() == 0:
            self.values = []
            self.showValues()
            return

        needextremum = self.cbxGraph.isChecked()  # if plot is checked

        # if position is not None:
        if self.cbxGraph.isChecked():
            rasterlayers = [self.the_layer_to_display.get_qgis_layer()]
        else:
            if self.layers_to_display is not None:
                rasterlayers = self.layers_to_display
            else:
                rasterlayers = self.get_raster_layers()

        irow = 0
        self.values = []
        self.ymin = 1e38
        self.ymax = -1e38

        if QGis.QGIS_VERSION_INT >= 10900:
            mapCanvasSrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
        else:
            mapCanvasSrs = self.iface.mapCanvas().mapRenderer().destinationSrs()

        for layer in rasterlayers:
            # check if the current layer is the working layer
            is_the_working_layer = False
            if self.the_layer_to_display is not None:
                if layer == self.the_layer_to_display.get_qgis_layer():
                    is_the_working_layer = True
            layername = ""
            try:
                if not is_the_working_layer:
                    layername = unicode(layer.name())
                else:
                    layername = ""
            except Exception:
                pass
            layerSrs = ""
            try:
                if QGis.QGIS_VERSION_INT >= 10900:
                    layerSrs = layer.crs()
                else:
                    layerSrs = layer.srs()
            except Exception:
                pass

            pos = position

            # if given no position, get dummy values
            if position is None:
                pos = QgsPoint(0, 0)
            # transform points if needed
            elif not mapCanvasSrs == layerSrs and self.iface.mapCanvas().hasCrsTransformEnabled():
                srsTransform = QgsCoordinateTransform(mapCanvasSrs, layerSrs)
                try:
                    pos = srsTransform.transform(position)
                except QgsCsException, err:
                    # ignore transformation errors
                    continue

            if QGis.QGIS_VERSION_INT >= 10900:  # for QGIS >= 1.9
                if not layer.dataProvider():
                    continue

                ident = None
                if position is not None:
                    canvas = self.iface.mapCanvas()

                    # first test if point is within map layer extent
                    # maintain same behaviour as in 1.8 and print out of extent
                    if not layer.dataProvider().extent().contains(pos):
                        ident = dict()
                        for iband in range(1, layer.bandCount() + 1):
                            ident[iband] = self.tr('En dehors de l\'image')
                    # we can only use context if layer is not projected
                    elif canvas.hasCrsTransformEnabled() and layer.dataProvider().crs() != canvas.mapRenderer().destinationCrs():
                        ident = layer.dataProvider().identify(pos, QgsRaster.IdentifyFormatValue).results()
                    else:
                        extent = canvas.extent()
                        width = round(extent.width() / canvas.mapUnitsPerPixel())
                        height = round(extent.height() / canvas.mapUnitsPerPixel())

                        extent = canvas.mapRenderer().mapToLayerCoordinates(layer, extent)

                        ident = layer.dataProvider().identify(pos, QgsRaster.IdentifyFormatValue, canvas.extent(), width, height).results()
                    if not len(ident) > 0:
                        continue

                # if given no position, set values to 0
                if position is None and ident is not None and ident.iterkeys() is not None:
                    for key in ident.iterkeys():
                        ident[key] = layer.dataProvider().noDataValue(key)

                for iband in range(1, layer.bandCount() + 1):  # loop over the bands
                    layernamewithband = layername
                    if ident is not None and len(ident) > 1:
                        if is_the_working_layer:
                            layernamewithband += ' ' + self.the_layer_to_display.band_invert_french[iband]
                        else:
                            layernamewithband += ' ' + layer.bandName(iband)

                    if not ident or iband not in ident:  # should not happen
                        bandvalue = "?"
                    else:
                        bandvalue = ident[iband]
                        if bandvalue is None:
                            bandvalue = "no data"

                    # get the pixel line of the current position
                    coordx, coordy = self.calculatePixelLine(layer, pos)
                    self.values.append((layernamewithband, str(bandvalue), coordx, coordy))

                    if needextremum:
                        # estimated statistics
                        stats = self.getStats(layer, iband)
                        if stats:
                            self.ymin = min(self.ymin, stats.minimumValue)
                            self.ymax = max(self.ymax, stats.maximumValue)

        try:
            message_pixel_line = "Coordonnee (pixel, ligne) = (" + str(int(float(coordx))) + ", " + str(int(float(coordy))) + ")"
            self.iface.mainWindow().statusBar().showMessage(message_pixel_line)
        except ValueError:
            self.iface.mainWindow().statusBar().clearMessage()
        self.showValues()

    def calculatePixelLine(self, layer, pos):
        """
        Computes the pixel line of the mouse position

        Keyword arguments:
            layer  -- The current layer the caller function is working on
            pos    -- The position in a given coordinate system

        Returns : nothing
        """
        self.posx = pos.x()
        self.posy = pos.y()
        self.posQgsPoint = pos

        # using GDAL
        try:
            dataset = gdal.Open(layer.source(), gdalconst.GA_ReadOnly)
        except RuntimeError:
            message = "Failed to open " + layer.source() + ". You may have to many data opened in QGIS."
            logger.error(message)
        else:
            spatialReference = osr.SpatialReference()
            spatialReference.ImportFromWkt(dataset.GetProjectionRef())

            # if the layer is not georeferenced
            if len(str(spatialReference)) == 0:
                # never go in this loop because qgis always georeference a file at opening
                coordx = pos.x()
                coordy = pos.y()
                if coordy < 0:
                    coordy = -coordy
            else:
                # getting the extent and the spacing
                geotransform = dataset.GetGeoTransform()
                if geotransform is not None:
                    origineX = geotransform[0]
                    origineY = geotransform[3]
                    spacingX = geotransform[1]
                    spacingY = geotransform[5]

                    coordx = (pos.x() - origineX) / spacingX
                    coordy = (pos.y() - origineY) / spacingY
                    if coordy < 0:
                        coordy = -coordy

            # if coordx < 0 or coordx > layer.width() or coordy < 0 or coordy > layer.height() :
            if not layer.dataProvider().extent().contains(pos):
                coordx = 'En dehors de l\'image'
                coordy = 'En dehors de l\'image'
            else:
                # coordx = QgsRasterBlock.printValue( coordx )#QString(pos.x())
                coordx = str(coordx)  # QString(pos.x())
                # coordy = QgsRasterBlock.printValue( coordy )#QString(pos.y())
                coordy = str(coordy)  # QString(pos.y())
            return coordx, coordy

    def showValues(self):
        if self.cbxGraph.isChecked():
            # TODO don't plot if there is no data to plot...
            if self.checkBox_hide_current.checkState() == QtCore.Qt.Unchecked:
                # logger.debug("show values self.values {}".format(self.values))
                self.plot()
            else:
                self.sc_1.clear()
                self.sc_1.update_plot()
            if self.saved_curves:
                self.extra_plot()
            self.sc_1.update_plot()
        else:
            self.printInTable()

    def calculateStatistics(self, layersWOStatistics):
        #self.invalidatePlot(False)

        self.statsChecked = True

        layerNames = []
        for layer in layersWOStatistics:
            if not layer.id() in self.layerMap:
                layerNames.append(layer.name())

        if (len(layerNames) != 0):
            if not self.cbxStats.isChecked():
                for layer in layersWOStatistics:
                    self.layerMap[layer.id()] = True
                return
        else:
            logger.error('ERROR, no layers to get stats for')

        save_state = self.cbxActive.isChecked()
        self.changeActive(Qt.Unchecked)  # deactivate

        # calculate statistics
        for layer in layersWOStatistics:
            if not layer.id() in self.layerMap:
                self.layerMap[layer.id()] = True
                for i in range(1, layer.bandCount() + 1):
                    if QGis.QGIS_VERSION_INT >= 10900:  # for QGIS >= 1.9
                        self.getStats(layer, i , True)
                    else:
                        stat = layer.bandStatistics(i)

        if save_state:
            self.changeActive(Qt.Checked)  # activate if necessary

    def getStats(self, layer, bandNo, force = False):
        """
        Get cached statistics for layer and band or None if not calculated
        """
        if layer in self.stats:
            if bandNo in self.stats[layer]:
                return self.stats[layer][bandNo]
        else:
            self.stats[layer] = {}

        if force or layer.dataProvider().hasStatistics(bandNo, QgsRasterBandStats.Min | QgsRasterBandStats.Min, QgsRectangle(), self.statsSampleSize):
            self.stats[layer][bandNo] = layer.dataProvider().bandStatistics(bandNo, QgsRasterBandStats.Min | QgsRasterBandStats.Min, QgsRectangle(), self.statsSampleSize)
            return self.stats[layer][bandNo]

        return None

    def order_values(self, values):
        # values [(u'toulouse_2_5m_l93 green', '49.0', '2690.09944444', '7962.55055556'), (u'toulouse_2_5m_l93 red', '107.0', '2690.09944444', '7962.55055556'), (u'toulouse_2_5m_l93 pir', '100.0', '2690.09944444', '7962.55055556')]
        ordre = ["bleu", "vert", "rouge", "pir", "mir"]
        new_values = []
        # for each color
        for color in ordre:
            # check if one of the items is concerned
            for item in values:
                # if yes, add to the ordered list
                if color in item[0]:
                    new_values.append(item)
                    values.remove(item)
        new_values = new_values + values
        return new_values

    def order_values_from_attr(self, values):
        # attr {1: -14144.0, 2: -4984.0, 3: -13252.0, 4: 15707.0}
        # self.the_layer_to_display.bands:{'blue': 3, 'pir': 4, 'mir': -1, 'green': 2, 'red': 1}

        ordre = ["blue", "green", "red", "pir", "mir"]
        new_values = []

        for color in ordre:
            # check if one of the items is concerned
            if self.the_layer_to_display.bands[color] in values.keys():
                new_values.append((self.the_layer_to_display.bands[color], values[self.the_layer_to_display.bands[color]]))
        return new_values

    def printInTable(self):
        items = self.values
        new_items = self.order_values(items)

        irow = 0

        items = []

        for row in new_items:  # self.values:
            layername, value, x, y = row

            try:
                value = str("{0:." + str(3) + "f}").format(float(value))
                x = str(int(float(x)))
                y = str(int(float(y)))
            except ValueError:
                pass

            if (self.tableWidget.item(irow, 0) == None):
                # create the item
                self.tableWidget.setItem(irow, 0, QTableWidgetItem())
                self.tableWidget.setItem(irow, 1, QTableWidgetItem())

            self.tableWidget.item(irow, 0).setText(layername)
            self.tableWidget.item(irow, 1).setText(value)
            irow += 1

    def plot(self):
        logger.debug("plot")
        items = self.values
        new_items = self.order_values(items)
        logger.debug("items {}".format(new_items))
        self.temp_values = None

        pixel = 0
        ligne = 0

        numvalues = []
        if self.hasmpl:
            for row in new_items:
                layername, value, pixel_, ligne_ = row
                pixel = pixel_
                ligne = ligne_
                try:
                    numvalues.append(float(value))
                except:
                    numvalues.append(0)

        self.plot_values = numvalues

        ymin = self.ymin
        ymax = self.ymax
        if self.leYMin.text() != '' and self.leYMax.text() != '':
            ymin = float(self.leYMin.text())
            ymax = float(self.leYMax.text())

        if (self.hasmpl and (self.plotSelector.currentText() == 'mpl')):

            self.remove_current_line()
            if self.checkBox_hide_current.checkState() == QtCore.Qt.Unchecked:
                self.sc_1.clear()

                t = range(1, len(numvalues) + 1)
                self.sc_1.plot(t, numvalues, 'k', 'o-')


                self.lines_mpl = self.ax.plot(t, numvalues, color = 'k', marker = 'o', linestyle = "-")

                self.temp_values = numvalues
                logger.debug("self.canvas.draw()")

        # if self.saved_curves:
        #     self.extra_plot()

        self.canvas_mpl.draw()

    def remove_current_line(self):
        #remove the first line
        if self.lines_mpl:
            try:
                l = self.lines_mpl.pop(0).remove()
                del l
            except (IndexError, ValueError):
                pass

    def del_extra_curve(self, curve):
        self.saved_curves.remove(curve)
        curve.close()
        self.extra_plot(True)

    def extra_plot(self, current_line=False):
        """
        Manages the plot of saved curves
        Args:
            current_line:

        Returns:

        """
        plt.cla()
        if current_line and self.temp_values:
            t = range(1, len(self.temp_values) + 1)
            if self.checkBox_hide_current.checkState() == QtCore.Qt.Unchecked:
                self.lines_mpl = self.ax.plot(t, self.temp_values, color = 'k', marker = 'o', linestyle = "-")

        for curve in self.saved_curves:
            if curve.display_points():
                logger.debug(curve)

                numvalues = curve.points

                ymin = self.ymin
                ymax = self.ymax

                t = range(1, len(numvalues) + 1)
                color_curve = curve.color
                self.ax.plot(t, numvalues, color = color_curve, marker = 'o', linestyle = "-")

                self.sc_1.plot(t, numvalues, color_curve, 'o-')


    def on_get_point_button(self):
        if self.tool is None:
            # if self.pushButton_get_point.isFlat() == False:
            self.tool = ProfiletoolMapTool_ValueTool(self.iface.mapCanvas())
            QtCore.QObject.connect(self.tool, QtCore.SIGNAL("canvas_clicked_v"), self.rightClicked)
            # init the mouse listener comportement and save the classic to restore it on quit
            self.canvas.setMapTool(self.tool)
        else:
            if self.tool:
                self.tool.deactivate()
            QtCore.QObject.disconnect(self.tool, QtCore.SIGNAL("canvas_clicked_v"), self.rightClicked)
            self.toolPan = qgis.gui.QgsMapToolPan(self.canvas)
            self.canvas.setMapTool(self.toolPan)
            self.tool = None

    def rightClicked(self, position):
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
        x, y = self.calculatePixelLine(self.the_layer_to_display.get_qgis_layer(), mapPos)
        try:
            x = int(float(x))
            y = int(float(y))
        except ValueError:
            pass

        newPoints = [[mapPos.x(), mapPos.y()]]

        ident = self.the_layer_to_display.get_qgis_layer().dataProvider().identify(QgsPoint(mapPos.x(), mapPos.y()), QgsRaster.IdentifyFormatValue)
        if ident is not None:
            attr = ident.results()
            new_points = self.order_values_from_attr(attr)

            points_for_curve = [ t[1] for t in new_points ]
            logger.debug("points_for_curve: {}".format(points_for_curve))
            abs = [ t[0] for t in new_points ]
            logger.debug("abs: {}".format(abs))

            curve_temp = TerreImageCurve("Courbe" + str(len(self.saved_curves)), x, y, points_for_curve)
            QObject.connect(curve_temp, SIGNAL("deleteCurve()"), lambda who=curve_temp: self.del_extra_curve(who))
            QObject.connect(curve_temp, SIGNAL("redraw()"), self.curve_state_changed)
            self.saved_curves.append(curve_temp)
            self.verticalLayout_curves.addWidget(curve_temp)
            self.groupBox_saved_layers.show()

        self.on_get_point_button()

    def export_csv(self):
        csv = QFileDialog.getSaveFileName(None, "Fichier CSV")
        if not csv.endswith(".csv"):
            csv += ".csv"
        csv_file = open(csv, "w")
        if csv:
            for curve in self.saved_curves:
                logger.debug(u"save curve {}".format(curve))
                csv_file.write(str(curve.name) + u';Coordonnées pixel '.encode('utf8') + curve.coordinates + "\n")
                csv_file.write(u'Bande spectrale; Intensité \n'.encode('utf8'))
                for i in range(1, len(curve.points) + 1):
                    csv_file.write("{};{}\n".format(i, int(curve.points[i - 1])))

                csv_file.write("\n\n\n")

    def update_plot(self):
        # logger.debug("update plot")
        self.plot()

    def curve_state_changed(self):
        logger.info("====State changed from valuewidget====")
        self.extra_plot(True)
        self.update_plot()


    def statsNeedChecked(self, indx):
        # self.statsChecked = False
        self.invalidatePlot()

    def invalidatePlot(self, replot=True):
        self.statsChecked = False
        if self.mplLine is not None:
            del self.mplLine
            self.mplLine = None
        # update empty plot
        if replot and self.cbxGraph.isChecked():
            # self.values=[]
            #self.printValue(None)
            pass

    def resizeEvent(self, event):
        pass
        #self.invalidatePlot()
