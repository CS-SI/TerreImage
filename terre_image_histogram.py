# -*- coding: utf-8 -*-
#!/usr/bin/env python
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




from __future__ import unicode_literals
import sys, os, random, string
from PyQt4 import QtGui, QtCore

from osgeo import gdal, gdalconst, ogr

from numpy import arange, sin, pi
import numpy.ma as ma

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

from pyrasterRasterIO import rasterIO
import matplotlib.pyplot as plt
 

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from ui_terre_image_curve import Ui_Form

import random


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        #self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


    def get_GDAL_histogram( self, image, band ):
        """
        From the given binary image, compute histogram and return the number of 1
        """
        histogram = []
        dataset = gdal.Open(str(image), gdal.GA_ReadOnly)
        if dataset is None:
            print "Error : Opening file ", image
        else :
            band = dataset.GetRasterBand(band)
            rasterMin, rasterMax = band.ComputeRasterMinMax()
            nbVal = rasterMax - rasterMin
            if nbVal < 1 :
                return 0
            #get the histogram of the given raster
            histogram = band.GetHistogram(rasterMin, rasterMax+1, int(nbVal+1), approx_ok = 0)
            return histogram
        

class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self, raster_matrix, color_c='k'):
        flat_raster = ma.compressed(raster_matrix)
        #ax.hist(self, x, bins=10, range=None, normed=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, **kwargs)
        #self.axes.hist(flat_raster, 500, normed=0, histtype='bar', align='mid', color=color_c)
        self.axes.hist(flat_raster, 500, normed=0, histtype='stepfilled', align='mid', color=color_c)
        #t = arange(0.0, 3.0, 0.01)
        #s = sin(2*pi*t)
        #self.axes.plot(t, s)
        
    def display_histogram(self, filename, band, color, name):
        histogram = self.get_GDAL_histogram(filename, band)
        #print histogram
        t = range(0, len(histogram))
        s = histogram
        self.axes.plot(t, s, color)
        xtext = self.axes.set_xlabel('Valeur') # returns a Text instance
        ytext = self.axes.set_ylabel('Nombre')
        self.axes.set_title(name)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
         self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [ random.randint(0, 10) for i in range(4) ]

        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()



class TerreImageHistogram(QtGui.QWidget) :#, Ui_Form):
    
    __pyqtSignals__ = ("curveTitleChanged(str)", "hideCurve(int)", "colorChanged(QtGui.QColor)", "deleteCurve()")
    
    
    def __init__(self, layer):
        QWidget.__init__(self)
        #self.setupUi(self)
        
        self.layer = layer
        
        
        l = QVBoxLayout(self)
#         sc = MyStaticMplCanvas(self, width=5, height=4, dpi=100)
#         l.addWidget(sc)
        
        
        sc_1 = MyStaticMplCanvas(self, width=5, height=4, dpi=100)
        sc_2 = MyStaticMplCanvas(self, width=5, height=4, dpi=100)
        sc_3 = MyStaticMplCanvas(self, width=5, height=4, dpi=100)
        #dc = MyDynamicMplCanvas(self, width=5, height=4, dpi=100)
        l.addWidget(sc_1)
        l.addWidget(sc_2)
        l.addWidget(sc_3)
        #l.addWidget(dc)

        file_pointer = rasterIO.opengdalraster(layer.get_source())
        # pir, red, green
        print "layer pir", layer.pir
        #band = rasterIO.readrasterband(file_pointer, 1)
        #sc_1.compute_initial_figure(band, 'r')
        sc_1.display_histogram(layer.get_source(), layer.pir, 'r', "Plan R : BS PIR")
        #band = rasterIO.readrasterband(file_pointer, 2)
        #sc_2.compute_initial_figure(band, 'g')
        sc_2.display_histogram(layer.get_source(), layer.red, 'g', "Plan V : BS R")
        #band = rasterIO.readrasterband(file_pointer, 3)
        #sc_3.compute_initial_figure(band, 'b')
        sc_3.display_histogram(layer.get_source(), layer.green, 'b', "Plan B : BS V")
        #dc.compute_initial_figure()
        
        
        
        
#         # matplotlib context:
#         self.mplFig = plt.figure(figsize=(8,11)) #facecolor='w', edgecolor='w', 
#          
#         # qt stuff
#         self.pltCanvas = FigureCanvasQTAgg(self.mplFig)
#         self.pltCanvas.setParent(self)
#         self.pltCanvas.setAutoFillBackground(False)
#         self.pltCanvas.setObjectName("mplPlot")
#         self.mplPlot = self.pltCanvas
#         self.mplPlot.setVisible(False)
#         self.addWidget(self.mplPlot)
#         xmin, xmax = xlim()
#         print "xmin, xman", xmin, xmax
#          
#         # Open a raster using rasterIO
#         # Open a gdal pointer to a file on disk
#         file_pointer = rasterIO.opengdalraster('/home/amondot/OTB-Data/Examples/QB_1_ortho.tif')
#         band = rasterIO.readrasterband(file_pointer, 1)
#         # Pass matrix representation of raster to function
#         self.rasterHistogram(band)
#         # Shows histogram on screen
        
 
    # Create a histogram function
    def rasterHistogram(self, raster_matrix):
        '''Accepts matrix and generates histogram'''
         
        # Line above is function docstring
        # Flatten 2d-matrix
        flat_raster = ma.compressed(raster_matrix)
         
        # Setup the plot (see matplotlib.sourceforge.net)
        ax = self.mplFig.add_subplot(1,1,1)
         
        # Plot histogram
        #ax.hist(self, x, bins=10, range=None, normed=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, **kwargs)
        ax.hist(flat_raster, 100, normed=0, histtype='bar', align='mid')
        # Show the plot on screen
        plt.show()
     

        
        
        
#         # should make figure light gray
#         self.mplBackground = None #http://www.scipy.org/Cookbook/Matplotlib/Animations
#         self.mplFig = plt.Figure(facecolor='w', edgecolor='w')
#         self.mplFig.subplots_adjust(left=0.1, right=0.975, bottom=0.13, top=0.95)
#         self.mplPlt = self.mplFig.add_subplot(111)   
#         self.mplPlt.tick_params(axis='both', which='major', labelsize=12)
#         self.mplPlt.tick_params(axis='both', which='minor', labelsize=10)                           
#         # qt stuff
#         self.pltCanvas = FigureCanvasQTAgg(self.mplFig)
#         self.pltCanvas.setParent(self.stackedWidget)
#         self.pltCanvas.setAutoFillBackground(False)
#         self.pltCanvas.setObjectName("mplPlot")
#         self.mplPlot = self.pltCanvas
#         self.mplPlot.setVisible(False)