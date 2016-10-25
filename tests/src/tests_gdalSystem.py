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
import shutil
from terre_image_test_case import TerreImageTestCase
from TerreImage import terre_image_gdal_system
from TerreImage.terre_image_exceptions import TerreImageRunProcessError


class TestGdalSystem(TerreImageTestCase):


    def setUp(self):
        """
        Defines the test image
        Returns:

        """
        self.image_test = os.path.join(self.data_dir_input, "taredji_extract.TIF")

    def testUnionPolygonsWithOGR_ok(self):
        """
        Test on Terre Image unionPolygonsWithOGR
        Returns:

        """
        green_files = os.path.join(self.data_dir_input, "classif", 'samples', "green.*")
        os.system("cp {} {}".format(green_files, self.working_dir))
        green = os.path.join(self.working_dir, "green.shp")
        road_files = os.path.join(self.data_dir_input, "classif", 'samples', "road.*")
        os.system("cp {} {}".format(road_files, self.working_dir))
        road = os.path.join(self.working_dir, "road.shp")
        union = terre_image_gdal_system.unionPolygonsWithOGR([green, road], self.working_dir)

    def test_Gdaladdo(self):
        """
        Test call of gdaladdo
        Returns:

        """
        copy_image_test = os.path.join(self.working_dir, os.path.basename(self.image_test))
        shutil.copy(self.image_test, copy_image_test)
        output_image = terre_image_gdal_system.compute_overviews(copy_image_test)
        split = os.path.splitext(os.path.basename(self.image_test))
        ovr_file = os.path.join(self.working_dir, os.path.basename(self.image_test) + ".ovr")
        print "Test existence of {}".format(ovr_file)
        self.assertTrue(os.path.exists(ovr_file))

    def test_gdal_edit_remove_no_data(self):
        """
        Test on removing no data value
        Returns:

        """
        copy_image_test = os.path.join(self.working_dir, os.path.basename(self.image_test))
        shutil.copy(self.image_test, copy_image_test)
        with self.assertRaises(TerreImageRunProcessError):
            terre_image_gdal_system.gdal_edit_remove_no_data(copy_image_test)

        #TO DO: add a assertion on no data



if __name__ == '__main__':
    unittest.main()