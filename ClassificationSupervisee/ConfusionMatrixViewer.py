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
import xml.etree.ElementTree as xml


def read_results_old(outputresults):
    percentage = {}
    root = xml.parse(outputresults).getroot()

    # Confusion matrix
    matrix = []
    for row in root.find("Resultats").find("MatriceConfusion").findall("Class"):
        matrix.append(row.text.split())
    '''
    for line in iter(root.find("Resultats").find("MatriceConfusion").text.splitlines()):
        if not line:
            continue
        matrix.append(line.split())
    '''

    # Kappa index
    kappa = float(root.find("Resultats").find("IndiceKappa").attrib["value"])

    # Class statistics
    for child in root.find("Resultats").find("Statistiques"):
        if child.tag == "Class":
            percentage[ int(child.attrib["label"]) ] = float(child.attrib["pourcentage"])

    return {"percentage": percentage, "confusion": matrix, "kappa": kappa}


def read_results(confmat, kappa, out_pop):

    # Class statistics
    percentage = {}
    root = xml.parse(out_pop).getroot()
    for child in root.find("Resultats").find("Statistiques"):
        if child.tag == "Class":
            percentage[ int(child.attrib["label"]) ] = float(child.attrib["pourcentage"])

    # Confusion matrix
    matrix = []
    f=open(confmat, "r")
    lines = f.readlines()
    for line in lines:
        if not line.startswith("#"):
            matrix.append([x.replace("\n", "") for x in line.split(",")])

    # Kappa index

    return {"percentage": percentage, "confusion": matrix, "kappa": kappa}


class ColorSquare(QtGui.QPushButton):
    def __init__(self, color, parent = None):
        super(ColorSquare, self).__init__(parent)

        pixmap = QtGui.QPixmap(self.size())
        pixmap.fill(color)
        icon = QtGui.QIcon(pixmap)
        self.setIcon(icon)
        self.setFlat(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setCheckable(False)

    def mouseMoveEvent(self, e):
        pass

    def mousePressEvent(self, e):
        pass

    def mouseReleaseEvent(self, e):
        pass


class ConfusionMatrixViewer(QtGui.QDialog):
    def __init__(self, selectedvectorlayers, confmat, kappa, out_pop, parent = None):
        QtGui.QDialog.__init__(self)

        results = read_results(confmat, kappa, out_pop)
        n = len(results["confusion"])

        self.setWindowTitle(u"Résultats")
        self.verticalLayout = QtGui.QVBoxLayout()

        self.verticalLayout.addWidget(QtGui.QLabel(u'La classification a été réalisée avec succès.'))
        self.verticalLayout.addWidget(QtGui.QLabel(''))
        self.verticalLayout.addWidget(QtGui.QLabel(u'Statistiques par classe en % de l\'image classée :'))

        self.statgrid = QtGui.QGridLayout()
        for i in range(len(selectedvectorlayers)):
            vectorlayer = selectedvectorlayers[i]
            classcolor = vectorlayer[1]
            classlabel = vectorlayer[2]

            self.statgrid.addWidget(ColorSquare(classcolor), i, 0)
            self.statgrid.addWidget(QtGui.QLabel(classlabel), i, 1)
            self.statgrid.addWidget(QtGui.QLabel( "%.1f %%" % (results["percentage"][i]) ), i, 2)

        self.stath = QtGui.QHBoxLayout()
        self.stath.addLayout(self.statgrid)
        self.stath.addStretch()
        self.verticalLayout.addLayout(self.stath)

        self.verticalLayout.addWidget(QtGui.QLabel(''))
        self.verticalLayout.addWidget(QtGui.QLabel(u'Calcul de bon classement des pixels des échantillons'))
        self.verticalLayout.addWidget(QtGui.QLabel(u'(matrice de confusion) :'))

        self.confusion = QtGui.QGridLayout()
        layernames = []
        matrix = results["confusion"]
        for row in range(n):
            layernames.append(selectedvectorlayers[row][2])
            for col in range(n):
                self.confusion.addWidget(QtGui.QLabel(matrix[row][col]), 2*row+2, 2*col+2)

        for i in range(n):
            layername = selectedvectorlayers[i][2]

            label1 = QtGui.QLabel(layername)
            values = "{color}".format(color=selectedvectorlayers[i][1].name())
            label1.setStyleSheet( "QLabel { color : %s; }" % (values) )
            # label1.setAutoFillBackground(True)

            label2 = QtGui.QLabel(layername)
            values = "{color}".format(color=selectedvectorlayers[i][1].name())
            label2.setStyleSheet( "QLabel { color : %s; }" % (values) )
            # label2.setAutoFillBackground(True)

            self.confusion.addWidget(label1, 0,     2*i+2)
            self.confusion.addWidget(label2, 2*i+2, 0    )

        for i in range(n):
            vline = QtGui.QFrame()
            vline.setFrameShadow(QtGui.QFrame.Plain)
            vline.setFrameShape(QtGui.QFrame.VLine)
            vline.setLineWidth(1)
            self.confusion.addWidget(vline, 0, 2*i+1, 2*n+2, 1)

            hline = QtGui.QFrame()
            hline.setFrameShadow(QtGui.QFrame.Plain)
            hline.setFrameShape(QtGui.QFrame.HLine)
            hline.setLineWidth(1)
            self.confusion.addWidget(hline, 2*i+1, 0, 1, 2*n+2)

        self.verticalLayout.addLayout(self.confusion)

        self.verticalLayout.addWidget(QtGui.QLabel(''))
        self.verticalLayout.addWidget(QtGui.QLabel( (u'Indice de qualité du classement (entre 0 et 1) : <b>%.6f</b>' % (results["kappa"]))))

        self.verticalLayout.addStretch()

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.okButton = QtGui.QPushButton("OK")
        self.buttonBox.addButton(self.okButton, QtGui.QDialogButtonBox.AcceptRole)
        QtCore.QObject.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.close)
        self.verticalLayout.addWidget(self.buttonBox)

        self.setLayout(self.verticalLayout)
