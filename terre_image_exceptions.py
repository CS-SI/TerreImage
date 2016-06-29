# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerreImage
                                 A QGIS plugin
                              -------------------
        begin               : 2016-06-27
        copyright           : (C) 2016 by CNES
        email               : alexia.mondot@c-s.fr
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


class ExceptionTemplate(Exception):
    def __call__(self, *args):
        return self.__class__(*(self.args + args))
    def __str__(self):
        return ': '.join(self.args)

class TerreImageError(ExceptionTemplate): pass

class TerreImageRunProcessError(ExceptionTemplate): pass