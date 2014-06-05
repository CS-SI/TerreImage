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
import matplotlib.pyplot as plt

import manage_QGIS



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
        
        decimal_values = False
        
        print "image", image
        dataset = gdal.Open(str(image), gdal.GA_ReadOnly)
        if dataset is None:
            print "Error : Opening file ", image
        else :
            band = dataset.GetRasterBand(band)
            rasterMin, rasterMax = band.ComputeRasterMinMax()
            print rasterMax, rasterMin
            nbVal = rasterMax# - rasterMin
            if nbVal < 1 :
                print "nb val < 1", nbVal
                if nbVal != 0:
                    histogram = band.GetHistogram(rasterMin, rasterMax+1, int(nbVal+1)*100, approx_ok = 0)
                    decimal_values = True
                else:
                    return []
            else :
                #get the histogram of the given raster
                #histogram = band.GetHistogram(rasterMin, rasterMax+1, int(nbVal+1), approx_ok = 0)
                histogram = band.GetHistogram(0, rasterMax+1, int(nbVal+1), approx_ok = 0)
            print "histogram", histogram
            
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
            
            if decimal_values:
                parcours = arange(0, len(histogram)/100, 0.01)
            else:
                parcours = arange(0, len(histogram))
            cpt = 0
            for i in parcours: #range(len(histogram)):
                #print "i", i
                if hist_cum > nb_pixels_2 and self.x_min == 0 :
                    self.x_min = i #+ rasterMin
                if hist_cum > nb_pixels_98 :
                    self.x_max = i #+ rasterMin
                    break;
                hist_cum += histogram[cpt]
                cpt += 1
            print "self.x_min, self.x_max", self.x_min, self.x_max
            self.two_min = self.x_min
            self.ninety_eight_max = self.x_max
            print "self.two_min, self.ninety_eight_max", self.two_min, self.ninety_eight_max

            return histogram, decimal_values
        
    def display_histogram(self, filename, band, color, name):
        self.color = color
        self.name = name
        histogram, decimal_values = self.get_GDAL_histogram(filename, band)
        print type(histogram)
        print histogram
        if not decimal_values:
            self.t = arange(0, len(histogram)) #range(0, len(histogram))
        else:
            self.t = arange(0, len(histogram)/100, 0.01)
            locs,labels = plt.yticks()
            plt.yticks(locs, map(lambda x: "%.1f" % x, locs*1e9))
            #ylabel('microseconds (1E-9)'
        self.s = histogram
        print "len s and len t", len(self.s), len(self.t)
        print "self.t", self.t
        self.draw_histogram()
        self.axes.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.axes.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.draw_min_max_percent()
        
        
    def draw_histogram(self):
        if self.t.any() and self.s and self.color and self.name:
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
    
    
    def __init__(self, layer, nb_bands = 3):
        QtGui.QWidget.__init__(self)
        QtCore.QObject.__init__(self)
        #self.setupUi(self)
        
        self.layer = layer
        if nb_bands >= 3:
            self.nb_hist = 3
        else :
            self.nb_hist = 1
        
        self.l = QtGui.QVBoxLayout(self)
        self.sc_1 = MyMplCanvas(self, width=5, height=4, dpi=100)
        QtCore.QObject.connect( self.sc_1, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        self.l.addWidget(self.sc_1)
        

    def set_buttons(self):
        b = QtGui.QPushButton("Remise à zéro")
        b.clicked.connect(self.reset)
        self.l.addWidget(b)
#         seuil = QtGui.QPushButton("Seuillage")
#         seuil.clicked.connect(self.seuillage)
#         self.l.addWidget(seuil)
        
        
        
    def reset(self):
        print "resset"
        self.sc_1.draw_reset_percent()
        if self.nb_hist == 3 :
            self.sc_2.draw_reset_percent()
            self.sc_3.draw_reset_percent()
        
        
    def seuillage(self):
        forms = []
        forms.append( "\"if(((im1b1>" + str(self.sc_1.x_min) + ") and (im1b1<" + str(self.sc_1.x_max) + ")), im1b1, 0)\"" )
        if self.nb_hist == 3 :
            forms.append( "\"if(((im1b2>" + str(self.sc_2.x_min) + ") and (im1b2<" + str(self.sc_2.x_max) + ")), im1b2, 0)\"" )
            forms.append( "\"if(((im1b3>" + str(self.sc_3.x_min) + ") and (im1b3<" + str(self.sc_3.x_max) + ")), im1b3, 0)\"" )
        print forms
        #emit signal
        self.emit( QtCore.SIGNAL("threshold(PyQt_PyObject)"), forms )
        
        
        
class TerreImageHistogram_monoband(TerreImageHistogram) :#, Ui_Form):        
        
    def __init__(self, layer, canvas, processing=None, specific_band=-1):
        #super(TerreImageHistogram_monoband, self).__init__(layer, 1) 
        TerreImageHistogram.__init__( self, layer, 1 )
        self.canvas = processing.mirror.mainWidget.canvas
        
        if specific_band == -1:
            self.sc_1.display_histogram(self.layer.get_source(), 1, 'r', layer.name())
        else :
            self.sc_1.display_histogram(self.layer.get_source(), specific_band, 'r', layer.name())
        self.set_buttons()
        
        seuil = QtGui.QPushButton("Seuillage")
        seuil.clicked.connect(self.seuillage)
        self.l.addWidget(seuil)
           
    def valueChanged(self):
        print "value changed"
        values = [ (self.sc_1.x_min, self.sc_1.x_max ) ]
        print "values", values
        manage_QGIS.custom_stretch(self.layer.qgis_layer, values, self.canvas, mono=True)
        #self.emit( QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), values )           
           
           
           
class TerreImageHistogram_multiband(TerreImageHistogram) :#, Ui_Form):    
      
    def __init__(self, layer, canvas, nb_bands = 3):
        #super(TerreImageHistogram_monoband, self).__init__(layer, nb_bands) 
        TerreImageHistogram.__init__( self, layer, nb_bands )  
        self.canvas = canvas       
        
        self.sc_2 = MyMplCanvas(self, width=5, height=4, dpi=100)
        QtCore.QObject.connect( self.sc_2, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        self.sc_3 = MyMplCanvas(self, width=5, height=4, dpi=100)
        QtCore.QObject.connect( self.sc_3, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        self.l.addWidget(self.sc_2)
        self.l.addWidget(self.sc_3)
        
        
        self.sc_1.display_histogram(self.layer.get_source(), self.layer.pir, 'r', "Plan R : BS PIR")
        self.sc_2.display_histogram(self.layer.get_source(), self.layer.red, 'g', "Plan V : BS R")
        self.sc_3.display_histogram(self.layer.get_source(), self.layer.green, 'b', "Plan B : BS V")
        self.set_buttons()
        
        
           
    def valueChanged(self):
        values = [ (self.sc_1.x_min, self.sc_1.x_max ), (self.sc_2.x_min, self.sc_2.x_max ), (self.sc_3.x_min, self.sc_3.x_max )]
        print "values", values
        manage_QGIS.custom_stretch(self.layer.qgis_layer, values, self.canvas)
        #self.emit( QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), values )           
           

        
        
        