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


class TestGdalSystem(TerreImageTestCase):

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


if __name__ == '__main__':
    unittest.main()