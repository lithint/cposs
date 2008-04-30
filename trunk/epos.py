#!/usr/bin/env python

try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	print "PyGTK Not found"
try:
	import sys
	import basket
	import Database.ProductData as ProductData
	import gtk
	import gtk.glade
	import gobject
	import logging
	import shelve
	import os
	import locale
	import gettext
except:
	print "Import error, epos cannot start. Check your dependencies."
	sys.exit(1)

FILE_EXT = "epos"
APP_NAME = "ePoS"

class epos:
	"""The ePoS"""

	def __init__(self):

		#Translation stuff

		#Get the local directory since we are not installing anything
		self.local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
		# Init the list of languages to support
		langs = []
		#Check the default locale
		lc, encoding = locale.getdefaultlocale()
		if (lc):
			#If we have a default, it's the first in the list
			langs = [lc]
		# Now lets get all of the supported languages on the system
		language = os.environ.get('LANGUAGE', None)
		if (language):
			"""langage comes back something like en_CA:en_US:en_GB:en
			on linuxy systems, on Win32 it's nothing, so we need to
			split it up into a list"""
			langs += language.split(":")
		"""Now add on to the back of the list the translations that we
		know that we have, our defaults"""
		langs += ["en_CA", "en_US"]

		"""Now langs is a list of all of the languages that we are going
		to try to use.  First we check the default, then what the system
		told us, and finally the 'known' list"""

		gettext.bindtextdomain(APP_NAME, self.local_path)
		gettext.textdomain(APP_NAME)
		# Get the language to use
		self.lang = gettext.translation(APP_NAME, self.local_path
			, languages=langs, fallback = True)
		"""Install the language, map _() (which we marked our
		strings to translate with) to self.lang.gettext() which will
		translate them."""
		_ = self.lang.gettext

		# Set the project file
		self.project_file = ""

		#Set the Glade file
		self.gladefile = "Glade/home.glade"

		self.wTree = gtk.glade.XML(self.gladefile, "Home")
		self.win = self.wTree.get_widget("Home")
		self.win.maximize()

		#Initiate the textview element on the GUI
		self.logwindowview=self.wTree.get_widget("Description")
		self.bufferDescription=gtk.TextBuffer(None)
		self.logwindowview.set_buffer(self.bufferDescription)
	
		#Create the dictionary of events and create them
		dic = {		"on_Home_destroy" : self.on_Quit
				, "on_txtBarcode_changed" : self.OnBarcodeChange
				, "on_btnBasket_clicked" : self.OnBasketClick}
		self.wTree.signal_autoconnect(dic)

		#Print out the command line arguments
		#print sys.argv

		#Setup logging
		logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',filename='debug.log')

	def on_Quit(self, widget):
		"""Called when the application is going to quit"""
		gtk.main_quit()

	def OnBarcodeChange(self, widget):
		"""Called when the user types in the text area."""
		ItemID=int(self.wTree.get_widget("txtBarcode").get_text() or 0)
		logging.debug('Barcode changed to %s', ItemID)
        	ItemDetails=ProductData.ProductDictionary(ItemID) 
        	for ControlName in [ "Heading", "Detail1", "Detail2", "Price" ]:
			self.wTree.get_widget(ControlName).set_text("%s" % ItemDetails[ControlName])
		#Simply adds text to the buffer which is being shown in the textarea		
		self.bufferDescription.insert_at_cursor("%s" % ItemDetails["Description"],len("%s" % ItemDetails["Description"]))		
		#print ItemDetails

	def OnBasketClick(self, widget):
		"""Called when we want to take the product to the sale screen"""
		basketScreen=basket.Basket()

	def show_error_dlg(self, error_string):
		"""This Function is used to show an error dialog when
		an error occurs.
		error_string - The error string that will be displayed
		on the dialog.
		"""
		error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR
					, message_format=error_string
					, buttons=gtk.BUTTONS_OK)
		error_dlg.run()
		error_dlg.destroy()

if __name__ == "__main__":
	epos = epos()
	gtk.main()
	
