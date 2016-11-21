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
from TerreImage import terre_image_utils
from terre_image_test_case import TerreImageTestCase


class TestTerreImageUtils(TerreImageTestCase):

    def setUp(self):
        """
        Defines the test image and create a Terre Image working layer
        Returns:

        """
        self.image = os.path.join(self.data_dir_input, "taredji_extract.TIF")

    def test_get_info_from_metadata(self):
        """

        Returns:

        """
        list_mtd = terre_image_utils.get_info_from_metadata(self.image, None)

        list_baseline = [(u'Satellite', u'Pleiades1A '),
                         (u'Lieu', u'S\xe9n\xe9gal '),
                         (u'Lignes', '256'),
                         (u'Colonnes', '256'),
                         (u'R\xe9solution', '4.63654288652e-06'),
                         (u'Date', u'30/10/2012 '),
                         (u'Commentaire', u'')]



        self.assertEqual(list_mtd, list_baseline)



if __name__ == '__main__':
    unittest.main()

