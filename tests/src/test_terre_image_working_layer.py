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
from TerreImage.working_layer import WorkingLayer
from terre_image_test_case import TerreImageTestCase


class TestWorkingLayer(TerreImageTestCase):

    def setUp(self):
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")

    def testWorkingLayerWithoutQGISLayer_ok(self):
        """
        Test on Terre Image working layer creation
        Returns:

        """
        self.terre_image_layer = WorkingLayer(self.image_test, self.raster_layer, {'red':1, 'green':2, 'blue':3, 'pir':4, 'mir':None})
        self.assertIsNot( self.terre_image_layer.get_qgis_layer(), None)
        self.assertIs(self.terre_image_layer.get_source(), self.image_test)
        # while the layer is not loaded in qgis, this information is not available
        self.assertEqual(self.terre_image_layer.get_band_number(),0)
        self.assertEqual(self.terre_image_layer.has_natural_colors(), True)
        # can not test the whole string because of the dictionary
        print_message_start = "{} taredji_extract".format(self.image_test)
        generated_printed_message = str(self.terre_image_layer)
        self.assertTrue(generated_printed_message.startswith(print_message_start))


    def testWorkingLayerWithoutQGISLayer_colorMissingdef(self):
        """
        Def test on bad structure in Terre Image working layer creation
        Returns:

        """
        with self.assertRaises(KeyError):
          self.terre_image_layer = WorkingLayer(self.image_test, None, {'red':1, 'green':2, 'blue':3, 'pir':4})

if __name__ == '__main__':
    unittest.main()

