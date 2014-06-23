# -*- coding: utf-8 -*-
"""
/***************************************************************************
 S2Catalog           A QGIS plugin :  S2 Catalog for specific Sentinel2 product.
                              -------------------
        begin                : 2013-06-12
        copyright            : (C) 2012-2013, CS Information Systems, CSSI
        contributors         : A. Mondot
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

#import system librairies
import os
import tempfile

#import loggin for debug messages
import logging
# create logger
logger = logging.getLogger('s2constant')


class TerreImageConstant(object):
    """
    This class allow to manage constants of the catalog.
    It manages:
        iface                  --    iface to link the catalog to qgis (adding layers, acces to canvas...)
        canvas                 --    mapCanvas of qgis == self.iface.mapCanvas() 
        legendInterface        --    acces from qgis to symbols, layers ...
        index_group            --    qgis group of terre_image.
    """
    instance = None
    def __new__(cls, *args, **kwargs): # __new__ always a classmethod
        if not cls.instance:
            cls.instance = super(TerreImageConstant, cls).__new__(cls, *args, **kwargs) #S2Constant.__S2Constant()
            cls.instance.__private_init__()
        return cls.instance
    
    def __private_init__(self):
        """
        Init to have constant values
        """
        self.iface = None   # iface
        self.canvas = None  # canvas
        self.legendInterface = None
        self.index_group = None
        


