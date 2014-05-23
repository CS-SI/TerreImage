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
from PyQt4 import QtCore, QtGui
from qgis.gui import *
from qgis.core import *

class RasterLayerSelectorItem(QtGui.QWidget):

    def __init__(self, layer, parent = None):
        super(RasterLayerSelectorItem, self).__init__(parent)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        
        self.checkbox = QtGui.QCheckBox()
        self.checkbox.setText(layer.name())
        
        self.horizontalLayout.addWidget(self.checkbox)
        self.horizontalLayout.addStretch()
        self.setLayout(self.horizontalLayout)

    def setChecked(self, val):
        self.checkbox.setChecked(val)

    def isChecked(self):
        return self.checkbox.isChecked()
