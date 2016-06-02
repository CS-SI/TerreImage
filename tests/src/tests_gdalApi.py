# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2016-06-02
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
from terre_image_test_case import TerreImageTestCase
from TerreImage import terre_image_gdal_api


class TestMergeVectorData(TerreImageTestCase):

    def setUp(self):
        self.image_test = os.path.join(self.data_dir_input, "classif", "taredji_extract_1024.tif")
        self.vector_test = os.path.join(self.data_dir_input, "classif", 'samples', "green.shp")


    def testGetImageEPSGCodeWithGDAL_ok(self):
        """
        Test on Terre Image GetImageEPSGCodeWithGDAL
        Returns:

        """
        epsg_code = terre_image_gdal_api.get_image_epsg_code_with_gdal(self.image_test)
        self.assertEqual(int(epsg_code),4326)


    def testGetVectorEPSGCodeWithOGR_ok(self):
        """
        Test on Terre Image GetVectorEPSGCodeWithOGR
        Returns:

        """
        epsg_code = terre_image_gdal_api.get_vector_epsg_with_ogr(self.vector_test)
        self.assertEqual(int(epsg_code),4326)


    def testGetVectorEPSGCodeWithOGR_ok(self):
        """
        Test on Terre Image GetVectorEPSGCodeWithOGR
        Returns:

        """
        epsg_code = terre_image_gdal_api.get_vector_epsg_with_ogr(self.vector_test)
        self.assertEqual(int(epsg_code),4326)


if __name__ == '__main__':
    unittest.main()