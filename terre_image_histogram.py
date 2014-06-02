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
from matplotlib.patches import Rectangle

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
    __pyqtSignals__ = ("valueChanged()")
    
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
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

        self.two_min = 0
        self.ninety_eight_max = 0
        self.x_min = 0
        self.x_max = 0
        self.change_min = True


    def get_GDAL_histogram( self, image, band ):
        """
        From the given binary image, compute histogram and return the number of 1
        """
        histogram = []
        print "image", image
        dataset = gdal.Open(str(image), gdal.GA_ReadOnly)
        if dataset is None:
            print "Error : Opening file ", image
        else :
            band = dataset.GetRasterBand(band)
            rasterMin, rasterMax = band.ComputeRasterMinMax()
            nbVal = rasterMax# - rasterMin
            if nbVal < 1 :
                return 0
            #get the histogram of the given raster
            #histogram = band.GetHistogram(rasterMin, rasterMax+1, int(nbVal+1), approx_ok = 0)
            histogram = band.GetHistogram(0, rasterMax+1, int(nbVal+1), approx_ok = 0)
            #print "histogram", histogram
            
            # get 2 - 98 %
            #taking the size of the raster
            sizeX = dataset.RasterXSize
            sizeY = dataset.RasterYSize
            print "sizeX, sizeY", sizeX, sizeY
            nb_pixels = sizeX * sizeY
            print nb_pixels
            
            nb_pixels_2 = int(float(nb_pixels * 0.02))
            nb_pixels_98 = int(float(nb_pixels * 0.98))
            
            print "nb_pixels_2, nb_pixels_98", nb_pixels_2, nb_pixels_98
            
            # catch the i where cum_hist(i) > nb_pixels_2 and nb_pixels_98
            hist_cum = 0
            for i in range(len(histogram)):
                #print "i", i
                if hist_cum > nb_pixels_2 and self.x_min == 0 :
                    self.x_min = i #+ rasterMin
                if hist_cum > nb_pixels_98 :
                    self.x_max = i #+ rasterMin
                    break;
                hist_cum += histogram[i]
            print "self.x_min, self.x_max", self.x_min, self.x_max
            self.two_min = self.x_min
            self.ninety_eight_max = self.x_max
            print "self.two_min, self.ninety_eight_max", self.two_min, self.ninety_eight_max

            return histogram
        
    def display_histogram(self, filename, band, color, name):
        self.color = color
        self.name = name
        histogram = self.get_GDAL_histogram(filename, band)
        #print histogram
        self.t = range(0, len(histogram))
        self.s = histogram
        self.draw_histogram()
        self.axes.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.axes.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.draw_min_max_percent()
        
        
    def draw_histogram(self):
        if self.t and self.s and self.color and self.name:
            self.axes.plot(self.t, self.s, self.color)
            xtext = self.axes.set_xlabel('Valeur') # returns a Text instance
            ytext = self.axes.set_ylabel('Nombre')
            self.axes.set_title(self.name)
            
    def draw_reset_percent(self):
        print "draw reset"
        self.axes.clear()
        self.draw_histogram()
        if self.two_min and self.ninety_eight_max:
             print "self.two_min, self.ninety_eight_max", self.two_min, self.ninety_eight_max
             self.axes.axvline(x=self.two_min,c="red",linewidth=2,zorder=0, clip_on=False)
             self.axes.axvline(x=self.ninety_eight_max,c="red",linewidth=2,zorder=0, clip_on=False)
        self.axes.figure.canvas.draw()
        self.x_min = self.two_min
        self.x_max = self.ninety_eight_max 
        self.emit( QtCore.SIGNAL("valueChanged()") )


    def draw_min_max_percent(self):
        if self.x_min and self.x_max:
            print "self.x_min, self.x_max", self.x_min, self.x_max
            self.axes.axvline(x=self.x_min,c="red",linewidth=2,zorder=0, clip_on=False)
            self.axes.axvline(x=self.x_max,c="red",linewidth=2,zorder=0, clip_on=False)
            
        
    def on_press(self, event):
        """
        Check if the clicked point is nearer from x_min than from x_max
        """
        print 'press'
        x = event.xdata
        # take x_min
        if abs(x-self.x_min) < abs(x-self.x_max):
            self.change_min = True
        else:
            self.change_min = False
        #self.valueChanged.emit()
        
        
        #self.x_min = 

    def on_release(self, event):
        """
        Check
        """
        print 'release'
        if self.change_min :
            self.x_min = event.xdata
        else:
            self.x_max = event.xdata
        
        self.axes.clear()
        self.draw_histogram()
        #self.axes.plot(self.t, self.s, self.color)
        #self.axes.plot(self.x1, self.x1, 'g^')
        self.draw_min_max_percent()
        #self.axes.vlines(self.x1, [0], self.x1)
#         self.axes.set_xlabel('time (s)')
#         self.axes.set_title('Vertical lines demo')
        
        self.axes.figure.canvas.draw()
        self.emit( QtCore.SIGNAL("valueChanged()") )
        print self.x_min, self.x_max



class TerreImageHistogram(QtGui.QWidget, QtCore.QObject) :#, Ui_Form):
    
    #__pyqtSignals__ = ("curveTitleChanged(str)", "hideCurve(int)", "colorChanged(QtGui.QColor)", "deleteCurve()")
    __pyqtSignals__ = ("valueChanged(PyQt_PyObject)", "threshold(PyQt_PyObject)")
    
    
    def __init__(self, layer):
        QtGui.QWidget.__init__(self)
        QtCore.QObject.__init__(self)
        #self.setupUi(self)
        
        self.layer = layer
        
        
        l = QVBoxLayout(self)
        self.sc_1 = MyMplCanvas(self, width=5, height=4, dpi=100)
        #self.sc_1.valueChanged.connect( self.valueChanged )
        QtCore.QObject.connect( self.sc_1, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        self.sc_2 = MyMplCanvas(self, width=5, height=4, dpi=100)
        QtCore.QObject.connect( self.sc_2, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        self.sc_3 = MyMplCanvas(self, width=5, height=4, dpi=100)
        QtCore.QObject.connect( self.sc_3, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        l.addWidget(self.sc_1)
        l.addWidget(self.sc_2)
        l.addWidget(self.sc_3)
        b = QtGui.QPushButton("Remise à zéro")
        b.clicked.connect(self.reset)
        l.addWidget(b)
        seuil = QtGui.QPushButton("Seuillage")
        seuil.clicked.connect(self.seuillage)
        l.addWidget(seuil)
        
        

        #file_pointer = rasterIO.opengdalraster(layer.get_source())
        # pir, red, green
        print "layer pir", layer.pir
        #band = rasterIO.readrasterband(file_pointer, 1)
        #sc_1.compute_initial_figure(band, 'r')
        self.sc_1.display_histogram(layer.get_source(), layer.pir, 'r', "Plan R : BS PIR")
        #band = rasterIO.readrasterband(file_pointer, 2)
        #sc_2.compute_initial_figure(band, 'g')
        self.sc_2.display_histogram(layer.get_source(), layer.red, 'g', "Plan V : BS R")
        #band = rasterIO.readrasterband(file_pointer, 3)
        #sc_3.compute_initial_figure(band, 'b')
        self.sc_3.display_histogram(layer.get_source(), layer.green, 'b', "Plan B : BS V")
        #dc.compute_initial_figure()
        
    def reset(self):
        print "resset"
        self.sc_1.draw_reset_percent()
        self.sc_2.draw_reset_percent()
        self.sc_3.draw_reset_percent()
        
    def seuillage(self):
        forms = []
        forms.append( "if(((im1b1>" + str(self.sc_1.x_min) + ") and (im1b1<" + str(self.sc_1.x_max) + ")), im1b1, 0)" )
        forms.append( "if(((im1b2>" + str(self.sc_2.x_min) + ") and (im1b2<" + str(self.sc_2.x_max) + ")), im1b2, 0)" )
        forms.append( "if(((im1b3>" + str(self.sc_3.x_min) + ") and (im1b3<" + str(self.sc_3.x_max) + ")), im1b3, 0)" )
        print forms
        #emit signal
        self.emit( QtCore.SIGNAL("threshold(PyQt_PyObject)"), forms )
        
    def valueChanged(self):
        print "value changed"
        values = [ (self.sc_1.x_min, self.sc_1.x_max ), (self.sc_2.x_min, self.sc_2.x_max ), (self.sc_3.x_min, self.sc_3.x_max )]
        print "values", values
        self.emit( QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), values )
        
        