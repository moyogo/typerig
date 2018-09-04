# MODULE: Fontlab 6 Proxy | Typerig
# VER 	: 0.41
# ----------------------------------------
# (C) Vassil Kateliev, 2017 (http://www.kateliev.com)
# (C) Karandash Type Foundry (http://www.karandash.eu)
#-----------------------------------------
# www.typerig.com

# No warranties. By using this you agree
# that you use it at your own risk!

# - Dependencies --------------------------
import fontlab as fl6
import fontgate as fgt
import PythonQt as pqt
import FL as legacy

# - Classes -------------------------------
class pWorkspace(object):
	'''Proxy to flWorkspace object

	Constructor:
		pWorkspace()

	Attributes:
		.fl (flWorkspace): Current workspace
		.main (QWidget): Main QWidget's window
	'''

	def __init__(self):
		self.fl = fl6.flWorkspace.instance()
		self.main = self.fl.mainWindow
		self.name = self.fl.name

	def getCanvas(self, atCursor=False):
		return self.fl.getActiveCanvas() if not atCursor else self.fl.getCanvasUnderCursor()

	def getCanvasList(self):
		return self.fl.canvases()

	def getTextBlockList(self, atCursor=False):
		return self.getCanvas(atCursor).textBlocks()

	def getTextBlockGlyphs(self, tbi=0):
		return [info.glyph for info in self.getTextBlockList()[tbi].getAllGlyphs()]

class pNode(object):
	'''Proxy to flNode object

	Constructor:
		pNode(flNode)

	Attributes:
		.fl (flNode): Original flNode 
		.parent (flContour): parent contour
		.contour (flContour): parent contour
	'''
	def __init__(self, node):
		self.fl = node
		self.parent = self.contour = self.fl.contour
		self.name = self.fl.name
		self.index = self.fl.index
		self.id = self.fl.id
		self.isOn = self.fl.isOn()
		self.type = self.fl.type
		self.x, self.y = float(self.fl.x), float(self.fl.y)
		self.angle = float(self.fl.angle)

	def __repr__(self):
		return '<%s (%s, %s) index=%s time=%s on=%s>' % (self.__class__.__name__, self.x, self.y, self.index, self.getTime(), self.isOn)
	
	# - Basics -----------------------------------------------
	def getTime(self):
		return self.contour.getT(self.fl)

	def getNext(self, naked=True):
		return self.fl.nextNode() if naked else self.__class__(self.fl.nextNode())

	def getNextOn(self, naked=True):
		nextNode = self.fl.nextNode()
		nextNodeOn = nextNode if nextNode.isOn() else nextNode.nextNode().getOn()
		return nextNodeOn if naked else self.__class__(nextNodeOn)

	def getPrevOn(self, naked=True):
		prevNode = self.fl.prevNode()
		prevNodeOn = prevNode if prevNode.isOn() else prevNode.prevNode().getOn()
		return prevNodeOn if naked else self.__class__(prevNodeOn)

	def getPrev(self, naked=True):
		return self.fl.prevNode() if naked else self.__class__(self.fl.prevNode())

	def getOn(self, naked=True):
		return self.fl.getOn() if naked else self.__class__(self.fl.getOn())

	def getSegment(self, relativeTime=0):
		return self.contour.segment(self.getTime() + relativeTime)

	def getSegmentNodes(self, relativeTime=0):
		if len(self.getSegment(relativeTime)) == 4:
			currNode = self.fl if self.fl.isOn() else self.fl.getOn()
			
			if currNode != self.fl:
				tempNode = self.__class__(currNode)

				if tempNode.getTime() != self.getTime():
					currNode = tempNode.getPrevOn()

			currNode_bcpOut = currNode.nextNode()
			nextNode_bcpIn = currNode_bcpOut.nextNode()
			nextNode = nextNode_bcpIn.getOn()
		
			return (currNode, currNode_bcpOut, nextNode_bcpIn, nextNode)
		
		elif len(self.getSegment(relativeTime)) == 2:
			return (self.fl, self.fl.nextNode())

	def getContour(self):
		return self.fl.contour

	def insertAfter(self, time):
		self.contour.insertNodeTo(self.getTime() + time)

	def remove(self):
		self.contour.removeOne(self.fl)

	def update(self):
		self.fl.update()
		self.x, self.y = float(self.fl.x), float(self.fl.y)

	# - Transformation -----------------------------------------------
	def reloc(self, newX, newY):
		'''Relocate the node to new coordinates'''
		self.fl.x, self.fl.y = newX, newY
		self.x, self.y = newX, newY	
		#self.update()
	
	def shift(self, deltaX, deltaY):
		'''Shift the node by given amout'''
		self.fl.x += deltaX
		self.fl.y += deltaY
		self.x, self.y = self.fl.x, self.fl.y 
		#self.update()

	def smartReloc(self, newX, newY):
		'''Relocate the node and adjacent BCPs to new coordinates'''
		self.smartShift(newX - self.fl.x, newY - self.fl.y)

	def smartShift(self, deltaX, deltaY):
		'''Shift the node and adjacent BCPs by given amout'''
		if self.isOn:	
			nextNode = self.getNext(False)
			prevNode = self.getPrev(False)

			for node, mode in [(prevNode, not prevNode.isOn), (self, self.isOn), (nextNode, not nextNode.isOn)]:
				if mode: node.shift(deltaX, deltaY)
		else:
			self.shift(deltaX, deltaY)

class pShape(object):
	'''Proxy to flShape, flShapeData and flShapeInfo objects

	Constructor:
		pShape(flShape)

	Attributes:
		.fl (flNode): Original flNode 
		.parent (flContour): parent contour
		.contour (flContour): parent contour
	'''
	def __init__(self, shape, layer=None, glyph=None):
		self.fl = shape
		self.shapeData = self.data()
		self.name = self.shapeData.name
		self.currentName = self.fl.name
		self.refs = self.shapeData.referenceCount

		self.parent = glyph
		self.layer = layer

	# - Basics -----------------------------------------------
	def data(self):
		''' Return flShapeData Object'''
		return self.fl.shapeData

	def info(self):
		''' Return flShapeInfo Object'''
		pass

	def tag(self, tagString):
		self.data().tag(tagString)

	def isChanged(self):
		return self.data().hasChanges

	# - Position, composition ---------------------------------
	def decompose(self):
		self.fl.decomposite()

	def goUp(self):
		return self.data().goUp()

	def goDown(self):
		return self.data().goDown()

	def goFrontOf(self, flShape):
		return self.data().sendToFront(flShape)

	def goBackOf(self, flShape):
		return self.data().sendToBack(flShape)

	def goLayerBack(self):
		if self.layer is not None:
			return self.goBackOf(self.layer.shapes[0])
		return False

	def goLayerFront(self):
		if self.layer is not None:
			return self.goFrontOf(self.layer.shapes[-1])
		return False

	# - Contours, Segmets, Nodes ------------------------------
	def segments(self):
		return self.data().segments

	def contours(self):
		return self.data().contours

	def nodes(self):
		return [node for contour in self.contours() for node in contour.nodes()]

	# - Transformation ----------------------------------------
	'''
	# -- NOTE: this should go to new eShape object as the proxy is not the palce for such extended functionality
	def applyTransformation(self, transformMatrix, flEngine=False):
		if not flEngine:
			from typerig.brain import transform
			tMat = transform().transform(transformMatrix)

			for node in self.nodes():
				tNode = tMat.applyTransformation(node.x, node.y)
				node.setXY(*tNode)
	'''
	def __repr__(self):
		return '<%s name=%s references=%s contours=%s>' % (self.__class__.__name__, self.name, self.refs, len(self.contours()))


class pGlyph(object):
	'''Proxy to flGlyph and fgGlyph combined into single entity.

	Constructor:
		pGlyph() : default represents the current glyph and current font
		pGlyph(flGlyph)
		pGlyph(fgFont, fgGlyph)
	
	Methods:

	Attributes:
		.parent (fgFont)
		.fg (fgGlyph)
		.fl (flGlyph)
		...
	'''

	def __init__(self, *argv):
		
		if len(argv) == 0:
			self.parent = fl6.CurrentFont()
			self.fg = fl6.CurrentGlyph()
			self.fl = fl6.flGlyph(fl6.CurrentGlyph(), fl6.CurrentFont())
		
		elif len(argv) == 1 and isinstance(argv[0], fl6.flGlyph):
			'''
			# - Kind of not working as the reslting glyph is detached (-1 orphan) from the fgFont
			self.fl = argv[0]
			self.fg = self.fl.fgGlyph
			self.parent = self.fl.fgPackage
			'''

			# - Alternate way - will use that way
			font, glyph = argv[0].fgPackage, argv[0].fgPackage[argv[0].name]
			self.parent = font
			self.fg = glyph
			self.fl = fl6.flGlyph(glyph, font)

		elif len(argv) == 2 and isinstance(argv[0], fgt.fgFont) and isinstance(argv[1], fgt.fgGlyph):
			font, glyph = argv
			self.parent = font
			self.fg = glyph
			self.fl = fl6.flGlyph(glyph, font)
			
		self.name = self.fg.name
		self.index = self.fg.index
		self.id = self.fl.id
		self.mark = self.fl.mark
		self.tags = self.fl.tags
		self.unicode = self.fg.unicode
		self.package = fl6.flPackage(self.fl.package)

	def __repr__(self):
		return '<%s name=%s index=%s unicode=%s>' % (self.__class__.__name__, self.name, self.index, self.unicode)

	# - Basics -----------------------------------------------
	def activeLayer(self): return self.fl.activeLayer

	def fg_activeLayer(self): return self.fg.layer

	def mask(self): return self.fl.activeLayer.getMaskLayer(True)

	def activeGuides(self): return self.fl.activeLayer.guidelines

	def object(self): return fl6.flObject(self.fl.id)

	def italicAngle(self): return self.package.italicAngle_value

	def nodes(self, layer=None, extend=None):
		'''Return all nodes at given layer.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer.
			extend (class): A class construct with extended functionality to be applied on every node.
		Returns:
			list[flNodes]
		'''
		#return sum([contour.nodes() for contour in self.layer(layer).getContours()], [])
		if extend is None:
			return [node for contour in self.layer(layer).getContours() for node in contour.nodes()]
		else:
			return [extend(node) for contour in self.layer(layer).getContours() for node in contour.nodes()]

	def fg_nodes(self, layer=None):
		'''Return all FontGate nodes at given layer.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[fgNodes]
		'''
		return sum([contour.nodes.asList() for contour in self.fg_contours(layer)], [])

	def contours(self, layer=None):
		'''Return all contours at given layer.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[flContours]
		'''
		return [contour for contour in self.layer(layer).getContours()]

	def fg_contours(self, layer=None):
		'''Return all FontGate contours at given layer.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[fgContours]
		'''
		return sum([shape.contours.asList() for shape in self.fg_shapes(layer)],[])

	def layers(self):
		'''Return all layers'''
		return self.fl.layers

	def fg_layers(self, asDict=False):
		'''Return all FotnGate layers'''
		return self.fg.layers if not asDict else {layer.name:layer for layer in self.fg.layers}

	def layer(self, layer=None):
		'''Returns layer no matter the reference.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			flLayer
		'''
		if layer is None:
			return self.fl.activeLayer
		else:
			if isinstance(layer, int):
				return self.fl.layers[layer]

			elif isinstance(layer, basestring):
				return self.fl.getLayerByName(layer)

	def fg_layer(self, layer=None):
		'''Returns FontGate layer no matter the reference.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			fgLayer
		'''
		if layer is None:
			return self.fg.activeLayer
		else:
			if isinstance(layer, int):
				return self.fg.layers[layer]

			elif isinstance(layer, basestring):
				try:
					return self.fg_layers(True)[layer]
				except KeyError:
					return None

	def hasLayer(self, layerName):
		return True if self.fl.findLayer(layerName) is not None else False

	def fg_hasLayer(self, layerName):
		return self.fg.fgData().findLayer(layer)

	def shapes(self, layer=None):
		'''Return all shapes at given layer.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[flShapes]
		'''
		if layer is None:
			return self.fl.activeLayer.shapes
		else:
			if isinstance(layer, int):
				return self.fl.layers[layer].shapes

			elif isinstance(layer, basestring):
				return self.fl.getLayerByName(layer).shapes

	def shapes_data(self, layer=None):
		'''Return all flShapeData objects at given layer.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[flShapeData]
		'''
		return [shape.shapeData for shape in self.shapes(layer)]

	def fg_shapes(self, layer=None):
		'''Return all FontGate shapes at given layer.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[fgShapes]
		'''
		activeLayer = self.fg_layer(layer)
		return [activeLayer[sid] for sid in range(activeLayer.countShapes())]

	# - Composite glyph --------------------------------------------
	def listGlyphComponents(self, layer=None, fullData=False):
		'''Return all glyph components in glyph'''
		return [item if fullData else item[0] for item in [self.package.isComponent(shape.shapeData) for shape in self.shapes(layer)] if item[0] is not None]

	def listUnboundShapes(self, layer=None):
		'''Return all glyph shapes that are not glyph references or those belonging to the original (master) glyph'''
		return [shape for shape in self.shapes(layer) if self.package.isComponent(shape.shapeData)[0] is None or self.package.isComponent(shape.shapeData)[0] == self.fl]		

	def hasGlyphComponents(self, layer=None):
		'''Return all glyph components in besides glyph.'''
		return [glyph for glyph in self.listGlyphComponents(layer) if glyph != self.fl]

	# - Layers -----------------------------------------------------
	def masters(self):
		'''Returns all master layers.'''
		return [layer for layer in self.layers() if layer.isMasterLayer]

	def masks(self):
		'''Returns all mask layers.'''
		return [layer for layer in self.layers() if layer.isMaskLayer]

	def services(self):
		'''Returns all service layers.'''
		return [layer for layer in self.layers() if layer.isService]

	def addLayer(self, layer, toBack=False):
		'''Adds a layer to glyph.
		Args:
			layer (flLayer or fgLayer)
			toBack (bool): Send layer to back
		Returns:
			None
		'''
		if isinstance(layer, fl6.flLayer):
			self.fl.addLayer(layer, toBack)

		elif isinstance(layer, fgt.fgLayer):
			self.fg.layers.append(layer)

	def removeLayer(self, layer):
		'''Removes a layer from glyph.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		self.fl.removeLayer(self.layer(layer))

	def duplicateLayer(self, layer=None, newLayerName='New Layer', toBack=False):
		'''Duplicates a layer with new name and adds it to glyph's layers.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
			toBack(bool): send to back
		Returns:
			flLayer
		Note:
			This is redundant and false duplication until better solution is found.
			Currently Guidelines are not duplicated due to crash.
		'''
		srcLayer = self.layer(layer)
		dstLayer = fl6.flLayer()

		dstLayer.name = newLayerName
		dstLayer.advanceHeight = srcLayer.advanceHeight
		dstLayer.advanceWidth = srcLayer.advanceWidth
		#dstLayer.flags = srcLayer.flags
		#dstLayer.data = srcLayer.data
		dstLayer.wireframeColor = srcLayer.wireframeColor
		dstLayer.mark = srcLayer.mark

		dstLayer.metricsLeft = srcLayer.metricsLeft
		dstLayer.metricsRight = srcLayer.metricsRight
		dstLayer.metricsWidth = srcLayer.metricsWidth

		dstLayer.assignStyle(srcLayer)
		dstLayer.addShapes([shape.cloneTopLevel() for shape in srcLayer.shapes])
		dstLayer.appendGuidelines(srcLayer.guidelines)

		for anchor in srcLayer.anchors:
			dstLayer.addAnchor(anchor)

		for comp in srcLayer.components:
			dstLayer.addComponent(comp)

		dstLayer.update()
		self.addLayer(dstLayer, toBack)
		return dstLayer

	def update(self, fl=True, fg=False):
		'''Updates the glyph and sends notification to the editor.
		Args:
			fl (bool): Update the flGlyph
			fg (bool): Update the fgGlyph
		'''
		# !TODO: Undo?
		if fl:self.fl.update()
		if fg:self.fg.update()

		fl6.flItems.notifyGlyphUpdated(self.package.id, self.id)

	def updateObject(self, flObject, undoMessage='TypeRig', verbose=True):
		'''Updates a flObject sends notification to the editor as well as undo/history item.
		Args:
			flObject (flGlyph, flLayer, flShape, flNode, flContour): Object to be update and set undo state
			undoMessage (string): Message to be added in undo/history list.'''
		
		# - General way ---- pre 6774 worked fine!
		fl6.flItems.notifyChangesApplied(undoMessage, flObject, True)
		if verbose: print 'DONE:\t %s' %undoMessage
		
		# - New from 6774 on
		for contour in self.contours():
			contour.changed()
		
		fl6.flItems.notifyPackageContentUpdated(self.fl.fgPackage.id)
		#fl6.Update()
		
		'''# - Type specific way 
		# -- Covers flGlyph, flLayer, flShape
		if isinstance(flObject, fl6.flGlyph) or isinstance(flObject, fl6.flLayer) or isinstance(flObject, fl6.flShape):
			fl6.flItems.notifyChangesApplied(undoMessage, flObject, True)
		
		# -- Covers flNode, flContour, (flShape.shapeData)
		elif isinstance(flObject, fl6.flContour) or isinstance(flObject, fl6.flNode):
			fl6.flItems.notifyChangesApplied(undoMessage, flObject.shapeData)
		'''

	# - Glyph Selection -----------------------------------------------
	def selectedNodeIndices(self, filterOn=False):
		'''Return all indices of nodes selected at current layer.
		Args:
			filterOn (bool): Return only on-curve nodes
		Returns:
			list[int]
		'''
		allNodes = self.nodes()

		if not filterOn:
			return [allNodes.index(node) for node in self.nodes() if node.selected]
		else:
			return [allNodes.index(node) for node in self.nodes() if node.selected and node.isOn()]
	
	def selected(self, filterOn=False):
		'''Return all selected nodes indexes at current layer.
		Args:
			filterOn (bool): Return only on-curve nodes
		Returns:
			list[int]
		'''
		return self.selectedNodeIndices(filterOn)

	def selectedNodes(self, layer=None, filterOn=False, extend=None):
		'''Return all selected nodes at given layer.
		Args:
			filterOn (bool): Return only on-curve nodes
			extend (class): A class construct with extended functionality to be applied on every node.
		Returns:
			list[flNode]
		'''
		return [self.nodes(layer, extend)[nid] for nid in self.selectedNodeIndices(filterOn)]
	
	def selectedAtContours(self, index=True, layer=None, filterOn=False):	
		'''Return all selected nodes and the contours they rest upon at current layer.
		Args:
			index (bool): If True returns only indexes, False returns flContour, flNode
			filterOn (bool): Return only on-curve nodes
		Returns:
			list[tuple(int, int)]: [(contourID, nodeID)..()] or 
			list[tuple(flContour, flNode)]
		'''
		allContours = self.contours(layer)
		
		if index:
			return [(allContours.index(node.contour), node.index) for node in self.selectedNodes(layer, filterOn)]
		else:
			return [(node.contour, node) for node in self.selectedNodes(layer, filterOn)]

	def selectedAtShapes(self, index=True, filterOn=False):
		'''Return all selected nodes and the shapes they belong at current layer.
		Args:
			index (bool): If True returns only indexes, False returns flShape, flNode
			filterOn (bool): Return only on-curve nodes
		Returns:
			list[tuple(int, int)]: [(shapeID, nodeID)..()] or
			list[tuple(flShape, flNode)]

		!TODO: Make it working with layers as selectedAtContours(). This is legacy mode so other scripts would work!
		'''
		allContours = self.contours()
		allShapes = self.shapes()

		if index:
			return [(allShapes.index(shape), allContours.index(contour), node.index) for shape in allShapes for contour in shape.contours for node in contour.nodes() if node in self.selectedNodes(filterOn=filterOn)]
		else:
			return [(shape, contour, node) for shape in allShapes for contour in shape.contours for node in contour.nodes() if node in self.selectedNodes(filterOn=filterOn)]

	def selectedCoords(self, layer=None, filterOn=False, applyTransform=False):
		'''Return the coordinates of all selected nodes at the current layer or other.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
			filterOn (bool): Return only on-curve nodes
			applyTransform (bool) : Gets local shape transformation matrix and applies it to the node coordinates
		Returns:
			list[QPointF]
		'''
		pLayer = self.layer(layer)
		
		if not applyTransform:
			nodelist = self.selectedAtContours(filterOn=filterOn)
			return [pLayer.getContours()[item[0]].nodes()[item[1]].position for item in nodelist]

		else:
			nodelist = self.selectedAtShapes(filterOn=filterOn)
			return [pLayer.getShapes(1)[item[0]].transform.map(pLayer.getContours()[item[1]].nodes()[item[2]].position) for item in nodelist]

	def selectedSegments(self, layer=None):
		'''Returns list of currently selected segments
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[CurveEx]
		'''
		return [self.contours(layer)[cID].segment(self.mapNodes2Times(layer)[cID][nID]) for cID, nID in self.selectedAtContours()]

	# - Outline -----------------------------------------------
	def _mapOn(self, layer=None):
		'''Create map of onCurve Nodes for every contour in given layer
		Returns:
			dict: {contour_index : {True_Node_Index : on_Curve__Node_Index}...}
		'''
		contourMap = {}		
		allContours = self.contours(layer)
		
		for contour in allContours:
			nodeMap = {}
			countOn = -1

			for node in contour.nodes():
				countOn += node.isOn() # Hack-ish but working
				nodeMap[node.index] = countOn
				
			contourMap[allContours.index(contour)] = nodeMap

		return contourMap

	def mapNodes2Times(self, layer=None):
		'''Create map of Nodes at contour times for every contour in given layer
		Returns:
			dict{Contour index (int) : dict{Contour Time (int): Node Index (int) }}
		'''
		return self._mapOn(layer)

	def mapTimes2Nodes(self, layer=None):
		'''Create map of Contour times at node indexes for every contour in given layer
		Returns:
			dict{Contour index (int) : dict{Node Index (int) : Contour Time (int) }}
		'''
		n2tMap = self._mapOn(layer)
		t2nMap = {}

		for cID, nodeMap in n2tMap.iteritems():
			tempMap = {}
			
			for nID, time in nodeMap.iteritems():
				tempMap.setdefault(time, []).append(nID)

			t2nMap[cID] = tempMap

		return t2nMap

	def getSegment(self, cID, nID, layer=None):
		'''Returns contour segment of the node specified at given layer
		Args:
			cID (int): Contour index
			nID (int): Node of insertion index
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			CurveEx
		'''
		return self.contours(layer)[cID].segment(self._mapOn(layer)[cID][nID])

	def segments(self, cID, layer=None):
		'''Returns all contour segments at given layer
		Args:
			cID (int): Contour index
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			list[CurveEx]
		'''
		return self.contours(layer)[cID].segments()

	def nodes4segments(self, cID, layer=None):
		'''Returns all contour segments and their corresponding nodes at given layer
		Args:
			cID (int): Contour index
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			dict{time(int):(CurveEx, list[flNode]}
		'''

		segments = self.segments(cID, layer)
		
		#nodes = self.nodes(layer)
		nodes = self.contours(layer)[cID].nodes()
		nodes.append(nodes[0]) # Dirty Close contour

		timeTable = self.mapTimes2Nodes(layer)[cID]
		n4sMap = {}

		for time, nodeIndexes in timeTable.iteritems():
			n4sMap[time] = (segments[time], [nodes[nID] for nID in nodeIndexes] + [nodes[nodeIndexes[-1] + 1]]) # Should be closed otherwise fail			

		return n4sMap

	def insertNodesAt(self, cID, nID, nodeList, layer=None):
		'''Inserts a list of nodes to specified contour, starting at given index all on layer specified.
		Args:
			cID (int): Contour index
			nID (int): Node of insertion index
			nodeList (list): List of flNode objects
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		self.contours(layer)[cID].insert(nID, nodeList)

	def removeNodes(self, cID, nodeList, layer=None):
		'''Removes a list of nodes from contour at layer specified.
		Args:
			cID (int): Contour index
			nodeList (list): List of flNode objects
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		for node in nodeList:
			self.contours(layer)[cID].removeOne(node)
			#self.contours(layer)[cID].updateIndices()

	def insertNodeAt(self, cID, nID_time, layer=None):
		''' Inserts node in contour at specified layer
		Arg:
			cID (int): Contour Index
			nID_time (float): Node index + float time
			layer (int or str): Layer index or name. If None returns ActiveLayer

		!NOTE: FL6 treats contour insertions (as well as nodes) as float times along contour,
		so inserting a node at .5 t between nodes with indexes 3 and 4 will be 3 (index) + 0.5 (time) = 3.5
		'''
		self.contours(layer)[cID].insertNodeTo(nID_time)

	def removeNodeAt(self, cID, nID, layer=None):
		'''Removes a node from contour at layer specified.
		Args:
			cID (int): Contour index
			nID (int): Index of Node to be removed
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		self.contours(layer)[cID].removeAt(nID)

	def translate(self, dx, dy, layer=None):
		'''Translate (shift) outline at given layer.
		Args:
			dx (float), dy (float): delta (shift) X, Y
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		pLayer = self.layer(layer)
		pTransform = pLayer.transform
		pTransform.translate(dx, dy)
		pLayer.applyTransform(pTransform)

	def scale(self, sx, sy, layer=None):
		'''Scale outline at given layer.
		Args:
			sx (float), sy (float): delta (scaling) X, Y
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		pLayer = self.layer(layer)
		pTransform = pLayer.transform
		pTransform.scale(sx, sy)
		pLayer.applyTransform(pTransform)

	def slant(self, deg, layer=None):
		'''Slant outline at given layer.
		Args:
			deg (float): degrees of slant
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		from math import tan, radians
		pLayer = self.layer(layer)
		pTransform = pLayer.transform
		pTransform.shear(tan(radians(deg)), 0)
		pLayer.applyTransform(pTransform)

	def rotate(self, deg, layer=None):
		'''Rotate outline at given layer.
		Args:
			deg (float): degrees of slant
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			None
		'''
		pLayer = self.layer(layer)
		pTransform = pLayer.transform
		pTransform.rotate(deg)
		pLayer.applyTransform(pTransform)

	# - Interpolation  -----------------------------------------------
	def _shape2fg(self, flShape):
		'''Convert flShape to fgShape'''
		tempFgShape = fgt.fgShape()
		flShape.convertToFgShape(tempFgShape)
		return tempFgShape

	def blendShapes(self, shapeA, shapeB, blendTimes, outputFL=True, blendMode=0, engine='fg'):
		'''Blend two shapes at given times (anisotropic support).
		Args:
			shapeA (flShape), shapeB (flShape): Shapes to be interpolated
			blendTimes (int or float or tuple(float, float)): (int) for percent 0%-100% or (float) time for both X,Y or tuple(float,float) times for anisotropic blending
			outputFL (bool): Return blend native format or flShape (default)
			blendMode (int): ?
			engine (str): 'fg' for FontGate (in-build).

		Returns:
			Native (interpolation engine dependent) or flShape (default)
		'''

		if engine.lower() == 'fg': # Use FontGate engine for blending/interpolation
			if isinstance(shapeA, fl6.flShape): shapeA = self._shape2fg(shapeA)
			if isinstance(shapeB, fl6.flShape):	shapeB = self._shape2fg(shapeB)
			
			if isinstance(blendTimes, tuple): blendTimes = pqt.QtCore.QPointF(*blendTimes)
			if isinstance(blendTimes, int): blendTimes = pqt.QtCore.QPointF(float(blendTimes)/100, float(blendTimes)/100)
			if isinstance(blendTimes, float): blendTimes = pqt.QtCore.QPointF(blendTimes, blendTimes)

			tempBlend = fgt.fgShape(shapeA, shapeB, blendTimes.x(), blendTimes.y(), blendMode)
			return fl6.flShape(tempBlend) if outputFL else tempBlend

	# - Metrics -----------------------------------------------
	def getLSB(self, layer=None):
		'''Get the Left Side-bearing at given layer (int or str)'''
		pLayer = self.layer(layer)
		return int(pLayer.boundingBox.x())
	
	def getAdvance(self, layer=None):
		'''Get the Advance Width at given layer (int or str)'''
		pLayer = self.layer(layer)
		return int(pLayer.advanceWidth)

	def getRSB(self, layer=None):
		'''Get the Right Side-bearing at given layer (int or str)'''
		pLayer = self.layer(layer)
		return int(pLayer.advanceWidth - (pLayer.boundingBox.x() + pLayer.boundingBox.width()))

	def setLSB(self, newLSB, layer=None):
		'''Set the Left Side-bearing (int) at given layer (int or str)'''
		pLayer = self.layer(layer)
		pTransform = pLayer.transform
		shiftDx = newLSB - int(pLayer.boundingBox.x())
		pTransform.translate(shiftDx, 0)
		pLayer.applyTransform(pTransform)

	def setRSB(self, newRSB, layer=None):
		'''Set the Right Side-bearing (int) at given layer (int or str)'''
		pLayer = self.layer(layer)
		pRSB = pLayer.advanceWidth - (pLayer.boundingBox.x() + pLayer.boundingBox.width())
		pLayer.advanceWidth += newRSB - pRSB

	def setAdvance(self, newAdvance, layer=None):
		'''Set the Advance Width (int) at given layer (int or str)'''
		pLayer = self.layer(layer)
		pLayer.advanceWidth = newAdvance

	def setLSBeq(self, equationStr, layer=None):
		'''Set LSB metric equation on given layer'''
		self.layer(layer).metricsLeft = equationStr

	def setRSBeq(self, equationStr, layer=None):
		'''Set RSB metric equation on given layer'''
		self.layer(layer).metricsRight = equationStr

	def setADVeq(self, equationStr, layer=None):
		'''Set Advance width metric equation on given layer'''
		self.layer(layer).metricsWidth = equationStr

	def fontMetricsInfo(self, layer=None):
		'''Returns Font(layer) metrics no matter the reference.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			FontMetrics (object)
		'''
		if layer is None:
			return fl6.FontMetrics(self.package, self.fl.activeLayer.name)
		else:
			if isinstance(layer, int):
				return fl6.FontMetrics(self.package, self.fl.layers[layer].name) 

			elif isinstance(layer, basestring):
				return fl6.FontMetrics(self.package, layer)

	# - Anchors and pins -----------------------------------------------
	def anchors(self, layer=None):
		'''Return list of anchors (list[flAnchor]) at given layer (int or str)'''
		return self.layer(layer).anchors

	def addAnchor(self, coordTuple, name, layer=None, isAnchor=True):
		'''	Adds named Anchor at given layer.
		Args:
			coordTuple (tuple(float,float)): Anchor coordinates X, Y
			name (str): Anchor name
			layer (int or str): Layer index or name. If None returns ActiveLayer
			isAnchor (bool): True creates a true flAnchor, False ? (flPinPoint)
		Returns:
			None
		'''
		newAnchor = fl6.flPinPoint(pqt.QtCore.QPointF(*coordTuple))
		newAnchor.name = name
		newAnchor.anchor = isAnchor
		
		self.layer(layer).addAnchor(newAnchor)

	def clearAnchors(self, layer=None):
		'''Remove all anchors at given layer (int or str)'''
		return self.layer(layer).clearAnchors()

	# - Guidelines -----------------------------------------------
	def guidelines(self, layer=None):
		'''Return list of guidelines (list[flGuideline]) at given layer (int or str)'''
		return self.layer(layer).guidelines

	def addGuideline(self, coordTuple, layer=None, angle=0, name='',  color='darkMagenta', style='gsGlyphGuideline'):
		'''Adds named Guideline at given layer
		Args:
			coordTuple (tuple(float,float) or tuple(float,float,float,float)): Guideline coordinates X, Y and given angle or two node reference x1,y1 and x2,y2
			name (str): Anchor name
			angle (float): Incline of the guideline
			layer (int or str): Layer index or name. If None returns ActiveLayer			
		Returns:
			None
		'''
		if len(coordTuple) == 2:
			origin = pqt.QtCore.QPointF(0,0)
			position = pqt.QtCore.QPointF(*coordTuple)

			vector = pqt.QtCore.QLineF(position, origin)
			vector.setAngle(90 - angle)
		else:
			vector = pqt.QtCore.QLineF(*coordTuple)

		newGuideline = fl6.flGuideLine(vector)
		newGuideline.name =  name
		newGuideline.color = pqt.QtGui.QColor(color)
		newGuideline.style = style
			
		self.layer(layer).appendGuidelines([newGuideline])


class pFontMetrics(object):
	'''
	An Abstract Font Metrics getter/setter of a flPackage.

	Constructor:
		pFontMetrics() - default represents the current glyph and current font
		pFontMetrics(flPackage)
	
	'''
	def __init__(self, font):
		self.fl = font
		
	# - Getters
	def getAscender (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.ascender_value

	def getCapsHeight (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.capsHeight_value

	def getDescender (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.descender_value

	def getLineGap (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.lineGap_value

	'''
	def getUpm (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.upm
	'''

	def getXHeight (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.xHeight_value

	def getItalicAngle (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.italicAngle_value

	def getCaretOffset (self, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		return self.fl.caretOffset_value

	'''
	cornerTension_value
	curveTension_value
	inktrapLen_value
	measurement_value
	underlinePosition_value
	underlineThickness_value
	'''

	# - Setters
	def setAscender (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.ascender_value = value

	def setCapsHeight (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.capsHeight_value = value

	def setDescender (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.descender_value = value

	def setLineGap (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.lineGap_value = value

	'''
	def setUpm (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.upm = value
	'''

	def setXHeight (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.xHeight_value = value

	def setItalicAngle (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.italicAngle_value = value

	def setCaretOffset (self, value, layer=None):
		if layer is not None:
			self.fl.setMaster(layer)
		self.fl.caretOffset_value = value

	# - Export & Import
	def asDict(self, layer=None):
		# - Genius!!!!
		getterFunctions = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__") and 'get' in func]
		return {getter.replace('get',''):getattr(self, getter)(layer) for getter in getterFunctions} 

	def fromDict(self, metricDict, layer=None):
		for func, value in metricDict.iteritems():
			eval("self.set%s(%s, '%s')" %(func, value, layer))


class pFont(object):
	'''
	A Proxy Font representation of Fonlab fgFont and flPackage.

	Constructor:
		pFont() - default represents the current glyph and current font
		pFont(fgFont)
	
	'''

	def __init__(self, font=None):

		if font is not None:
			self.fg = font
			self.fl = fl6.flPackage(font)
			
		else:
			self.fg = fl6.CurrentFont()
			self.fl = fl6.flPackage(fl6.CurrentFont())

		# - Basics
		self.italic_angle = self.getItalicAngle()
		self.info = self.fg.info
		self.familyName = self.info.familyName
		self.name = self.familyName # Change later
		self.OTfullName = self.info.openTypeNameCompatibleFullName
		self.PSfullName = self.info.postscriptFullName

		# - Special 
		self.__altMarks = {'liga':'_', 'alt':'.', 'hide':'__'}
		self.__diactiricalMarks = ['grave', 'dieresis', 'macron', 'acute', 'cedilla', 'uni02BC', 'circumflex', 'caron', 'breve', 'dotaccent', 'ring', 'ogonek', 'tilde', 'hungarumlaut', 'caroncomma', 'commaaccent', 'cyrbreve'] # 'dotlessi', 'dotlessj'

	
	def __repr__(self):
		return '<%s name=%s glyphs=%s path=%s>' % (self.__class__.__name__, self.fg.info.familyName, len(self.fg), self.fg.path)

	# - Font Basics -----------------------------------------------
	def getSelectedIndices(self):
		# WARN: Legacy syntax used, as of current 6722 build there is no way to get the selected glyphs in editor
		return [index for index in range(len(legacy.fl.font)) if legacy.fl.Selected(index)]

	def selected_pGlyphs(self):
		'''Return TypeRig proxy glyph object for each selected glyph'''
		return self.pGlyphs(self.selectedGlyphs())

	def selectedGlyphs(self):
		'''Return TypeRig proxy glyph object for each selected glyph'''
		return self.glyphs(self.getSelectedIndices())

	def glyph(self, glyph):
		'''Return TypeRig proxy glyph object (pGlyph) by index (int) or name (str).'''
		if isinstance(glyph, int) or isinstance(glyph, basestring):
			return pGlyph(self.fg, self.fg[glyph])
		else:
			return pGlyph(self.fg, glyph)

	def symbol(self, gID):
		'''Return fgSymbol by glyph index (int)'''
		return fl6.fgSymbol(gID, self.fg)

	def glyphs(self, indexList=[]):
		'''Return list of FontGate glyph objects (list[fgGlyph]).'''
		return self.fg.glyphs if not len(indexList) else [self.fg.glyphs[index] for index in indexList]

	def symbols(self):
		'''Return list of FontGate symbol objects (list[fgSymbol]).'''
		return [self.symbol(gID) for gID in range(len(self.fg.glyphs))]
	
	def pGlyphs(self, fgGlyphList=[]):
		'''Return list of TypeRig proxy Glyph objects glyph objects (list[pGlyph]).'''
		return [self.glyph(glyph) for glyph in self.fg] if not len(fgGlyphList) else [self.glyph(glyph) for glyph in fgGlyphList]

	# - Font metrics -----------------------------------------------
	def getItalicAngle(self):
		return self.fl.italicAngle_value

	def fontMetricsInfo(self, layer):
		'''Returns Font(layer) metrics no matter the reference.
		Args:
			layer (int or str): Layer index or name. If None returns ActiveLayer
		Returns:
			FontMetrics (object)
		'''
		if isinstance(layer, int):
			return fl6.FontMetrics(self.fl, self.fl.masters[layer]) 

		elif isinstance(layer, basestring):
			return fl6.FontMetrics(self.fl, layer)

	def fontMetrics(self):
		'''Returns pFontMetrics Object with getter/setter functionality'''
		from typerig.proxy import pFontMetrics
		return pFontMetrics(self.fl)

	def updateObject(self, flObject, undoMessage='TypeRig', verbose=True):
		'''Updates a flObject sends notification to the editor as well as undo/history item.
		Args:
			flObject (flGlyph, flLayer, flShape, flNode, flContour): Object to be update and set undo state
			undoMessage (string): Message to be added in undo/history list.
		'''
		fl6.flItems.notifyChangesApplied(undoMessage, flObject, True)
		if verbose: print 'DONE:\t %s' %undoMessage

	def update(self):
		self.updateObject(self.fl, verbose=False)

	# - Axes and MM ----------------------------------------------------
	def axes(self):
		return self.fl.axes

	def masters(self):
		return self.fl.masters

	def hasMaster(self, layerName):
		return self.fl.hasMaster(layerName)

	def instances(self):
		return self.fl.instances

	# - Guides & Hinting Basics ----------------------------------------
	def guidelines(self, hostInf=False, fontgate=False):
		'''Return font guidelines
		Args:
			hostInf (bool): If True Return flHostInfo guidelines host objects
			fontgate (bool): If True return FontGate font guideline objects
		Returns
			list[flGuideline] or list[fgGuideline]
		'''
		if not fontgate:
			return self.fl.guidelines if not hostInf else self.fl.guidelinesHost.guidelines
		else:
			return self.fg.guides

	def addGuideline(self, flGuide):
		'''Adds a guideline (flGuide) to font guidelines'''
		self.fl.guidelinesHost.appendGuideline(flGuide)
		self.fl.guidelinesHost.guidelinesChanged()

	def delGuideline(self, flGuide):
		'''Removes a guideline (flGuide) from font guidelines'''
		self.fl.guidelinesHost.removeGuideline(flGuide)
		self.fl.guidelinesHost.guidelinesChanged()

	def clearGuidelines(self):
		'''Removes all font guidelines'''
		self.fl.guidelinesHost.clearGuidelines()
		self.fl.guidelinesHost.guidelinesChanged()

	def getZones(self, layer=None, HintingDataType=0):
		'''Returns font alignment (blue) zones (list[flGuideline]). Note: HintingDataType = {'HintingPS': 0, 'HintingTT': 1}'''
		backMasterName = self.fl.master
		if layer is not None: self.fl.setMaster(layer)
		zoneQuery = (self.fl.zones(HintingDataType, True), self.fl.zones(HintingDataType, False)) # tuple(top, bottom) zones
		if self.fl.master != backMasterName: self.fl.setMaster(backMasterName)	
		return zoneQuery

	def setZones(self, fontZones, layer=None):
		backMasterName = self.fl.master

		if layer is not None: self.fl.setMaster(layer)
		self.fl.convertZonesToGuidelines(*fontZones) # Dirty register zones	
		if self.fl.master != backMasterName: self.fl.setMaster(backMasterName)

		self.update()

	def zonesToTuples(self, layer=None, HintingDataType=0):
		fontZones = self.getZones(layer, HintingDataType)
		return [(zone.position, zone.width, zone.name) for zone in fontZones[0]] + [(zone.position, -zone.width, zone.name) for zone in fontZones[1]]

	def zonesFromTuples(self, zoneTupleList, layer=None, forceNames=False):
		fontZones = ([], [])

		for zoneData in zoneTupleList:
			isTop = zoneData[1] >= 0
			newZone = fl6.flZone(zoneData[0], abs(zoneData[1]))
			
			if forceNames and len(zoneData) > 2: newZone.name = zoneData[2]
			newZone.guaranteeName(isTop)
			
			fontZones[not isTop].append(newZone)

		if not len(fontZones[1]):
			fontZones[1].append(fl6.flZone())

		self.setZones(fontZones, layer)

	def addZone(self, position, width, layer=None):
		''' A very dirty way to add a new Zone to Font'''
		isTop = width >= 0
		backMasterName = self.fl.master
		fontZones = self.getZones(layer)
		
		newZone, killZone = fl6.flZone(position, abs(width)), fl6.flZone()
		newZone.guaranteeName(isTop)

		fontZones[not isTop].append([newZone, killZone][not isTop])
		fontZones[isTop].append([newZone, killZone][isTop])
				
		if layer is not None: self.fl.setMaster(layer)
		self.fl.convertZonesToGuidelines(*fontZones)
		if self.fl.master != backMasterName: self.fl.setMaster(backMasterName)	

		self.update()
		
	def hinting(self):
		'''Returns fonts hinting'''
		return self.fg.hinting

	# - Charset -----------------------------------------------
	# -- Return Names
	def getGlyphNamesDict(self):
		# -- Init
		nameDict = {}

		# --- Controls and basic latin: 0000 - 0080
		nameDict['Latin_Upper'] = [self.fl.findUnicode(uni).name for uni in range(0x0000, 0x0080) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).isupper()]
		nameDict['Latin_Lower'] = [self.fl.findUnicode(uni).name for uni in range(0x0000, 0x0080) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).islower()]

		# --- Latin 1 Supplement: 0080 - 00FF
		nameDict['Latin1_Upper'] = [self.fl.findUnicode(uni).name for uni in range(0x0080, 0x00FF) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).isupper()]
		nameDict['Latin1_Lower'] = [self.fl.findUnicode(uni).name for uni in range(0x0080, 0x00FF) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).islower()]

		# --- Latin A: unicode range 0100 - 017F
		nameDict['LatinA_Upper'] = [self.fl.findUnicode(uni).name for uni in range(0x0100, 0x017F) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).isupper()]
		nameDict['LatinA_Lower'] = [self.fl.findUnicode(uni).name for uni in range(0x0100, 0x017F) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).islower()]

		# --- Latin B: unicode range 0180 - 024F
		nameDict['LatinB_Upper'] = [self.fl.findUnicode(uni).name for uni in range(0x0180, 0x024F) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).isupper()]
		nameDict['LatinB_Lower'] = [self.fl.findUnicode(uni).name for uni in range(0x0180, 0x024F) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).islower()]

		# --- Cyrillic: unicode range 0400 - 04FF
		nameDict['Cyrilic_Upper'] = [self.fl.findUnicode(uni).name for uni in range(0x0400, 0x04FF) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).isupper()]
		nameDict['Cyrilic_Lower'] = [self.fl.findUnicode(uni).name for uni in range(0x0400, 0x04FF) if isinstance(self.fl.findUnicode(uni), fl6.flGlyph) and unichr(uni).islower()]
		
		return nameDict		
	
	# -- Return Glyphs
	def uppercase(self):
		'''Returns all uppercase characters (list[fgGlyph])'''
		return [glyph for glyph in self.fg if glyph.unicode is not None and glyph.unicode < 10000 and unichr(glyph.unicode).isupper()] # Skip Private ranges - glyph.unicode < 10000

	def lowercase(self):
		'''Returns all uppercase characters (list[fgGlyph])'''
		return [glyph for glyph in self.fg if glyph.unicode is not None and glyph.unicode < 10000 and unichr(glyph.unicode).islower()]		

	def figures(self):
		'''Returns all uppercase characters (list[fgGlyph])'''
		return [glyph for glyph in self.fg if glyph.unicode is not None and glyph.unicode < 10000 and unichr(glyph.unicode).isdigit()]	

	def symbols(self):
		'''Returns all uppercase characters (list[fgGlyph])'''
		return [glyph for glyph in self.fg if glyph.unicode is not None and glyph.unicode < 10000 and not unichr(glyph.unicode).isdigit() and not unichr(glyph.unicode).isalpha()]

	def ligatures(self):
		'''Returns all ligature characters (list[fgGlyph])'''
		return [glyph for glyph in self.fg if self.__altMarks['liga'] in glyph.name and not self.__altMarks['hide'] in glyph.name]

	def alternates(self):
		'''Returns all alternate characters (list[fgGlyph])'''
		return [glyph for glyph in self.fg if self.__altMarks['alt'] in glyph.name and not self.__altMarks['hide'] in glyph.name]

	# - Information -----------------------------------------------
	def info(self):
		return self.info
