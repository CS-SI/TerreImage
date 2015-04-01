# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerreImage
                              -------------------
        begin                : 2014-06-12
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


class TerreImageParamaters(object):
    """
    """
    instance = None
    def __new__(cls, *args, **kwargs):  # __new__ always a classmethod
        if not cls.instance:
            cls.instance = super(TerreImageParamaters, cls).__new__(cls, *args, **kwargs)
            cls.instance.__private_init__()
        return cls.instance

    def __private_init__(self):
        """
        Init to have constant values
        """
        self.red_min = None
        self.red_max = None
        self.green_min = None
        self.green_max = None
        self.blue_min = None
        self.blue_max = None

    def is_complete(self):
        return self.red_max and self.red_min and self.blue_max and self.blue_min and self.green_max and self.green_min
