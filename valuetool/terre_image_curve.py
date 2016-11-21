# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2014-05-06
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

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QColor, QWidget, QPixmap, QIcon, QInputDialog

from ui_terre_image_curve import Ui_Form

import random

# import logging for debug messages
from TerreImage import terre_image_logging
logger = terre_image_logging.configure_logger()


LETTERSTOQCOLOR = {"bleu": QColor(0, 132, 255), "vert": QColor(148, 255, 69),
                   "rouge": QColor(255, 30, 0), "cyan": QColor(0, 255, 204),
                   "magenta": QColor(255, 0, 255), "jaune": QColor(255, 255, 0),
                   "noir": QColor(0, 0, 0)}

FRENCHTOLETTER = {"bleu": 'b', "vert": 'g',
                       "rouge": 'r', "cyan": 'c',
                       "magenta": 'm', "jaune": 'y',
                       "noir": 'k'}

LETTERSTONAMECOLOR = {"b": "blue", "g": "green", "r": "red",
                           "c": "cyan", "m": "magenta",
                           "y": "yellow", "k": "black"}

NAMECOLORSTOLETTERS = dict((v, k) for k, v in LETTERSTONAMECOLOR.iteritems())

COLORS = ['b', 'r', 'g', 'c', 'm', 'y', 'k']



class TerreImageCurve(QWidget, Ui_Form):

    __pyqtSignals__ = ("curveTitleChanged(str)", "hideCurve(int)", "colorChanged()",
                       "deleteCurve()", "redraw()")

    def __init__(self, name, x, y, points, abs = None, color = None):
        QWidget.__init__(self)
        self.setupUi(self)

        self.name = name
        self.lineEdit_curve_name.setText(name)

        logger.debug("from curve: {} {}".format(x, y))
        self.coordinates = "[x=" + str(x) + ", y=" + str(y) + "]"
        self.label_coordinates.setText(self.coordinates)

        if color is None:
            logger.debug("len(colors): {}".format(len(COLORS)))
            color = COLORS[ random.randint(0, len(COLORS) - 1) ]
            logger.debug("color from creation courbe: {}".format(color))
        self.color = color

        if abs:
            self.abs = abs
        else:
            self.abs = None

        pixmap = QPixmap(self.pushButton_color.size())
        pixmap.fill(QColor(LETTERSTONAMECOLOR[self.color]))
        icon = QIcon(pixmap)
        self.pushButton_color.setIcon(icon)

        self.points = points

        # self.connect(self.lineEdit_curve_name, SIGNAL("textChanged(str)"), self, SIGNAL("curveTitleChanged(str)"))
        self.connect(self.lineEdit_curve_name, SIGNAL("editingFinished()"), self.set_name)
        self.connect(self.pushButton_color, SIGNAL("clicked()"), self.set_color)
        self.connect(self.pushButton_delete_curve, SIGNAL("clicked()"), self, SIGNAL("deleteCurve()"))
        self.connect(self.checkBox_curve_visible, SIGNAL("stateChanged(int)"), self.change_state)

    def change_state(self, state):
        print "====**State changed===="
        logger.info("====**State changed from ti_curve====")
        self.emit(SIGNAL("redraw()"))

    def display_points(self):
        logger.debug("checkBox_curve_visible.checkState() {}".format(self.checkBox_curve_visible.checkState()))
        return self.checkBox_curve_visible.checkState() == Qt.Checked

    def set_color(self):
        # couleur = QtGui.QColorDialog.getColor(QtCore.Qt.white)

        testqt, ok = QInputDialog.getItem(None, "Couleur", "Selection d'une couleur", LETTERSTOQCOLOR.keys(), False)
        if ok:
            # couleur = self.nameColorsToLetters[testqt]
            couleur = LETTERSTOQCOLOR[testqt]
            logger.debug(couleur)
            self.color = FRENCHTOLETTER[testqt]
        else:
            couleur = LETTERSTOQCOLOR['noir']
            self.color = 'b'

        # self.color = str(couleur.name())
        # logger.debug( couleur.name())

        # self.color = self.lettersToNameColor[testqt]

        pixmap = QPixmap(self.pushButton_color.size())
        # pixmap.fill(QColor(self.color))
        pixmap.fill(couleur)
        icon = QIcon(pixmap)
        self.pushButton_color.setIcon(icon)
        # logger.debug(  QColor(self.color) )

        # self.pushButton_color.setStyleSheet("background-color: " + self.color )

        # palette = QtGui.QPalette()
        # palette.setColor(QtGui.QPalette.ButtonText, self.lettersToQColor[testqt])
        # palette.setColor(10, couleur)
        # self.pushButton_color.setPalette(palette)
        self.emit(SIGNAL("redraw()"))

    def set_name(self, text = None):
        self.name = self.lineEdit_curve_name.text()

    def __str__(self):
        return "{} {} {} {}".format(self.name, self.coordinates, self.color, self.points)

    def has_abs(self):
        return self.abs is not None
