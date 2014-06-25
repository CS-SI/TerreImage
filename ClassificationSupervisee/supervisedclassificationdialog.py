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
from RasterLayerSelectorTable import RasterLayerSelectorTable
from VectorLayerSelectorTable import VectorLayerSelectorTable
from ConfusionMatrixViewer import ConfusionMatrixViewer

from QGisLayers import QGisLayers
from QGisLayers import QGisLayerType

from OSIdentifier import OSIdentifier

import tempfile
import os
import subprocess
import shutil
import time
import datetime

import logging
# create logger
logger = logging.getLogger( 'SupervisedClassificationDialog' )
logger.setLevel(logging.INFO)

def ensure_clean_dir(d):
    #d = os.path.dirname(f)
    if os.path.exists(d):
      shutil.rmtree(d)  
    os.makedirs(d)

def saferemovefile(filename):
    if os.path.exists(filename):
        os.remove(filename)

def transform_spaces(filename):
    from copy import deepcopy
    ret = deepcopy(filename)
    return ret.replace(' ', '_')
	
def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_working_dir():
    dir = os.path.join( os.getenv("HOME"), "ClassificationSupervisee", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    ensure_dir_exists(dir)
    return dir

'''
class StatusChanger():
    def __init__(self, classifdialog):
        self.classifdialog = classifdialog
        self.classifdialog.setClassifyingStatus()
        
        
    def __del__(self):
        self.classifdialog.clearStatus()
'''

'''
class GenericThread(QtCore.QThread):
 def __init__(self, function, *args, **kwargs):
  QtCore.QThread.__init__(self)
  self.function = function
  self.args = args
  self.kwargs = kwargs

 def __del__(self):
  self.wait()

 def run(self):
  self.function(*self.args,**self.kwargs)
  return
'''

class SupervisedClassificationDialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        QtGui.QApplication.restoreOverrideCursor()
        
        self.output_dir = get_working_dir()
        
        self.app_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "win32", "bin")
        logger.debug( "self.app_dir" + str(self.app_dir) )
        
        #self.setupUi()
        QGisLayers.setInterface(iface)
        

        
#         if not OSIdentifier.isWindows():
#             QtGui.QMessageBox.critical( self, \
#                                         u"Erreur", \
#                                         u"Système d'exploitation non supporté" )
#             return


    def setupUi(self):
        self.setWindowTitle(u"Classification Supervisée")
        
        self.mainlayout = QtGui.QVBoxLayout()
        
        #rasterlayers = QGisLayers.getRasterLayers()
        rasterlayers = self.layers
        self.rasterlayerselector = RasterLayerSelectorTable(rasterlayers, self.output_dir, self.main_layer, self.main_layer_bands)
        
        vectorlayers = QGisLayers.getVectorLayers(QGisLayerType.POLYGON)
        self.vectorlayerselector = VectorLayerSelectorTable(vectorlayers)

        self.layerlayout = QtGui.QHBoxLayout()
        self.layerlayout.addWidget(self.rasterlayerselector)
        self.layerlayout.addWidget(self.vectorlayerselector)
        
        self.outputlayout = QtGui.QHBoxLayout()
        
        self.outputdirwidget = QtGui.QLineEdit()
        self.outputdirselectorbutton = QtGui.QPushButton("...")
        #self.setOutputDir( tempfile.mkdtemp(prefix='ClassificationSupervisee_', dir=None) )
        self.setOutputDir( self.output_dir )

        self.outputlayout.addWidget( QtGui.QLabel(u"Répertoire de sortie") )
        self.outputlayout.addWidget( self.outputdirwidget )
        self.outputlayout.addWidget( self.outputdirselectorbutton )
        
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        
        self.classifButton = QtGui.QPushButton("Classification")
        self.cancelButton = QtGui.QPushButton("Annuler")
        
        self.bottomLayout = QtGui.QHBoxLayout()
        self.statusLabel = QtGui.QLabel()
        self.buttonBox.addButton(self.classifButton, QtGui.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(self.cancelButton, QtGui.QDialogButtonBox.RejectRole)
        self.bottomLayout.addWidget(self.statusLabel)
        self.bottomLayout.addStretch()
        self.bottomLayout.addWidget(self.buttonBox)
        
        self.mainlayout.addLayout(self.layerlayout)
        self.mainlayout.addLayout(self.outputlayout)
        self.mainlayout.addLayout(self.bottomLayout)
        self.setLayout(self.mainlayout)
        
        QtCore.QObject.connect(self.classifButton, QtCore.SIGNAL("clicked()"), self.setClassifyingStatus)
        QtCore.QObject.connect(self.classifButton, QtCore.SIGNAL("clicked()"), self.classify)
        
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.cancelPressed)
        
        QtCore.QObject.connect(self.outputdirselectorbutton, QtCore.SIGNAL("clicked()"), self.selectOutputDir)

    def set_layers(self, layers, main_layer=None, main_layer_bands = None):
        self.main_layer = main_layer
        self.main_layer_bands = main_layer_bands
        self.layers = [self.main_layer] + layers
        
        
    def update_layers(self, layers):
        print "update layers"
        self.layers = layers
        for layer in self.layers:
            print layer.name()
        vectorlayers = QGisLayers.getVectorLayers(QGisLayerType.POLYGON)
        self.vectorlayerselector.set_layers(vectorlayers)
        rasterlayers = layers
        self.rasterlayerselector.set_layers(rasterlayers)


    def cancelPressed(self):
        self.close()

    def setOutputDir(self, dirname):
        self.outputdirwidget.setText(dirname)
        
    def getOutputDir(self):
        return str(self.output_dir) #outputdirwidget.text())
        
    def selectOutputDir(self):
        filedialog = QtGui.QFileDialog()
        filedialog.setConfirmOverwrite(True);
        filedialog.setFileMode(QtGui.QFileDialog.Directory);
        filedialog.setNameFilter(u"Répertoire");
        if filedialog.exec_():
            self.setOutputDir(filedialog.selectedFiles()[0])

    def setClassifyingStatus(self):
        self.statusLabel.setText(u"<font color=\"Red\">Classification en cours...</font>")
        QtGui.QApplication.processEvents()
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
    def clearStatus(self):
        self.statusLabel.setText("")
    
    def classify(self):
        logger.debug( "classify" )
        simulation = False
        
        # Get rasters
        selectedrasterlayers = self.rasterlayerselector.getSelectedOptions()
        logger.debug( "selectedrasterlayers" + str(selectedrasterlayers) )
        if len(selectedrasterlayers) < 1:
            QtGui.QMessageBox.critical( self, \
                                        u"Erreur", \
                                        u"Aucune couche raster sélectionnée" )
            return

        # Get vectors
        selectedvectorlayers = self.vectorlayerselector.getSelectedOptions()
        if len(selectedvectorlayers) < 2:
            QtGui.QMessageBox.critical( self, \
                                        u"Erreur", \
                                        u"Au minimum deux couches vecteur doivent être sélectionnées" )
            return

        try:
            errorDuringClassif = False
            outputdir = self.getOutputDir()
            
            # Build list of input raster files
            rasterlist = ""
            for r in selectedrasterlayers:
                rasterlist += '"%s" ' % (r.source())
            logger.debug( "rasterlist" + str( rasterlist ) )

            #firstraster = '"%s" ' % (unicode(selectedrasterlayers[0].source()))
            logger.debug( "selectedrasterlayers[0]" + str(selectedrasterlayers[0]) )
            firstraster = '"%s" ' % (selectedrasterlayers[0].source())

            # Build list of input vector files
            vectorlist = ""
            labeldescriptor = {}
            label = 0
            for i in range(len(selectedvectorlayers)):
                v = selectedvectorlayers[i]
                inputshpfilepath = v[0].source()
                classcolor = v[1]
                classlabel = v[2]
                
                labeldescriptor[label] = (classcolor, classlabel)
                logger.debug( "labeldescriptor" + str(labeldescriptor) )
                label += 1
                
                # Reprocess input shp file to crop it to firstraster extent
                vectordir = os.path.join(outputdir, 'class%s' % (str(i)))
                ensure_clean_dir(vectordir)
                #preprocessedshpfile = os.path.join(vectordir, transform_spaces(os.path.basename(unicode(inputshpfilepath))))
                preprocessedshpfile = os.path.join(vectordir, "preprocessed.shp")
                
                cropcommand = ('%s/cropvectortoimage.bat '
                             '"%s" '
                             '"%s" '
                             '"%s" '
                             '"%s" '
                             '"%s" '
                             % ( self.app_dir,
                                 inputshpfilepath,
                                 selectedrasterlayers[0].source(),
                                 os.path.join(vectordir,"imageenveloppe.shp"),
                                 os.path.join(vectordir,"tmp_reprojected.shp"),
                                 preprocessedshpfile) )

                try:
                  if (simulation):
                      time.sleep(3)
                  else:
                      proc = subprocess.Popen(cropcommand.encode('mbcs'),
                                              shell=True,
                                              stdout=subprocess.PIPE,
                                              stdin=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              universal_newlines=False)
                      
                      loglines = []
                      for line in iter(proc.stdout.readline, ""):
                          loglines.append(line)
                          
                      proc.wait()
                      if proc.returncode != 0:
                          raise OSError

                except OSError:
                  errorDuringClassif = True
                  
                  mbox = QtGui.QMessageBox()
                  mbox.setWindowTitle(u"Erreur")
                  mbox.setText(u"Une erreur a été rencontrée lors de la préparation des données vecteurs")
                  
                  # has no effect...
                  #mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                  #mbox.setSizeGripEnabled(True)
                  
                  detailedtext = (u"Code de retour : %s%s"
                                  "Commande : %s%s"
                                  "Sortie standard :%s%s"
                                  % ( proc.returncode, 2*os.linesep,
                                      cropcommand, 2*os.linesep,
                                      os.linesep, u''.join([u'%s%s' % (unicode(c, 'mbcs'), os.linesep) for c in loglines]) ) )

                  mbox.setDetailedText(detailedtext)
                  mbox.setIcon(QtGui.QMessageBox.Critical)
                  mbox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
                  ret = mbox.exec_()
                  raise OSError
                  
                vectorlist += '"%s" ' % (preprocessedshpfile)

            # Build classifcommand   
            outputlog = os.path.join(outputdir, 'output.log')
            outputclassification = os.path.join(outputdir, 'classification.tif')
            outputresults = os.path.join(outputdir, 'classification.resultats.txt')
            
            launcher = "%s/classification.bat" % self.app_dir
            classifcommand = (  '%s '
                                '-io.il %s '
                                '-io.vd %s '
                                '-io.out "%s" '
                                '-io.results "%s"'
                                %  (launcher,
                                    rasterlist,
                                    vectorlist, 
                                    outputclassification,
                                    outputresults) )

            # Execute commandline
            try:
                if (simulation):
                    time.sleep(3)
                else:
                    proc = subprocess.Popen(classifcommand.encode('mbcs'),
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stdin=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            universal_newlines=False)
                    
                    loglines = []
                    with open(outputlog, "w") as logfile:
                      for line in iter(proc.stdout.readline, ""):
                          loglines.append(line)
                          logfile.writelines(line)
                          logfile.flush()
                          os.fsync(logfile.fileno())

                    proc.wait()
                    if proc.returncode != 0:
                        raise OSError

            except OSError:
                errorDuringClassif = True
                
                mbox = QtGui.QMessageBox()
                mbox.setWindowTitle(u"Erreur")
                mbox.setText(u"Une erreur a été rencontrée lors de la classification")
                
                # has no effect...
                #mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                #mbox.setSizeGripEnabled(True)
                
                detailedtext = (u"Code de retour : %s%s"
                                "Commande : %s%s"
                                "Sortie standard :%s%s"
                                % ( proc.returncode, 2*os.linesep,
                                    classifcommand, 2*os.linesep,
                                    os.linesep, u''.join([u'%s%s' % (unicode(c, 'mbcs'), os.linesep) for c in loglines]) ) )

                mbox.setDetailedText(detailedtext)
                mbox.setIcon(QtGui.QMessageBox.Critical)
                mbox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
                ret = mbox.exec_()
                
                saferemovefile(outputlog)
                saferemovefile(outputclassification)
                saferemovefile(outputresults)

            if (not simulation and not errorDuringClassif):
                QGisLayers.loadLabelImage(outputclassification, labeldescriptor)

                notificationDialog = ConfusionMatrixViewer(selectedvectorlayers, outputresults)
				
                self.clearStatus()
                QtGui.QApplication.restoreOverrideCursor()

                notificationDialog.setModal(True)
                notificationDialog.show()
                
                pixmap = QtGui.QPixmap(notificationDialog.size())
                notificationDialog.render(pixmap)
                pixmap.save(os.path.join(outputdir, 'resultats.png'))
                
                notificationDialog.exec_()
                
#        except:
#            raise

        finally:
            self.clearStatus()
            QtGui.QApplication.restoreOverrideCursor()
            return # this discards exception
