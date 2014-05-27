.. qgiseducation documentation master file, created by
   sphinx-quickstart on Sun Feb 12 17:11:03 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================================
Welcome to qgiseducation's documentation!
============================================

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Module DockableMirrorMap
========================

+ 3 modules
+ permet l'affichage multivue

dockableMirrorMapPlugin
-----------------------
Ce module est le mondule principal qui initialise le plugin.
Il contient :

* une liste des vues
* les actions permettant la sauvegarde des vues lors de la sauvegarde du projet QGIS
* les actions permettant de restaurer les vues lors de l'ouverture d'un projet QGIS
* ajoute une vue en réponse au clic du bouton du plugin


dockableMirrorMap
-----------------
Ce module gère un widget mirror dans QGIS.
Ce module permet de :

* creer le widget MirrorMap qui va permettre l'affichage de l'image
* donner un titre à la vue
* positionner la vue dans l'interface de qgis

L'attribut ``title`` a été ajouté pour permettre de mettre un nom personnalisé à la vue créée.
il est utilisé dans ``setNumber()``.

mirrorMap
---------
Cette classe gère toute la vue.

* Pour chaque nouvelle vue, on y associe un nouveau QgsMapCanvas. 
* Le canvas est mis à blanc ( noir par défaut )
* Les boutons "add layer", "remove layer", la checkbox de rendu, ainsi que l'option de mise à l'échelle sont ajoutés à la vue

Par simplification seul le nom de la vue et le canvas ont été laissés de l'interface d'une vue.

addLayer
~~~~~~~~
 ::
	def addLayer(self, layerId=None):
		# dans la plupart des cas, le layerID est None
		if layerId == None:
			# on prend la layer current
			layer = self.iface.activeLayer()
		else:
			# sinon, on récupère la layer layerID
			layer = QgsMapLayerRegistry.instance().mapLayer( layerId )
		
		if layer == None:
			return

		prevFlag = self.canvas.renderFlag()
		#stop rendering
		self.canvas.setRenderFlag( False )
		
		# add the layer to the map canvas layer set
		self.canvasLayers = []
		# id to canvas layer dictionnary
		id2cl_dict = {}
		# for each layer
		for l in self.iface.legendInterface().layers():
			# lid est l'id de la layer l 
			lid = self._layerId(l)
			#si la layer a été chargée précédemment dans la vue
			if self.layerId2canvasLayer.has_key( lid ):	# previously added
				cl = self.layerId2canvasLayer[ lid ]
			elif l == layer:	# selected layer
				cl = QgsMapCanvasLayer( layer )
			else:
				continue
			print type(cl) #qgis.gui.QgsMapCanvasLayer

			# maj dictionnaire id/canvas layer
			id2cl_dict[ lid ] = cl
			#ajout de la canvas layer
			self.canvasLayers.append( cl )

		self.layerId2canvasLayer = id2cl_dict
		self.canvas.setLayerSet( self.canvasLayers )

		self.refreshLayerButtons()
		self.onExtentsChanged()
		#remet le rendering comme avant l'opération
		self.canvas.setRenderFlag( prevFlag )


Developpement
-------------
Le zoom lié n'a pas été mis en place parce que le signal extentChanged génère une boucle.


Développement du module principal
=================================
Le module principal est comme suit :

:``qgiseducation``: Fichier principal du plugin. Il initialise le widget et crée les menus.  
 
:``qgiseducationwidget``: Ce fichier s'occupe de toute l'interface widget.  

:``process_manager``: Ce fichier contient la classe qui va gérer le plugin. Cette classe contient la liste des process, la layer courante et le répertoire de travail.

:``terre_image_task``: Ce fichier contient les classes de traitement.
	Il y a une classe mère de tache et deux classes filles, ``processing`` et ``display``.
  	La première lance les traitements d'image tels que le NDVI et le KMEANS, la seconde va afficher les bandes spectrales et d'autres informations.



Value Tool
==========

Il est composé de deux fichiers principaux

:valuetool: fichier d'initialisation du plugin supprimé dans notre version
:valuewidget: fichier qui contient tout le code interessant pour l'affichage des valeurs



valuewidget
-----------

Ce fichier parcours les layers visibles du canvas.
Il retient toutes les raster layers.

Il en parcours ensuite les bandes et en prend les valeurs.
Ensuite, il fait appel à la fonction de display qui va afficher soit en tableau, soit en courbe.


customization
-------------
Les attributs pixel/ligne ont été ajouté pour afficher la coordonnée dans l'image sous le curseur de la souris.

Les layers à afficher vont être fournies au plugin.
Si aucune layer n'est fournie, alors, on cherche les rasters.

Lors de la fermeture d'un projet, on enlève les widgets en rapport avec le plugin. Lorsqu'on recharge une image, on obtient l'erreur suivante :#

Traceback (most recent call last):
  File "/home/amondot/.qgis2/python/plugins/QGISEducation/valuetool/valuewidget.py", line 789, in invalidatePlot
    self.printValue( None )
  File "/home/amondot/.qgis2/python/plugins/QGISEducation/valuetool/valuewidget.py", line 375, in printValue
    layername=unicode(layer.name())
RuntimeError: underlying C/C++ object has been deleted

Dans le bout de code que j'ai rajouté je parcours les layers de travail que je passe en argument. Sauf qu'elles ont été deletées. 






Angle Spectral
==============
Cette fonctionalité est plus ou moins problématique.
En effet, les signaux ne fonctionnent pas systématiquement, je ne comprends pas pourquoi.

J'ai ajouté la méthode de display dans la classez de spectral angle.
J'ai essayé d'emettre un signal quand le fichier avait été créé. Impossible de le récuperer dans la classe de Processings.

Le code de display est par contre dupliqué. La classe spectral angle se voit ajouter un attribut ``mirrormap_tool`` pour le display des vues.
Reste à vérifier que ce mirror tool pointe vers le même mirror tool que les autres pour qu'on puisse gérer la vue du spectral angle depuis le plugin.




Sauvegarde du projet courant
============================


état terre image
----------------
La sauvegarde de projet comprend :
* L'image de travail
* 


Elle de comprend pas :
* Les courbes mémorisées dans "profil spectral"
* La réouvertures des vues des traitements


