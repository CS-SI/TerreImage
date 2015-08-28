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
"""
# from __future__ import unicode_literals


from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.gui

from numpy import arange

from ui_valuewidgetbase import Ui_ValueWidgetBase as Ui_Widget
from terre_image_curve import TerreImageCurve
import random
from ptmaptool import ProfiletoolMapTool_ValueTool

from osgeo import osr, gdal
import gdalconst

hasqwt = False
try:
    from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtScaleDiv, QwtSymbol
except:
    hasqwt = False

# test if matplotlib >= 1.0
hasmpl = True
try:
    import matplotlib
    # import matplotlib.pyplot as plt 
    import matplotlib.ticker as ticker
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except:
    hasmpl = False
if hasmpl:
    if int(matplotlib.__version__[0]) < 1:
        hasmpl = False


# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('ValueTool_valueWidget')
logger.setLevel(logging.INFO)




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
        # print "x", x
        # print "y", y
        options = '"' + color + marker + '"'
        # print options
        self.axes.plot(x, y, color + marker)
        xtext = self.axes.set_xlabel('Bandes')  # returns a Text instance
        ytext = self.axes.set_ylabel('Valeur')
        self.axes.figure.canvas.draw()
        
    def update_plot(self):
        self.axes.figure.canvas.draw()
        
    def plot_line(self, line):
#         try:
#             eval(line)
#         except SyntaxError:
#             print "Erreur display"
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

        self.hasqwt = hasqwt
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
        self.logger = logging.getLogger('.'.join((__name__,
                                        self.__class__.__name__)))

        QWidget.__init__(self)
        self.setupUi(self)
        self.setupUi_extra()
        
        # self.tool = ProfiletoolMapTool_ValueTool(self.iface.mapCanvas())
        self.maptool = self.canvas.mapTool()
        self.tool = None
        
        
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
        if self.hasqwt:
            self.plotSelector.addItem('Qwt')
        if self.hasmpl:
            self.plotSelector.addItem('mpl')
        self.plotSelector.setCurrentIndex(0);
        if (not self.hasqwt or not self.hasmpl):
            # self.plotSelector.setVisible(False)
            self.plotSelector.setEnabled(False)

        # Page 2 - qwt
        if self.hasqwt:
            self.qwtPlot = QwtPlot(self.stackedWidget)
            self.qwtPlot.setAutoFillBackground(False)
            self.qwtPlot.setObjectName("qwtPlot")
            self.curve = QwtPlotCurve()
            self.curve.setSymbol(
                QwtSymbol(QwtSymbol.Ellipse,
                          QBrush(Qt.white),
                          QPen(Qt.red, 2),
                          QSize(9, 9)))
            self.curve.attach(self.qwtPlot)
            self.qwtPlot.setVisible(False)
        else:
            self.qwtPlot = QtGui.QLabel("Need Qwt >= 5.0 or matplotlib >= 1.0 !")

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qwtPlot.sizePolicy().hasHeightForWidth())
        self.qwtPlot.setSizePolicy(sizePolicy)
        self.qwtPlot.setObjectName("qwtPlot")
        self.qwtPlot.updateGeometry()
        self.stackedWidget.addWidget(self.qwtPlot)

        # Page 3 - matplotlib
        self.mplLine = None  # make sure to invalidate when layers change
        if self.hasmpl:
            # mpl stuff
            # should make figure light gray
            self.sc_1 = ValueWidgetGraph(self, width=5, height=4, dpi=100)
            
            
#             self.mplBackground = None #http://www.scipy.org/Cookbook/Matplotlib/Animations
#             
#             
#             self.mplFig = plt.Figure(facecolor='w', edgecolor='w')
#             self.mplFig.subplots_adjust(left=0.1, right=0.975, bottom=0.13, top=0.95)
#             self.mplPlt = self.mplFig.add_subplot(111)   
#             self.mplPlt.tick_params(axis='both', which='major', labelsize=12)
#             self.mplPlt.tick_params(axis='both', which='minor', labelsize=10)                           
#             # qt stuff
#             self.pltCanvas = FigureCanvasQTAgg(self.mplFig)
#             self.pltCanvas.setParent(self.stackedWidget)
#             self.pltCanvas.setAutoFillBackground(False)
#             self.pltCanvas.setObjectName("mplPlot")
#             self.mplPlot = self.pltCanvas
#             self.mplPlot.setVisible(False)
        else:
            self.mplPlot = QtGui.QLabel("Need Qwt >= 5.0 or matplotlib >= 1.0 !")

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.mplPlot.sizePolicy().hasHeightForWidth())
#         self.mplPlot.setSizePolicy(sizePolicy)
#         self.qwtPlot.setObjectName("qwtPlot")
#         self.mplPlot.updateGeometry()
        self.stackedWidget.addWidget(self.sc_1)
        self.stackedWidget.setCurrentIndex(0)


    def disconnect(self):
        self.changeActive(False)
        QObject.disconnect(self.canvas, SIGNAL("keyPressed( QKeyEvent * )"), self.pauseDisplay)
    
    
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
                if layer is not None :
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
            # self.plotSelector.setVisible( True )
            # self.cbxStats.setVisible( True )
            # self.graphControls.setVisible( True )
            self.groupBox_saved_layers.setVisible(True)
            self.checkBox_hide_current.setVisible(True)
            self.pushButton_get_point.show()
            
            if (self.plotSelector.currentText() == 'mpl'):
                self.stackedWidget.setCurrentIndex(2)
            else:
                self.stackedWidget.setCurrentIndex(1)
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
            # QObject.connect(self.legend, SIGNAL( "itemAdded ( QModelIndex )" ), self.statsNeedChecked )
            # QObject.connect(self.legend, SIGNAL( "itemRemoved ()" ), self.invalidatePlot )
            QObject.connect(self.canvas, SIGNAL("layersChanged ()"), self.invalidatePlot)
            if QGis.QGIS_VERSION_INT >= 10300:  # for QGIS >= 1.3
                QObject.connect(self.canvas, SIGNAL("xyCoordinates(const QgsPoint &)"), self.printValue)
            else:
                QObject.connect(self.canvas, SIGNAL("xyCoordinates(QgsPoint &)"), self.printValue)
        else:
            QObject.disconnect(self.canvas, SIGNAL("layersChanged ()"), self.invalidatePlot)
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
            if (layer != None and layer.isValid() and layer.type() == QgsMapLayer.RasterLayer):
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
                    has_stats = self.getStats (layer, i) is not None
                  else:
                    has_stats = layer.hasStatistics(i)
                  if not layer.id() in self.layerMap and not has_stats\
                          and not layer in layersWOStatistics:
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
        else :
            if self.layers_to_display is not None:
                rasterlayers = self.layers_to_display
            else :
                rasterlayers = self.get_raster_layers()
#         else:
#             print "position", position
#             rasterlayers = self.get_raster_layers()
            
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
            try:
                if not is_the_working_layer:
                    layername = unicode(layer.name())
                else :
                    layername = ""
            except Exception:
                pass
            
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
                    ident[iband] = str(self.tr('En dehors de l\'image'))
                # we can only use context if layer is not projected
                elif canvas.hasCrsTransformEnabled() and layer.dataProvider().crs() != canvas.mapRenderer().destinationCrs():
                  ident = layer.dataProvider().identify(pos, QgsRaster.IdentifyFormatValue).results()
                else:
                  extent = canvas.extent()
                  width = round(extent.width() / canvas.mapUnitsPerPixel());
                  height = round(extent.height() / canvas.mapUnitsPerPixel());

                  extent = canvas.mapRenderer().mapToLayerCoordinates(layer, extent);

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

                if not ident or not ident.has_key(iband):  # should not happen
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
                  stats = self.getStats (layer, iband)
                  if stats:
                    self.ymin = min(self.ymin, stats.minimumValue)
                    self.ymax = max(self.ymax, stats.maximumValue)

        try :
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
        try :
            dataset = gdal.Open(layer.source(), gdalconst.GA_ReadOnly)
        except RuntimeError:
            message = "Failed to open " + layer.source() + ". You may have to many data opened in QGIS."
            logger.error(message)
        else :
            spatialReference = osr.SpatialReference()
            spatialReference.ImportFromWkt(dataset.GetProjectionRef())
            
            # if the layer is not georeferenced
            if len(str(spatialReference)) == 0 :
                # never go in this loop because qgis always georeference a file at opening
                coordx = pos.x()
                coordy = pos.y()
                if coordy < 0:
                    coordy = -coordy
            else :
                # getting the extent and the spacing
                geotransform = dataset.GetGeoTransform()
                if not geotransform is None:
                    origineX = geotransform[0]
                    origineY = geotransform[3]
                    spacingX = geotransform[1]
                    spacingY = geotransform[5]
    
    
                    coordx = (pos.x() - origineX) / spacingX
                    coordy = (pos.y() - origineY) / spacingY
                    if coordy < 0:
                        coordy = -coordy
                    
            if not layer.dataProvider().extent().contains(pos):
    #        if coordx < 0 or coordx > layer.width() or coordy < 0 or coordy > layer.height() :
                coordx = 'En dehors de l\'image'
                coordy = 'En dehors de l\'image'
            else :
    #            coordx = QgsRasterBlock.printValue( coordx )#QString(pos.x())
                coordx = str(coordx)  # QString(pos.x())
    #            coordy = QgsRasterBlock.printValue( coordy )#QString(pos.y())
                coordy = str(coordy)  # QString(pos.y())
            return coordx, coordy


    def showValues(self):
        if self.cbxGraph.isChecked():
            # TODO don't plot if there is no data to plot...
            if self.checkBox_hide_current.checkState() == QtCore.Qt.Unchecked:
                # print "show values self.values", self.values
                self.plot()
            else:
                self.sc_1.clear()
                self.sc_1.update_plot()
            if self.saved_curves :
                self.extra_plot()
            self.sc_1.update_plot()
        else:
            self.printInTable()

    def calculateStatistics(self, layersWOStatistics):
        
        self.invalidatePlot(False)

        self.statsChecked = True

        layerNames = []
        for layer in layersWOStatistics:
            if not layer.id() in self.layerMap:
                layerNames.append(layer.name())

        if (len(layerNames) != 0):
#            res = QMessageBox.warning( self, self.tr( 'Warning' ),
#                                       self.tr( 'There are no statistics in the following rasters:\n%1\n\nCalculate?' ).arg(layerNames.join('\n')),
#                                       QMessageBox.Yes | QMessageBox.No )
#            if res != QMessageBox.Yes:
            if not self.cbxStats.isChecked():
                # self.cbxActive.setCheckState(Qt.Unchecked)  
                for layer in layersWOStatistics:
                    self.layerMap[layer.id()] = True
                return
        else:
            print('ERROR, no layers to get stats for')
        
        save_state = self.cbxActive.isChecked()
        self.changeActive(Qt.Unchecked)  # deactivate

        # calculate statistics
        for layer in layersWOStatistics:
            if not layer.id() in self.layerMap:
                self.layerMap[layer.id()] = True
                for i in range(1, layer.bandCount() + 1):
                    if QGis.QGIS_VERSION_INT >= 10900:  # for QGIS >= 1.9
                        self.getStats (layer, i , True)
                    else:
                        stat = layer.bandStatistics(i)

        if save_state:
            self.changeActive(Qt.Checked)  # activate if necessary

    # get cached statistics for layer and band or None if not calculated
    def getStats (self, layer, bandNo, force=False):
      if self.stats.has_key(layer):
        if self.stats[layer].has_key(bandNo) : 
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
                # self.tableWidget.setItem(irow, 2, QTableWidgetItem())
                # self.tableWidget.setItem(irow, 3, QTableWidgetItem())
     
            self.tableWidget.item(irow, 0).setText(layername)
            self.tableWidget.item(irow, 1).setText(value)
            # self.tableWidget.item(irow, 2).setText( x )
            # self.tableWidget.item(irow, 3).setText( y )
            irow += 1
          

    def plot(self):
        items = self.values
        new_items = self.order_values(items)
        # print "items", new_items

        pixel = 0
        ligne = 0
        
        numvalues = []
        if (self.hasqwt or self.hasmpl):
            for row in new_items:
                layername, value, pixel_, ligne_ = row
                pixel = pixel_
                ligne = ligne_
                try:
                    numvalues.append(float(value))
                except:
                    numvalues.append(0)
        
        # print numvalues
        
        
#         if self.memorize_curve:
#             print "num values curve temp", numvalues
#             curve_temp = TerreImageCurve("Courbe" + str(len(self.saved_curves)), pixel, ligne, numvalues)
#             QObject.connect( curve_temp, SIGNAL( "deleteCurve()"), lambda who=curve_temp: self.del_extra_curve(who))
#             self.saved_curves.append(curve_temp)
#             self.memorize_curve = False
#             self.verticalLayout_curves.addWidget( curve_temp )
#             self.groupBox_saved_layers.show()
#             print curve_temp
                    
        ymin = self.ymin
        ymax = self.ymax
        if self.leYMin.text() != '' and self.leYMax.text() != '': 
            ymin = float(self.leYMin.text())
            ymax = float(self.leYMax.text())        

        if (self.hasqwt and (self.plotSelector.currentText() == 'Qwt')):

            self.qwtPlot.setAxisMaxMinor(QwtPlot.xBottom, 0)
            # self.qwtPlot.setAxisMaxMajor(QwtPlot.xBottom,0)
            self.qwtPlot.setAxisScale(QwtPlot.xBottom, 1, len(new_items))
            # self.qwtPlot.setAxisScale(QwtPlot.yLeft,self.ymin,self.ymax)
            self.qwtPlot.setAxisScale(QwtPlot.yLeft, ymin, ymax)
            
            self.curve.setData(range(1, len(numvalues) + 1), numvalues)
            self.qwtPlot.replot()
            self.qwtPlot.setVisible(len(numvalues) > 0)

        elif (self.hasmpl and (self.plotSelector.currentText() == 'mpl')):

            self.sc_1.clear()
            
            t = range(1, len(numvalues) + 1)
            self.sc_1.plot(t, numvalues, 'k', 'o-')
            
            self.temp_values = numvalues

        if self.saved_curves:
            self.extra_plot()

            # line = "self.axes.plot(" + str(t) + ", " + str(numvalues) +", ko-)"
            # self.sc_1.plot_line(line)
            
#             self.mplPlt.plot(range(1,len(numvalues)+1), numvalues, marker='o', color='k', mfc='b', mec='b')
#             self.mplPlt.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
#             self.mplPlt.yaxis.set_minor_locator(ticker.AutoMinorLocator())
#             self.mplPlt.set_xlim( (1-0.25,len(new_items)+0.25 ) )
#             self.mplPlt.set_ylim( (ymin, ymax) ) 
#             self.mplFig.canvas.draw()

            # disable optimizations - too many bugs, depending on mpl version!
#             if self.mplLine is None:
#                 self.mplPlt.clear()
#                 self.mplLine, = self.mplPlt.plot(range(1,len(numvalues)+1), numvalues, marker='o', color='k', mfc='b', mec='b', animated=True)
#                 self.mplPlt.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
#                 self.mplPlt.yaxis.set_minor_locator(ticker.AutoMinorLocator())
#                 self.mplPlt.set_xlim( (1-0.25,len(self.values)+0.25 ) )
#                 self.mplPlt.set_ylim( (self.ymin, self.ymax) )
#                 self.mplFig.canvas.draw()
#                 self.mplBackground = self.mplFig.canvas.copy_from_bbox(self.mplFig.bbox)
#             else:
#                 # restore the clean slate background
#                 self.mplFig.canvas.restore_region(self.mplBackground)
#                 # update the data
#                 self.mplLine.set_xdata(range(1,len(numvalues)+1))
#                 self.mplLine.set_ydata(numvalues)
#                 self.mplPlt.draw_artist(self.mplLine)
#                 # just redraw the axes rectangle
#                 self.mplFig.canvas.blit(self.mplFig.bbox)
#             self.mplPlot.setVisible(len(numvalues)>0)

        # try:
                #    attr = float(ident[j])
                # except:
                #    attr = 0
                #    print "Null cell value catched as zero!"  # For none values, profile height = 0. It's not elegant...

                    # nr = rastLayer.getRasterBandNumber(self.rastItems[field[1]][field[2]][0])

                    # print ident
            # for j in ident:
                # print j
                # if j.right(1) == str(nr):
       # attr = int(ident[j])
       #attr = float(ident[j])  ##### I MUST IMPLEMENT RASTER TYPE HANDLING!!!!
       # outFeat.addAttribute(i, QVariant(attr))


    def del_extra_curve(self, curve):
        self.saved_curves.remove(curve)
        curve.close()
        self.plot()


    def extra_plot(self):
        if self.checkBox_hide_current.checkState() == QtCore.Qt.Unchecked:
            t = range(1, len(self.temp_values) + 1)
            line = 'self.axes.plot(' + str(t) + ',' + str(self.temp_values) + ', "ko-"'
            if self.saved_curves:
                line += ","
        else:
            line = 'self.axes.plot('
        
        i = 0
        
        
        for curve in self.saved_curves:
            if curve.display_points():
                logger.debug(curve)
                
                numvalues = curve.points
                
                ymin = self.ymin
                ymax = self.ymax
                
                color_curve = curve.color
                
                t = range(1, len(numvalues) + 1)
                self.sc_1.plot(t, numvalues, color_curve, 'o-')
                line += str(t) + ',' + str(numvalues) + ', \'' + color_curve + 'o-\''
                if i + 1 < len(self.saved_curves):
                    line += ","
            i += 1
            
        line += ')'
                
        # print "line", line
        self.sc_1.plot_line(line)
                
                
                
#                 self.mplPlt.plot(range(1,len(numvalues)+1), numvalues, marker='o', color=color_curve, mfc='b', mec='b')
#                 self.mplPlt.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
#                 self.mplPlt.yaxis.set_minor_locator(ticker.AutoMinorLocator())
#                 self.mplPlt.set_xlim( (1-0.25,len(numvalues)+0.25 ) )
#                 self.mplPlt.set_ylim( (ymin, ymax) ) 
#                 self.mplFig.canvas.draw()

    def on_get_point_button(self):
        if self.tool is None:
        # if self.pushButton_get_point.isFlat() == False:
            self.tool = ProfiletoolMapTool_ValueTool(self.iface.mapCanvas())
            QtCore.QObject.connect(self.tool, QtCore.SIGNAL("canvas_clicked_v"), self.rightClicked)
            # init the mouse listener comportement and save the classic to restore it on quit
            self.canvas.setMapTool(self.tool)
        else :
            if self.tool:
                self.tool.deactivate()
            QtCore.QObject.disconnect(self.tool, QtCore.SIGNAL("canvas_clicked_v"), self.rightClicked)
            self.toolPan = qgis.gui.QgsMapToolPan(self.canvas)
            self.canvas.setMapTool(self.toolPan)
            self.tool = None
            
        
    def rightClicked(self, position):
        mapPos = self.canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])
        x, y = self.calculatePixelLine(self.the_layer_to_display.get_qgis_layer(), mapPos)
        
        try :
            x = int(float(x))
            y = int(float(y))
        except ValueError:
            pass
        
        
        
        newPoints = [[mapPos.x(), mapPos.y()]]
        
        ident = self.the_layer_to_display.get_qgis_layer().dataProvider().identify(QgsPoint(mapPos.x(), mapPos.y()), QgsRaster.IdentifyFormatValue)
        if ident is not None :
            attr = ident.results()
            new_points = self.order_values_from_attr(attr)
        
        # ident = self.the_layer_to_display.get_qgis_layer().dataProvider().identify(QgsPoint(mapPos.x(), mapPos.x()), QgsRaster.IdentifyFormatValue ).results()
        
            # TODO : put values in right order
#             new_points=[]
#             for i in range(1, len(attr)+1):
#                 new_points.append( (self.the_layer_to_display.band_invert[i], attr[i] ))
#             points = self.order_values(new_points)
            
            points_for_curve = [ t[1] for t in new_points ]
            logger.debug("points_for_curve: " + str(points_for_curve))
            abs = [ t[0] for t in new_points ]
            logger.debug("abs: " + str(abs))
            
    #         colors=['b', 'r', 'g', 'c', 'm', 'y', 'k', 'w']
    #         print "len(colors)", len(colors)
    #         color = colors[ random.randint(0, len(colors)-1) ] 
    #         print 'color from creation courbe', color
            # QtGui.QColor(random.randint(0,256), random.randint(0,256), random.randint(0,256))
            curve_temp = TerreImageCurve("Courbe" + str(len(self.saved_curves)), x, y, points_for_curve)
            QObject.connect(curve_temp, SIGNAL("deleteCurve()"), lambda who=curve_temp: self.del_extra_curve(who))
            QObject.connect(curve_temp, SIGNAL("colorChanged()"), self.update_plot)
            self.saved_curves.append(curve_temp)
            self.verticalLayout_curves.addWidget(curve_temp)
            self.groupBox_saved_layers.show()
            
        self.on_get_point_button()
        
     
    def export_csv(self):
        csv = QFileDialog.getSaveFileName(None, str("Fichier CSV"))
        if not csv.endswith(".csv"):
            csv += ".csv"
        csv_file = open(csv, "w")
        if csv :
            for curve in self.saved_curves:
                # print "save curve", curve
                csv_file.write(str(curve.name) + u';Coordonnées pixel '.encode('utf8') + curve.coordinates + "\n")
                csv_file.write(u'Bande spectrale; Intensité \n'.encode('utf8'))
                for i in range(1, len(curve.points) + 1):
                    csv_file.write(str(i) + ";" + str(int(curve.points[i - 1])) + "\n")
                    
                csv_file.write("\n\n\n")
                
    def update_plot(self):
        # print "update plot"
        self.plot()

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
            self.printValue(None)

    def resizeEvent(self, event):
        self.invalidatePlot()

