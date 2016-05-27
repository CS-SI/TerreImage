# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2016-05-24
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


import unittest
import os
from qgis.core import QgsRasterLayer
from TerreImage.working_layer import WorkingLayer
from terre_image_test_case import TerreImageTestCase


class TestWorkingLayer(TerreImageTestCase):

    def setUp(self):
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")
        self.raster_layer = QgsRasterLayer(self.image_test, "taredji_extract")

    def testWorkingLayerWithoutQGISLayer_ok(self):
        self.terre_image_layer = WorkingLayer(self.image_test, self.raster_layer, {'red':1, 'green':2, 'blue':3, 'pir':4, 'mir':None})


    def testWorkingLayerWithoutQGISLayer_colorMissingdef(self):
        with self.assertRaises(KeyError):
          self.terre_image_layer = WorkingLayer(self.image_test, self.raster_layer, {'red':1, 'green':2, 'blue':3, 'pir':4})

if __name__ == '__main__':
    unittest.main()

