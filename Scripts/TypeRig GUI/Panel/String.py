#FLM: TAB String
# ----------------------------------------
# (C) Vassil Kateliev, 2018 (http://www.kateliev.com)
# (C) Karandash Type Foundry (http://www.karandash.eu)
#-----------------------------------------

# No warranties. By using this you agree
# that you use it at your own risk!

# - Init
app_name, app_version = 'TypeRig | String', '0.20'
glyphSep = '/'

# - Dependencies -----------------
import fontlab as fl6
import fontgate as fgt
from PythonQt import QtCore, QtGui
from typerig.proxy import pFont
from typerig.string import stringGen, strRepDict, fillerList

# - Tabs -------------------------------
class QStringGen(QtGui.QGridLayout):
	def __init__(self):
		super(QStringGen, self).__init__()
		# - Init data
		val_fillerLeft, val_fillerRight = zip(*fillerList)
		
		# -- Init Interface 
		self.edt_inputA = QtGui.QLineEdit()
		self.edt_inputB = QtGui.QLineEdit()
		self.edt_suffixA = QtGui.QLineEdit()
		self.edt_suffixB = QtGui.QLineEdit()
		self.edt_fillerLeft = QtGui.QLineEdit()
		self.edt_fillerRight = QtGui.QLineEdit()
		self.edt_fillerPattern = QtGui.QLineEdit()
		self.edt_output = QtGui.QTextEdit()

		self.edt_inputA.setToolTip('Manual Glyph names input. [SPACE] delimited.\nNOTE: This field overrides the input combo box!')
		self.edt_inputB.setToolTip('Manual Glyph names input. [SPACE] delimited.\nNOTE: This field overrides the input combo box!')
		self.edt_suffixA.setToolTip('Suffix to be added to each glyph name.')
		self.edt_suffixB.setToolTip('Suffix to be added to each glyph name.')
		self.edt_fillerLeft.setToolTip('Manual input for Left Filler String.\nNOTE: This field overrides the input combo box! No separator!')
		self.edt_fillerRight.setToolTip('Manual input for Right Filler String.\nNOTE: This field overrides the input combo box! No separator!')
		self.edt_fillerPattern.setToolTip('Generator pattern expression.\n<< Filed names >> in any order, [SPACE] separated.')
		
		self.edt_fillerPattern.setText('FL A B A FR')

		#self.edt_inputA.setEnabled(False)
		#self.edt_inputB.setEnabled(False)
		#self.edt_fillerLeft.setEnabled(False)
		#self.edt_fillerRight.setEnabled(False)
		
		self.cmb_inputA = QtGui.QComboBox()
		self.cmb_inputB = QtGui.QComboBox()
		self.cmb_fillerLeft = QtGui.QComboBox()
		self.cmb_fillerRight = QtGui.QComboBox()

		self.cmb_inputA.setToolTip('Glyph names list.')
		self.cmb_inputB.setToolTip('Glyph names list.')
		self.cmb_fillerLeft.setToolTip('Left Filler String.')
		self.cmb_fillerRight.setToolTip('Right Filler String.')

		self.cmb_fillerLeft.addItems(val_fillerLeft)
		self.cmb_fillerRight.addItems(val_fillerRight)
				
		self.btn_genCopy = QtGui.QPushButton('Generate and send to &Clipboard')
		self.btn_refresh = QtGui.QPushButton('&Populate lists')
		self.btn_clear = QtGui.QPushButton('&Rest fields')

		self.btn_genCopy.setToolTip('Generate the pair string and sent it to the cliboard.')
		self.btn_refresh.setToolTip('Populate name lists with existing glyph names in active font.')
		self.btn_clear.setToolTip('Clear all manual input fields.')

		self.btn_clear.clicked.connect(self.clear)
		self.btn_refresh.clicked.connect(self.refresh)
		self.btn_genCopy.clicked.connect(self.generate)
		
		# - Build
		self.addWidget(QtGui.QLabel('A:'), 		0, 0, 1, 1)
		self.addWidget(self.cmb_inputA, 		0, 1, 1, 5)
		self.addWidget(QtGui.QLabel('Suffix:'), 0, 6, 1, 1)
		self.addWidget(self.edt_suffixA, 		0, 7, 1, 2)
		self.addWidget(self.edt_inputA, 		1, 1, 1, 8)
		self.addWidget(QtGui.QLabel('B:'), 		2, 0, 1, 1)
		self.addWidget(self.cmb_inputB, 		2, 1, 1, 5)
		self.addWidget(QtGui.QLabel('Suffix:'), 2, 6, 1, 1)
		self.addWidget(self.edt_suffixB, 		2, 7, 1, 2)
		self.addWidget(self.edt_inputB, 		3, 1, 1, 8)
		self.addWidget(QtGui.QLabel('FL:'), 	4, 0, 1, 1)
		self.addWidget(self.cmb_fillerLeft, 	4, 1, 1, 5)
		self.addWidget(self.edt_fillerLeft, 	4, 6, 1, 3)
		self.addWidget(QtGui.QLabel('FR:'), 	5, 0, 1, 1)
		self.addWidget(self.cmb_fillerRight, 	5, 1, 1, 5)
		self.addWidget(self.edt_fillerRight, 	5, 6, 1, 3)
		self.addWidget(QtGui.QLabel('E:'), 		6, 0, 1, 1)
		self.addWidget(self.edt_fillerPattern, 	6, 1, 1, 8)
		self.addWidget(self.btn_refresh, 		7, 1, 1, 5)
		self.addWidget(self.btn_clear, 			7, 6, 1, 3)
		self.addWidget(self.btn_genCopy, 		8, 1, 1, 8)
		self.addWidget(QtGui.QLabel('OUT:'), 	9, 0, 1, 1)
		self.addWidget(self.edt_output, 		9, 1, 4, 8)

		self.setColumnStretch(0, 0)
		self.setColumnStretch(1, 2)
		self.setColumnStretch(6, 0)
		self.setColumnStretch(7, 1)
				
	# - Procedures
	def clear(self):
		self.edt_inputA.clear()
		self.edt_inputB.clear()
		self.edt_suffixA.clear()
		self.edt_suffixB.clear()
		self.edt_fillerLeft.clear()
		self.edt_fillerRight.clear()
		self.edt_output.clear()
		self.edt_fillerPattern.setText('FL A B A FR')

	def refresh(self):
		self.font = pFont()
		self.glyphNames = self.font.getGlyphNamesDict()

		self.cmb_inputA.addItems(sorted(self.glyphNames.keys()))
		self.cmb_inputB.addItems(sorted(self.glyphNames.keys()))	

		print 'DONE:\t Active font glyph names loaded into generator.'	

	def generate(self):
		# - Get Values
		if len(self.edt_inputA.text) > 0:
			try:
				inputA = [self.font.fl.findUnicode(ord(item)).name for item in self.edt_inputA.text.split(' ')] 
			except AttributeError:
				print 'WARN:\t Unicode (Input A) to current font glyph names mapping is not activated! Please populate lists first.'
				inputA = self.edt_inputA.text.split(' ')
		else:
			inputA = sorted(self.glyphNames[self.cmb_inputA.currentText])

		if len(self.edt_inputB.text) > 0:
			try:
				inputB = [self.font.fl.findUnicode(ord(item)).name for item in self.edt_inputB.text.split(' ')]  
			except AttributeError:
				print 'WARN:\t Unicode (Input B) to current font glyph names mapping is not activated! Please populate lists first.'
				inputB = self.edt_inputB.text.split(' ')
		else:
			inputB = sorted(self.glyphNames[self.cmb_inputB.currentText])

		if len(self.edt_fillerLeft.text) > 0:
			fillerLeft = self.edt_fillerLeft.text
		else:
			fillerLeft = self.cmb_fillerLeft.currentText

		if len(self.edt_fillerRight.text) > 0:
			fillerRight = self.edt_fillerRight.text
		else:
			fillerRight = self.cmb_fillerRight.currentText

		# - Generate
		generatedString = stringGen(inputA, inputB, (fillerLeft, fillerRight), self.edt_fillerPattern.text, (self.edt_suffixA.text, self.edt_suffixB.text), glyphSep)
		self.edt_output.setText('\n'.join(generatedString))
		
		# - Copy to cliboard
		clipboard = QtGui.QApplication.clipboard()
		clipboard.setText('\n'.join(generatedString))
		print 'DONE:\t Generated string sent to clipboard.'
					
class tool_tab(QtGui.QWidget):
	def __init__(self):
		super(tool_tab, self).__init__()

		# - Init
		layoutV = QtGui.QVBoxLayout()
		self.strGenerator = QStringGen()

		# - Build ---------------------------
		layoutV.addWidget(QtGui.QLabel('String generator:'))
		layoutV.addLayout(self.strGenerator)

		layoutV.addStretch()
		self.setLayout(layoutV)

# - Test ----------------------
if __name__ == '__main__':
	test = tool_tab()
	test.setWindowTitle('%s %s' %(app_name, app_version))
	test.setGeometry(300, 300, 200, 400)
	test.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # Always on top!!
	
	test.show()