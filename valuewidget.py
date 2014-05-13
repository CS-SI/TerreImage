"""
/***************************************************************************
         Value Tool       - A QGIS plugin to get values at the mouse pointer
                             -------------------
    begin                : 2008-08-26
    copyright            : (C) 2008 by G. Picard
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

import logging
# change the level back to logging.WARNING(the default) before releasing
logging.basicConfig(level=logging.DEBUG)

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


#test if matplotlib >= 1.0
hasmpl=True
try:
    import matplotlib
    import matplotlib.pyplot as plt 
    import matplotlib.ticker as ticker
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
except:
    hasmpl=False
if hasmpl:
    if int(matplotlib.__version__[0]) < 1:
        hasmpl = False

print "hasmpl", hasmpl

class ValueWidget():

    def __init__(self, iface, ui):

        self.ui = ui
        self.hasmpl=hasmpl
        print self.hasmpl
        self.layerMap=dict()
        self.statsChecked=False
        self.ymin=0
        self.ymax=250

        self.iface=iface
        self.canvas=self.iface.mapCanvas()
        self.legend=self.iface.legendInterface()

        QObject.connect(self.canvas, SIGNAL( "keyPressed( QKeyEvent * )" ), self.pauseDisplay )
        QObject.connect(self.canvas, SIGNAL( "layersChanged ()" ), self.invalidatePlot )
        QObject.connect(self.canvas, SIGNAL("xyCoordinates(const QgsPoint &)"), self.printValue)
        QObject.connect(self.ui.tabWidget, SIGNAL("currentChanged(int))"), self.change_tab)
        
        self.is_graph = 0
        self.mplLine = None
        
        self.setupUi_extra()
        

    def setupUi_extra(self):
        #Page 3 - matplotlib
        self.toto = QPushButton( "Toto", self.ui.tab_graph )
        self.mplLine = None #make sure to invalidate when layers change
        if self.hasmpl:
            print "setup matplotlib"
            # mpl stuff
            # should make figure light gray
            self.mplBackground = None #http://www.scipy.org/Cookbook/Matplotlib/Animations
            self.mplFig = plt.Figure(facecolor='w', edgecolor='w')
            self.mplFig.subplots_adjust(left=0.1, right=0.975, bottom=0.13, top=0.95)
            self.mplPlt = self.mplFig.add_subplot(111)   
            self.mplPlt.tick_params(axis='both', which='major', labelsize=12)
            self.mplPlt.tick_params(axis='both', which='minor', labelsize=10)                           
            # qt stuff
            self.pltCanvas = FigureCanvasQTAgg(self.mplFig)
            self.pltCanvas.setParent(self.ui.tab_graph)
            self.pltCanvas.setAutoFillBackground(False)
            self.pltCanvas.setObjectName("mplPlot")
            self.mplPlot = self.pltCanvas
            self.mplPlot.setVisible(False)
        else:
            self.mplPlot = QtGui.QLabel("Need matplotlib >= 1.0 !")

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplPlot.sizePolicy().hasHeightForWidth())
        self.mplPlot.setSizePolicy(sizePolicy)
        self.mplPlot.setObjectName("qwtPlot")
        self.mplPlot.updateGeometry()
        self.ui.stackedWidget.addWidget(self.mplPlot)

        self.ui.stackedWidget.setCurrentIndex(0)


    def change_tab(self, index_tab):
        if index_tab == 0:
            self.is_graph = 0
        else:
            self.is_graph = 1


    def disconnect(self):
        QObject.disconnect(self.canvas, SIGNAL( "keyPressed( QKeyEvent * )" ), self.pauseDisplay )
    
    def pauseDisplay(self,e):
      if ( e.modifiers() == Qt.ShiftModifier or e.modifiers() == Qt.MetaModifier ) and e.key() == Qt.Key_A:
        return True
      return False


    def keyPressEvent( self, e ):
      if ( e.modifiers() == Qt.ControlModifier or e.modifiers() == Qt.MetaModifier ) and e.key() == Qt.Key_C:
        items = ''
        for rec in range( self.ui.tableWidget.rowCount() ):
          items += '"' + self.ui.tableWidget.item( rec, 0 ).text() + '",' + self.ui.tableWidget.item( rec, 1 ).text() + "\n"
        if not items == '':
          clipboard = QApplication.clipboard()
          clipboard.setText( items )
      elif (self.pauseDisplay(e)):
        pass
      else:
        QWidget.keyPressEvent( self, e )


    def printValue(self,position):

        if self.canvas.layerCount() == 0:
            self.values=[]         
            self.showValues()
            return
        
        needextremum = self.ui.cbxGraph.isChecked() # if plot is checked

        # count the number of requires rows and remember the raster layers
        nrow=0
        rasterlayers=[]
        layersWOStatistics=[]

        for i in range(self.canvas.layerCount()):
            layer = self.canvas.layer(i)
            if (layer!=None and layer.isValid() and layer.type()==QgsMapLayer.RasterLayer):
              if QGis.QGIS_VERSION_INT >= 10900: # for QGIS >= 1.9
                if not layer.dataProvider():
                  continue

                if not layer.dataProvider().capabilities() & QgsRasterDataProvider.IdentifyValue:
                  continue

                nrow+=layer.bandCount()
                rasterlayers.append(layer)

              else: # < 1.9
                if layer.providerKey()=="wms":
                  continue

                if layer.providerKey()=="grassraster":
                  nrow+=1
                  rasterlayers.append(layer)
                else: # normal raster layer
                  nrow+=layer.bandCount()
                  rasterlayers.append(layer)
                
                  
        # create the row if necessary
        self.ui.tableWidget.setRowCount(nrow)

        irow=0
        self.values=[]
        self.ymin=1e38
        self.ymax=-1e38

        if QGis.QGIS_VERSION_INT >= 10900:
            mapCanvasSrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
        else:
            mapCanvasSrs = self.iface.mapCanvas().mapRenderer().destinationSrs()

        # TODO - calculate the min/max values only once, instead of every time!!!
        # keep them in a dict() with key=layer.id()
                
        for layer in rasterlayers:
            layername=unicode(layer.name())
            if QGis.QGIS_VERSION_INT >= 10900:
                layerSrs = layer.crs()
            else:
                layerSrs = layer.srs()

            pos = position         

            # if given no position, get dummy values
            if position is None:
                pos = QgsPoint(0,0)
            # transform points if needed
            elif not mapCanvasSrs == layerSrs and self.iface.mapCanvas().hasCrsTransformEnabled():
              srsTransform = QgsCoordinateTransform(mapCanvasSrs, layerSrs)
              try:
                pos = srsTransform.transform(position)
              except QgsCsException, err:
                # ignore transformation errors
                continue

            if QGis.QGIS_VERSION_INT >= 10900: # for QGIS >= 1.9
              if not layer.dataProvider():
                continue

              ident = None
              if position is not None:
                canvas = self.iface.mapCanvas()

                # first test if point is within map layer extent 
                # maintain same behaviour as in 1.8 and print out of extent
                if not layer.dataProvider().extent().contains( pos ):
                  ident = dict()
                  for iband in range(1,layer.bandCount()+1):
                    ident[iband] = str('out of extent')
                # we can only use context if layer is not projected
                elif canvas.hasCrsTransformEnabled() and layer.dataProvider().crs() != canvas.mapRenderer().destinationCrs():
                  ident = layer.dataProvider().identify(pos, QgsRaster.IdentifyFormatValue ).results()
                else:
                  extent = canvas.extent()
                  width = round(extent.width() / canvas.mapUnitsPerPixel());
                  height = round(extent.height() / canvas.mapUnitsPerPixel());

                  extent = canvas.mapRenderer().mapToLayerCoordinates( layer, extent );

                  ident = layer.dataProvider().identify(pos, QgsRaster.IdentifyFormatValue, canvas.extent(), width, height ).results()
                if not len( ident ) > 0:
                    continue

              # if given no position, set values to 0
              if position is None and ident is not None and ident.iterkeys() is not None:
                  for key in ident.iterkeys():
                      ident[key] = layer.dataProvider().noDataValue(key)

              for iband in range(1,layer.bandCount()+1): # loop over the bands
                layernamewithband=layername
                if ident is not None and len(ident)>1:
                    layernamewithband+=' '+layer.bandName(iband)

                if not ident or not ident.has_key( iband ): # should not happen
                  bandvalue = "?"
                else:
                  bandvalue = ident[iband]
                  if bandvalue is None:
                      bandvalue = "no data"

                self.values.append((layernamewithband,str(bandvalue)))


            else: # QGIS < 1.9
              isok,ident = layer.identify(pos)
              if not isok:
                  continue

              # if given no position, set values to 0
              if position is None:
                  for key in ident.iterkeys():
                      ident[key] = 0

              if layer.providerKey()=="grassraster":
                if not ident.has_key("value"):
                  continue
                value = ident["value"]
                if value is None:
                  continue
                if isinstance(value, str):
                  # if this is not a double, it is probably a (GRASS string like
                  # 'out of extent' or 'null (no data)'. Let's just show that:
                  self.values.append((layername, value))
                  continue
                self.values.append((layername,value))
                if needextremum:
                  self.ymin = min(self.ymin,value)
                  self.ymax = max(self.ymax,value)

              else:
                for iband in range(1,layer.bandCount()+1): # loop over the bands
                  bandvalue=ident[layer.bandName(iband)]
                  layernamewithband=layername
                  if len(ident)>1:
                      layernamewithband+=' '+layer.bandName(iband)

                  self.values.append((layernamewithband,bandvalue))

                  if needextremum:
                      has_stats=layer.hasStatistics(i)
                      if has_stats:
                          cstr=layer.bandStatistics(iband)
                      if has_stats:
                          self.ymin=min(self.ymin,cstr.minimumValue)
                          self.ymax=max(self.ymax,cstr.maximumValue)
                      else:
                          self.ymin=min(self.ymin,layer.minimumValue(i))
                          self.ymax=max(self.ymax,layer.maximumValue(i))

        self.showValues()

    def showValues(self):
        if self.is_graph:
            #TODO don't plot if there is no data to plot...
            self.plot()
        else:
            self.printInTable()


    def printInTable(self):

        irow=0
        for row in self.values:
          layername,value=row

          if (self.ui.tableWidget.item(irow,0)==None):
              # create the item
              self.ui.tableWidget.setItem(irow,0,QTableWidgetItem())
              self.ui.tableWidget.setItem(irow,1,QTableWidgetItem())

          self.ui.tableWidget.item(irow,0).setText(layername)
          self.ui.tableWidget.item(irow,1).setText(value)
          irow+=1


    def plot(self):

        numvalues=[]
        if ( self.hasmpl ):
            for row in self.values:
                layername,value=row
                try:
                    numvalues.append(float(value))
                except:
                    numvalues.append(0)

        ymin = self.ymin
        ymax = self.ymax
        if self.ui.leYMin.text() != '' and self.ui.leYMax.text() != '': 
            ymin = float(self.ui.leYMin.text())
            ymax = float(self.ui.leYMax.text())

        elif ( self.hasmpl ):

            self.mplPlt.clear()
            self.mplPlt.plot(range(1,len(numvalues)+1), numvalues, marker='o', color='k', mfc='b', mec='b')
            self.mplPlt.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            self.mplPlt.yaxis.set_minor_locator(ticker.AutoMinorLocator())
            self.mplPlt.set_xlim( (1-0.25,len(self.values)+0.25 ) )
            self.mplPlt.set_ylim( (ymin, ymax) ) 
            self.mplFig.draw()


    def statsNeedChecked(self, indx):
        #self.statsChecked = False
        self.invalidatePlot()

    def invalidatePlot(self,replot=True):
        self.statsChecked = False
        if self.mplLine is not None:
            del self.mplLine
            self.mplLine = None
        #update empty plot
        if replot and self.ui.cbxGraph.isChecked():
            #self.values=[]
            self.printValue( None )

    def resizeEvent(self, event):
        self.invalidatePlot()

