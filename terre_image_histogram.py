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

from numpy import arange, sin, pi, cumsum, percentile
import numpy.ma as ma


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
#import matplotlib.pyplot as plt

import manage_QGIS

import math

#import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger( 'TerreImage_Histograms' )
logger.setLevel(logging.INFO)

from terre_image_environement import TerreImageParamaters


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
        self.real_x_min = 0
        self.real_x_max = 0
        self.change_min = True


    def get_2_98_percent(self, sizeX, sizeY, histogram):
        # get 2 - 98 %
        logger.debug(  "sizeX, sizeY" + str(sizeX) + " " + str(sizeY))
        nb_pixels = sizeX * sizeY
        logger.debug("nb_pixels: " + str(nb_pixels))
        
        nb_pixels_2 = int(float(nb_pixels * 0.02))
        nb_pixels_98 = int(float(nb_pixels * 0.98))
        
        logger.debug(  "nb_pixels_2, nb_pixels_98: "  + str(nb_pixels_2) + " " + str(nb_pixels_98))
        
        hist_cum = cumsum(histogram)
        #print "histogram", histogram
        #print "hist cum", hist_cum
        print "len(hist_cum)", len(hist_cum)
        
        self.x_min = 0
        self.x_max = len(hist_cum)
        hist_cum[-1] + self.rasterMin
        for index in range(0,len(hist_cum)-1):
            if hist_cum[index+1] > nb_pixels_2 and self.x_min == 0 :
                self.x_min = index + self.rasterMin
            if hist_cum[index+1] > nb_pixels_98 :
                self.x_max = index + self.rasterMin
                break;
            
        print "self.x_min, self.x_max", self.x_min, self.x_max
        
        logger.debug(  "self.x_min, self.x_max" + str(self.x_min) + " " + str(self.x_max))
        self.x_min = (self.x_min-self.rasterMin)*self.bin_witdh+self.rasterMin
        self.x_max = (self.x_max-self.rasterMin)*self.bin_witdh+self.rasterMin
        self.two_min = self.x_min
        self.ninety_eight_max = self.x_max
            
        print "self.x_min, self.x_max", self.x_min, self.x_max
            
        self.real_x_min = 0
        self.real_x_max = 0


    def get_GDAL_histogram( self, image, band_number, qgis_layer, no_data=-1 ):
        """
        From the given binary image, compute histogram and return the number of 1
        """
        histogram = []

        logger.debug( "image: " + image + " band: " + str(band_number) )
        dataset = gdal.Open(image, gdal.GA_ReadOnly)
        if dataset is None:
            print "Error : Opening file ", image
        else :
            #get raster band
            band = dataset.GetRasterBand(band_number)
            if no_data != -1:
                band.SetNoDataValue(no_data)
            
            #get raster and overview if available
            overview = 2
            if overview < band.GetOverviewCount() :
                band_overview = band.GetOverview(overview)
            else :
                band_overview = band
                
            # get overview statistics
            self.rasterMin, self.rasterMax, mean, stddev = band_overview.ComputeStatistics(True)
            print self.rasterMin, self.rasterMax, mean, stddev
            logger.debug( "self.rasterMax, self.rasterMin" + str(self.rasterMax) + " " + str(self.rasterMin) )
            nbVal = self.rasterMax - self.rasterMin
            print "nbVal", nbVal

            #taking the size of the raster
            sizeX = float(band_overview.XSize)
            sizeY = float(band_overview.YSize)
            print "totalXSize", sizeX
            print "totalYSize", sizeY
            
            #computing nb bins
            stddev_part = 3.5 * stddev 
            sizexy_part = math.pow( sizeX*sizeY, 1./3. )
            print "stddev", stddev_part
            print "sizexy", sizexy_part
            
            # warning stddev
            nb_bin_part = (3.5 * stddev ) / (math.pow( sizeX*sizeY, 1./3. ) )
            print nb_bin_part
            self.nb_bin = int(math.ceil(nbVal / nb_bin_part))
            print "nb_bin", self.nb_bin
            
            histogram = band_overview.GetHistogram(self.rasterMin, self.rasterMax+1, self.nb_bin, approx_ok = 0)
            
            # removing 0 at the end of the histogram
            while len(histogram) > 1 and histogram[-1] == 0 :
                del histogram[-1]
            print "histogram", histogram
            
            self.bin_witdh = float(self.rasterMax - self.rasterMin)/len(histogram)
            print "bin_witdh", self.bin_witdh
            
            self.get_2_98_percent(sizeX, sizeY, histogram)
            
            
            
            return histogram
        
        
    def display_histogram(self, filename, band, color, name, qgis_layer, no_data=-1):
        self.color = color
        self.name = name
        
        #getting histogram
        if name == "NDVI":
            histogram = self.get_GDAL_histogram(filename, band, qgis_layer)
        else :
            histogram = self.get_GDAL_histogram(filename, band, qgis_layer, no_data)

        #setting plot axis
        self.t = arange(0, len(histogram))*self.bin_witdh + self.rasterMin#*(self.rasterMax - self.rasterMin)/self.nb_bin + self.rasterMin #range(0, len(histogram))
        self.s = histogram
        logger.debug(  "len s and len t"+ str(len(self.s)) + " " + str(len(self.t)))
        
        #draw histogram, 2, 98 % and connect canvas
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
        logger.debug(  "draw reset" )
        self.axes.clear()
        self.draw_histogram()
        if self.two_min and self.ninety_eight_max:
            logger.debug(  "self.two_min, self.ninety_eight_max" + str(self.two_min) + str(self.ninety_eight_max))
            self.axes.axvline(x=self.two_min,c="red",linewidth=2,zorder=0, clip_on=False)
            self.axes.axvline(x=self.ninety_eight_max,c="red",linewidth=2,zorder=0, clip_on=False)
        self.axes.figure.canvas.draw()
        self.x_min = self.two_min
        self.x_max = self.ninety_eight_max 
        self.emit( QtCore.SIGNAL("valueChanged()") )


    def draw_min_max_percent(self):
        if self.x_min and self.x_max:
            print "self.x_min, self.x_max", self.x_min, self.x_max
            logger.debug( "self.x_min, self.x_max" + str(self.x_min) + str(self.x_max))
            self.axes.axvline(x=self.x_min,c="red",linewidth=2,zorder=0, clip_on=False)
            self.axes.axvline(x=self.x_max,c="red",linewidth=2,zorder=0, clip_on=False)
            
        
    def on_press(self, event):
        """
        Check if the clicked point is nearer from x_min than from x_max
        """
        self.do_change = True
        logger.debug( 'press')
        x = event.xdata
        if x :
            #knowing which line to move
            if abs(x-self.x_min) < abs(x-self.x_max):
                self.change_min = True
            else:
                self.change_min = False
            #self.valueChanged.emit()
        else:
            self.do_change = False
        

    def on_release(self, event):
        """
        Get asbscissas of new x_min or x_max
        """
        if self.do_change and event.xdata:
            logger.debug( 'release')
            # classic case
            last_min = self.x_min
            last_max = self.x_max
            if self.change_min :
                self.x_min = event.xdata
            else:
                self.x_max = event.xdata
            #if the user drag the max line under the min line, switch the values
            if self.x_min > self.x_max:
                temp = self.x_min
                self.x_min = self.x_max
                self.x_max = temp
            if self.x_min < self.rasterMin:
                self.x_min = self.rasterMin
            if self.x_max > self.rasterMax:
                self.x_max = self.rasterMax
                
                
            self.axes.clear()
            self.draw_histogram()
            #self.axes.plot(self.t, self.s, self.color)
            #self.axes.plot(self.x1, self.x1, 'g^')
            self.draw_min_max_percent()
            #self.axes.vlines(self.x1, [0], self.x1)
    #         self.axes.set_xlabel('time (s)')
    #         self.axes.set_title('Vertical lines demo')
            
            print self.color
            p = TerreImageParamaters()
            
            
            self.axes.figure.canvas.draw()
            self.emit( QtCore.SIGNAL("valueChanged()") )
            logger.debug( str(self.x_min) + " " + str(self.x_max))



class TerreImageHistogram(QtGui.QWidget, QtCore.QObject) :#, Ui_Form):
    
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
        
        self.dock_opened = False
        

    def set_buttons(self):
        b = QtGui.QPushButton("Remise à zéro")
        b.clicked.connect(self.reset)
        self.l.addWidget(b)
        
        
    def reset(self):
        logger.debug( "resset" )
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
        logger.debug( forms )
        #emit signal
        self.emit( QtCore.SIGNAL("threshold(PyQt_PyObject)"), forms )
        
        
        
class TerreImageHistogram_monoband(TerreImageHistogram) :#, Ui_Form):        
        
    def __init__(self, layer, canvas, processing=None, specific_band=-1):
        #super(TerreImageHistogram_monoband, self).__init__(layer, 1) 
        TerreImageHistogram.__init__( self, layer, 1 )
        self.canvas = processing.mirror.mainWidget.canvas
        
        self.specific_band = specific_band
        
        if specific_band == -1:
            self.sc_1.display_histogram(self.layer.get_source(), 1, 'k', layer.name(), layer.get_qgis_layer())
        else :
            self.sc_1.display_histogram(self.layer.get_source(), specific_band, 'k', layer.name(), layer.get_qgis_layer(), 0)
        self.set_buttons()
        
        seuil = QtGui.QPushButton("Seuillage")
        seuil.clicked.connect(self.seuillage)
        self.l.addWidget(seuil)
           
           
    def valueChanged(self):
        logger.debug( "value changed" )
        values = [ (self.sc_1.x_min, self.sc_1.x_max ) ]
        logger.debug( "values" + str( values ))
        manage_QGIS.custom_stretch(self.layer.qgis_layer, values, self.canvas, mono=True)
        #self.emit( QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), values )           
           
           
    def seuillage(self):
        forms = []
        if self.specific_band == -1:
            forms.append( "\"if(((im1b1>" + str(self.sc_1.x_min) + ") and (im1b1<" + str(self.sc_1.x_max) + ")), im1b1, 0)\"" )
        else :
            forms.append( "\"if(((im1b" + str(self.specific_band) +">" + str(self.sc_1.x_min) + ") and (im1b" + str(self.specific_band) +"<" + str(self.sc_1.x_max) + ")), im1b" + str(self.specific_band) +", 0)\"" )
        #emit signal
        self.emit( QtCore.SIGNAL("threshold(PyQt_PyObject)"), forms )
           
           
           
class TerreImageHistogram_multiband(TerreImageHistogram) :#, Ui_Form):    
      
    def __init__(self, layer, canvas, nb_bands = 3, processing=None):
        #super(TerreImageHistogram_monoband, self).__init__(layer, nb_bands) 
        TerreImageHistogram.__init__( self, layer, nb_bands )  
        
        
        logger.debug( "processing" + str(processing))
        if processing is None:
            logger.debug( "processing none")
            self.canvas = canvas
            self.processing=None
        else:
            #print "canvas", canvas
            #print "processing.mirror.mainWidget.canvas", processing.mirror.mainWidget.canvas
            logger.debug( "processing not none")
            self.canvas = processing.mirror.mainWidget.canvas
            self.processing = processing
        
        self.sc_2 = MyMplCanvas(self, width=5, height=4, dpi=100)
        QtCore.QObject.connect( self.sc_2, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        self.sc_3 = MyMplCanvas(self, width=5, height=4, dpi=100)
        QtCore.QObject.connect( self.sc_3, QtCore.SIGNAL( "valueChanged()" ), self.valueChanged )
        self.l.addWidget(self.sc_2)
        self.l.addWidget(self.sc_3)
        
        if processing is None:
            self.sc_1.display_histogram(self.layer.get_source(), self.layer.pir, 'r', "Plan R : BS PIR", layer.get_qgis_layer(), 0)
            self.sc_2.display_histogram(self.layer.get_source(), self.layer.red, 'g', "Plan V : BS R", layer.get_qgis_layer(), 0)
            self.sc_3.display_histogram(self.layer.get_source(), self.layer.green, 'b', "Plan B : BS V", layer.get_qgis_layer(), 0)
        else:
            self.sc_1.display_histogram(self.processing.output_working_layer.get_source(), self.layer.red, 'r', "Plan R : BS R", layer.get_qgis_layer(), 0)
            self.sc_2.display_histogram(self.processing.output_working_layer.get_source(), self.layer.green, 'g', "Plan V : BS V", layer.get_qgis_layer(), 0)
            self.sc_3.display_histogram(self.processing.output_working_layer.get_source(), self.layer.blue, 'b', "Plan B : BS B", layer.get_qgis_layer(), 0)
        self.set_buttons()
        
        
           
    def valueChanged(self):
        values = [ (self.sc_1.x_min, self.sc_1.x_max ), (self.sc_2.x_min, self.sc_2.x_max ), (self.sc_3.x_min, self.sc_3.x_max )]
        logger.debug( "values" + str(values))
        logger.debug( self.canvas )
        if self.processing:
            manage_QGIS.custom_stretch(self.processing.output_working_layer.get_qgis_layer(), values, self.canvas)
        else:
            manage_QGIS.custom_stretch(self.layer.qgis_layer, values, self.canvas)
        #self.emit( QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), values )           
           

        
        
        