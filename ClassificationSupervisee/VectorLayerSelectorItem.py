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

class VectorLayerSelectorItem(QtGui.QWidget):

    def __init__(self, layer, parent = None):
        super(VectorLayerSelectorItem, self).__init__(parent)

        # init color from Qgis layer proeperties
        self.color = self.getVectorLayerColor(layer)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        
        self.checkbox = QtGui.QCheckBox()
        self.checkbox.setText(layer.name())
        
        self.colorpicker = QtGui.QPushButton()
        self.updateColor()
        self.colorpicker.clicked.connect(self.selectColor)
        
        self.horizontalLayout.addWidget(self.checkbox)
        self.horizontalLayout.addStretch()
        self.horizontalLayout.addWidget(self.colorpicker)
        self.setLayout(self.horizontalLayout)

    def selectColor(self):
        color = QtGui.QColorDialog.getColor(self.getColor(), self, "Selectionner une couleur")
        if color.isValid():
            self.color = color
        self.updateColor()

    def updateColor(self):
        pixmap = QtGui.QPixmap(self.colorpicker.size())
        pixmap.fill(self.getColor())
        icon = QtGui.QIcon(pixmap)
        self.colorpicker.setIcon(icon)
        
    def getVectorLayerColor(self, layer):
        color = QtCore.Qt.white
        #if layer.isUsingRendererV2():
        rendererV2 = layer.rendererV2()
        if isinstance(rendererV2,QgsSingleSymbolRendererV2):
            sym = rendererV2.symbol()
            color = sym.color()          
#         else:
#             renderer = layer.renderer()
#             if isinstance(renderer,QgsSingleSymbolRenderer):
#                 sym = renderer.symbol()
#                 color = sym.fillColor()
        return color

    def setChecked(self, val):
        self.checkbox.setChecked(val)

    def isChecked(self):
        return self.checkbox.isChecked()

    def getColor(self):
        return self.color
        
    def getLabel(self):
        return self.checkbox.text()