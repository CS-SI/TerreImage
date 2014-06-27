# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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

		#self.title.setText( name() + version() )
		#self.description.setText( description() )

		text = self.txt.toHtml()
		text = text.replace( "$PLUGIN_NAME$", name() )
		text = text.replace( "$PLUGIN_VERSION$", version() )

		subject = "Help: %s" % name()
		body = """\n\n
--------
Plugin name: %s
Plugin version: %s
Python version: %s
Platform: %s - %s
--------
""" % ( name(), version(), platform.python_version(), platform.system(), platform.version() )

		mail = QUrl( "mailto:abc@abc.com" )
		mail.addQueryItem( "subject", subject )
		mail.addQueryItem( "body", body )

		text = text.replace( "$MAIL_SUBJECT$", unicode(mail.encodedQueryItemValue( "subject" )) )
		text = text.replace( "$MAIL_BODY$", unicode(mail.encodedQueryItemValue( "body" )) )

		self.txt.setHtml(text)



