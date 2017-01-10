# -*- coding: utf-8 -*-
"""
/***************************************************************************
TerreImage
                                 A QGIS plugin
                              -------------------
        begin               : 2016-06-29
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

from TerreImage import terre_image_logging

class TestTerreImageLogging(TerreImageTestCase):


    def test_logging(self):
        """
        Test of create_vrt_from_filelist
        Returns:

        """
        logger = terre_image_logging.configure_logger()
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')
        # self.assertTrue(False)