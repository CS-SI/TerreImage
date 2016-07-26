# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-11-03
        copyright            : (C) 2014 by CNES
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
import os
import ConfigParser
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QDialog, QPixmap

from ui_dlg import Ui_DlgAbout
from TerreImage import name, description, version
import platform

try:
    import resources
except ImportError:
    import resources_rc


class DlgAbout(QDialog, Ui_DlgAbout):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__),'metadata.txt'))

        name        = config.get('general', 'name')
        description = config.get('general', 'description')
        version     = config.get('general', 'version')

        # self.title.setText( name )
        # self.description.setText( description )

        text = self.txt.toHtml()
        text = text.replace("$PLUGIN_NAME$", name)
        text = text.replace("$PLUGIN_VERSION$", version)

        subject = "Help: %s" % name
        body = """\n\n
--------
Plugin name: %s
Plugin version: %s
Python version: %s
Platform: %s - %s
--------
""" % (name, version, platform.python_version(), platform.system(), platform.version())

        mail = QUrl("mailto:abc@abc.com")
        mail.addQueryItem("subject", subject)
        mail.addQueryItem("body", body)

        text = text.replace("$MAIL_SUBJECT$", unicode(mail.encodedQueryItemValue("subject")))
        text = text.replace("$MAIL_BODY$", unicode(mail.encodedQueryItemValue("body")))

        self.txt.setHtml(text)
