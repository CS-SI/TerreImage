# -*- coding: utf-8 -*-
"""
/*=========================================================================

Copyright (c) Centre National d'Etudes Spatiales
All rights reserved.

The "ClassificationSupervisee" Quantum GIS plugin is distributed 
under the CeCILL licence version 2.
See Copyright/Licence_CeCILL_V2-en.txt or
http://www.cecill.info/licences/Licence_CeCILL_V2-en.txt for more details.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=========================================================================*/
"""

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# -*- coding: utf-8 -*-

from supervisedclassificationdialog import SupervisedClassificationDialog
from QGisLayers import QGisLayers

class SupervisedClassification:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        QGisLayers.setInterface(iface)
        
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/supervisedclassification"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale")[0:2]
       
        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/supervisedclassification_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
   

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/supervisedclassification/icon.png"), \
            "Classification Supervis�e", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Classification Supervis�e", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Classification Supervis�e",self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # create the dialog
        dlg = SupervisedClassificationDialog()
        # show the dialog
        dlg.show()
        # Run the dialog event loop
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            
            pass
