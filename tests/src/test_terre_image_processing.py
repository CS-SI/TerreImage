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
from TerreImage import terre_image_processing
from TerreImage.working_layer import WorkingLayer
from terre_image_test_case import TerreImageTestCase


class TestTerreImageProcessingMethods(TerreImageTestCase):

    def setUp(self):
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")
        self.terre_image_layer = WorkingLayer(self.image_test, None, {'red':1, 'green':2, 'blue':3, 'pir':4, 'mir':None})

    def test_ndvi(self):
        generated_image = terre_image_processing.ndvi(self.terre_image_layer, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_ndvi.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))

    def test_ndti(self):
        generated_image = terre_image_processing.ndti(self.terre_image_layer, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_ndti.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))

    def test_brightness(self):
        generated_image = terre_image_processing.brightness(self.terre_image_layer, self.working_dir)
        baseline = os.path.join(self.data_dir_baseline, "taredji_extract_brightness.tif")
        self.assertTrue(self.checkResult(generated_image, baseline))





if __name__ == '__main__':
    unittest.main()

