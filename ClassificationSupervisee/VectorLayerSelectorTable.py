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
from VectorLayerSelectorItem import VectorLayerSelectorItem

class VectorLayerSelectorTable(QtGui.QWidget):
    def __init__(self, layers, parent = None):
        super(VectorLayerSelectorTable, self).__init__(parent)
        
        self.layers = layers
        
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        
        self.label = QtGui.QLabel("Echantillons d'apprentissage :")

        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0,270)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.setTableContent()
        
        self.selectallbutton = QtGui.QPushButton(u"(Dé)sélectionner tout")
        self.selectallbutton.clicked.connect(self.selectAll)
        
        self.selectallbuttonlayout = QtGui.QHBoxLayout()
        self.selectallbuttonlayout.addStretch()
        self.selectallbuttonlayout.addWidget(self.selectallbutton)
        self.selectallbuttonlayout.addStretch()
        
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.table)
        self.verticalLayout.addLayout(self.selectallbuttonlayout)
        
        self.setLayout(self.verticalLayout)

    def selectAll(self):
        checked = False
        for i in range(len(self.layers)):
            widget = self.table.cellWidget(i, 0)
            if not widget.isChecked():
                checked = True
                break
        for i in range(len(self.layers)):
            widget = self.table.cellWidget(i, 0)
            widget.setChecked(checked)

    def setTableContent(self):
        n = len(self.layers)
        self.table.setRowCount(n)
        for i in range(n):
            item = VectorLayerSelectorItem(self.layers[i], None)
            self.table.setCellWidget(i,0, item)

    def getSelectedOptions(self):
        selectedLayers = []
        for i in range(len(self.layers)):
            widget = self.table.cellWidget(i, 0)
            if widget.isChecked():
                selectedLayers.append( (self.layers[i], widget.getColor(), widget.getLabel()) )
        return selectedLayers
    
    
    def set_layers(self, layers):
        self.table.clear()
        self.layers = layers
        self.setTableContent()
        