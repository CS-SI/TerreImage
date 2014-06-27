# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-04-30
        copyright            : (C) 2014 by CS SI
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
 This script initializes the plugin, making it known to QGIS.
"""

def name():
    return "TerreImage"

def description():
    return ""

def version():
    return "2.3.6"

def qgisMinimumVersion():
    return "2.0"

def icon():
    return "icon.png"

def authorName():
    return "CS SI (alexia.mondot@c-s.fr)"


def classFactory(iface):
    # load QGISEducation class from file QGISEducation
    from qgiseducation import QGISEducation
    return QGISEducation(iface)
