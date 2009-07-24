import sys
import gtk
import xmlrpclib
import re

import config

from gobject import TYPE_STRING
from ctypes import *

class Names(Structure):
	_fields_ = [('marty', c_char_p),
				('biff', c_char_p)]

class Types(Structure):
	_fields_ = [('ONESHOT', c_int),
				('PERIODIC', c_int),
				('TRIGGER', c_int)]

class DataItem:
	key = ''
	ctype = None
	keytype = ''
	explanation = ''	
	
	def __init__(self, key, keytype, explanation, ctype = c_int):
		self.key = key
		self.ctype = ctype
		self.keytype = keytype
		self.explanation = explanation

class DataItems:
	_fields_ = []
	_types_ = []
	_explanations_ = []

	def __init__(self, data_items):
		for item in data_items:
			self._fields_.append((item.key, item.ctype))
			self._types_.append(item.keytype)
			self._explanations_.append(item.explanation)

class DataItems404Error(Exception):
	'''Used if config file can't be read'''
	pass

class DataItemsLoader:
	
	def __init__(self):
		self.config_file = config.DATAITEMS_PATH
		self.raw = ''
		self.lines = None
		self.data_items = []
		try:
			config_file = open(self.config_file)
			self.raw = config_file.read().strip()
		except IOError, e:
			raise DataItems404Error('Error on opening config file: ' + config.DATAITEMS_PATH)

		self.lines = self.raw.split("\n")
		for line in self.lines:
			line = line.strip()	
			# skip empty or comment lines
			if line == '':
				continue
			if line[0] == '#':
				continue
			# replace all tabstops
			line = re.sub(r'\t+', ':', line)
			items = line.split(':')
			# ignore lines that don't have the format NAME TYPE (IMPL) EXPLANATION
			if items.count < 3:
				continue
			# ignore lines that are not implemented (impl = *)
			if items[2].strip()[0] != '*':
				continue
			d = DataItem(items[0].strip(), items[1].strip(), items[3])
			self.data_items.append(d)

	def get_data_items(self):
		return self.data_items

class ClioLoadApp:

	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()
     
	def on_btn_go_clicked(self, widget, data=None):
		order = {}
		order['name1'] = str(self.box_name1.get_active_text())
		#order['name2'] = str(self.box_name2.get_active_text())
		order['dataitem'] = str(self.box_dataitem.get_active_text())
		order['type'] = str(self.box_type.get_active_text()).lower()
		#print 'TEST: ' + str(self.box_name2.get_active_text())
		#print self.box_name2.sensitive
		print order
		print self.rpc_server.commit_load_order(order)		
		self.__send_request()

	def on_btn_clear_clicked(self, widget, data=None):
		pass

	def on_box_dataitem_changed(self, widget, data=None):
		'''Update status bar with operation in plain text and enable/disable second name box'''
		# index of selected dataitem
		index = self.box_dataitem.get_active()
		status = "Operation: " + self.dataitems._explanations_[index]
		# remove old stuff from statusbar and add new status
		self.statusbar.pop(self.statusbar_cid)
		self.statusbar.push(self.statusbar_cid, status)
		# check whether the dataitem is a node/interface-request or a link-request
		single_name_types = ['n', 'i']
		multi_name_types  = ['l']
		# note/interface-requests are only for one host. disable second name field
		if self.dataitems._types_[index] in single_name_types:
			self.box_name2.set_sensitive(False)
		else:
			self.box_name2.set_sensitive(True)

	def __init__(self):
		'''Prepare Data for GUI and Tests'''		
		builder = gtk.Builder()
		builder.add_from_file("loadapp.xml") 

		self.window = builder.get_object("window")
		self.box_name1 = builder.get_object("box_name1")
		self.box_name2 = builder.get_object("box_name2")
		self.box_dataitem = builder.get_object("box_dataitem")
		self.box_type = builder.get_object("box_type")
		self.btn_clear = builder.get_object("btn_clear")
		self.btn_go = builder.get_object("btn_go")
		self.statusbar = builder.get_object("statusbar")
		builder.connect_signals(self)   

		self.statusbar_cid = self.statusbar.get_context_id("CLIO LoadApp")
		
		# load dataitems from text file
		dil = DataItemsLoader()
		# let DataItems() class prepare its own data (by passing a list of
		# DataItem() objects
		self.dataitems 	= DataItems(dil.get_data_items())
		types		= Types()
		names		= Names()
		# fill all comboboxes with data
		self.__update_box(self.box_dataitem, self.dataitems._fields_)
		self.__update_box(self.box_name1, names._fields_)
		self.__update_box(self.box_name2, names._fields_)
		self.__update_box(self.box_type, types._fields_)

		try:		
			self.rpc_server = xmlrpclib.ServerProxy('http://localhost:46000')
			print self.rpc_server.system.listMethods()
		except StandardError, e:
			print "Error: ", e

	def __send_request(self):
		order = {}
		order['name1'] = str(self.box_name1.get_active_text())
		order['name2'] = str(self.box_name2.get_active_text())
		order['dataitem'] = str(self.box_dataitem.get_active_text())
		order['type'] = str(self.box_type.get_active_text()).lower()
		#print 'TEST: ' + str(self.box_name2.get_active_text())
		print order
		print self.rpc_server.commit_load_order(order)

	def __update_box(self, box, dic):
		'''Loads a dictionary into the given combo-box'''		
		#l = gtk.ListStore(TYPE_STRING)
		box.remove_text(0)
		for key,item in dic:
			box.append_text(str(key))
			#iter = l.append()
			#l.set(iter, 0, str(key))
		#box.set_model(l)

	def main(self):
		'''Init GUI-Window'''
		self.window.show()
		gtk.main()

if __name__ == "__main__":
	editor = ClioLoadApp()
	editor.main()

# marty biff
# localhost:46000 -> 
