# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerreImage
                    -------------------
        begin               : 2016-06-20
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
 ***************************************************************************
"""

import os

### path
# windows
# comment the following lines when the custom path are used
dirname = os.path.dirname(os.path.abspath(__file__))
OTB_APPLICATION_PATH =  os.path.join(dirname, "win32", "plugin")
PATH = os.path.join(dirname, "win32", "bin")


# # configuration system for linux
# otb_dir = "/usr"

# Configuration for linux standalone package
# otb_dir = "/home/amondot/Downloads/OTB-5.2.1-Linux64/"


# OTB_APPLICATION_PATH =  os.path.join(otb_dir, "lib", "otb", "applications")
# PATH = os.path.join(otb_dir, "bin")
# LD_LIBRARY_PATH = ""


# custom
# otb_dir = "/home/amondot/dev/OTB/install-5.4.0-classic"
# OTB_APPLICATION_PATH =  os.path.join(otb_dir, "lib", "otb", "applications")
# PATH = os.path.join(otb_dir, "bin")
# LD_LIBRARY_PATH = os.path.join(otb_dir, "lib")

