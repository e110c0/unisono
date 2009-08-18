'''
loadapp.py

 Created on: Jul 21, 2009
 Authors: korscheck (zxmmi77)

 $LastChangedBy$
 $LastChangedDate$
 $Revision$

 (C) 2008-2009 by Computer Networks and Internet, University of Tuebingen

 This file is part of UNISONO Unified Information Service for Overlay
 Network Optimization.

 UNISONO is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 2 of the License, or
 (at your option) any later version.

 UNISONO is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with UNISONO.  If not, see <http://www.gnu.org/licenses/>.

'''
import sys
import gtk
import xmlrpclib
import re
from datetime import datetime
from time import localtime, strftime, sleep
from gobject import TYPE_STRING
from threading import Timer

import loadapp_config

config = loadapp_config

# some types required to modify sensitivity of widgets
single_name_types = ['n', 'i']
multi_name_types  = ['l']
time_types  = ['PERIODIC', 'TRIGGERED']
threshold_types = ['TRIGGERED']

# host-names
class Names:
	_fields_ = ['marty', 'biff']

# order-types
class Types:
	_fields_ = ['ONESHOT', 'PERIODIC', 'TRIGGERED']

# helper class, an element in DataItems list
class DataItem:
	key = ''
	keytype = ''
	explanation = ''	
	
	def __init__(self, key, keytype, explanation):
		self.key = key
		self.keytype = keytype
		self.explanation = explanation

# list with DataItems. Note: this class doesn't have only the fields, but also
# additional data that is required for output in the GUI or other modifications
# for the widgets (like setting sensitive)
class DataItems:
	_fields_ = []
	_types_ = []
	_explanations_ = []

	def __init__(self, data_items):
		for item in data_items:
			self._fields_.append(item.key)
			self._types_.append(item.keytype)
			self._explanations_.append(item.explanation)

class DataItemsLoader:
	'''Reads data-items from file and parses the format'''	
	def __init__(self):
		self.config_file = config.DATAITEMS_PATH
		self.raw = ''
		self.lines = None
		self.data_items = []
		try:
			config_file = open(self.config_file)
			self.raw = config_file.read().strip()
			config_file.close()
		except IOError, e:
			print 'Error on opening UNISONO config file: ' + config.DATAITEMS_PATH
			return

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

class ConnectorLogLoader:
	'''Reads a logfile and parses the data'''

	def __init__(self):
		self.logfile = '/tmp/clioloadapp-log-' + datetime.now().strftime("%d-%m-%y")
		print "Using Logfile '" + self.logfile + "' to get results"

	def __load_data(self):
		self.order_results = {}	
		try:
			fh = open(self.logfile)
			self.raw = fh.read().strip()
			fh.close()
		except IOError, e:
			print 'Error on reading logfile: ' + e
			return

		self.lines = self.raw.split("\n")
		for line in self.lines:
			dataitems = line.split(';')
			# check if we have at least 3 data items (timestamp, result_type, orderid)
			if len(dataitems) < 3:
				print 'Corrupt line in logfile? ' + line
				continue

			if dataitems[1] == 'RESULT':
				data = {				
					'timestamp' : dataitems[0],
					'result' : dataitems[3],
					'errno' : dataitems[4],
					'errmsg' : dataitems[5]
				}

				if not self.order_results.has_key(dataitems[2]):
					self.order_results[dataitems[2]] = []
				self.order_results[dataitems[2]].append(data)					


	def get_order_results(self, orderid):
		'''Returns string representation of results for an order'''
		# update data from text file
		self.__load_data()
		if not self.order_results.has_key(orderid):
			return 'No data for this order'
		order_data = self.order_results[orderid]
		s = ''
		for d in order_data:
			s += strftime("%d-%m-%Y %H:%m:%S", localtime(int(d['timestamp'])))
			if d['errno'] != '0':
				s += ' ERROR (' + str(d['errno']) + '): ' + str(d['errmsg'])
			else:
				s += ' RESULT: ' + str(d['result'])
			s += "\n"
		return s

# main class
class ClioLoadApp:
	'''Class for GUI and order-submit'''
	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()
     
	def on_btn_go_clicked(self, widget, data=None):
		# notebook page = single order
		if self.notebook.get_current_page() == 0:
			self.__send_request()
		# notebook page = batch order
		elif self.notebook.get_current_page() == 1:
			scenario = self.box_batch.get_active_text()
			self.__send_batch_requests(scenario)

	def on_btn_ordertostr_clicked(self, widget, data=None):
		'''Helper to output current order to generate batch-orders'''
		n1 = str(self.box_name1.get_active_text())
		n2 = str(self.box_name2.get_active_text())
		if n2 == 'None': n2 = ''
		di = str(self.box_dataitem.get_active_text())
		ty = str(self.box_type.get_active_text())
		if self.box_type.get_active_text() in time_types:
			iv = str(self.sbtn_interval.get_value_as_int())
			li = str(self.sbtn_lifetime.get_value_as_int())
		else:
			iv,li = '0','0'
		if self.box_type.get_active_text() in threshold_types:
			ut = str(self.sbtn_upper_threshold.get_value_as_int())
			lt = str(self.sbtn_lower_threshold.get_value_as_int())
		else:
			ut,lt = '0','0'
		print "[0, '"+n1+"', '"+n2+"', '"+di+"', '"+ty+"', "+iv+", "+li+", "+ut+", "+lt+"]"

	def on_btn_cancel_order_clicked(self, widget, data=None):
		treeselection = self.treeview_orders.get_selection()
		(model, iter) = treeselection.get_selected()
		if iter != None:
			index = model.get_path(iter)[0]
			orderid = self.orderlist[index]
			try:
				self.rpc_server.cancel_order(orderid)
				print 'Cancelled order ' + orderid
			except StandardError, e:
				print "Couldn't cancel order "+ orderid + ": ", e

	def on_box_batch_changed(self, widget, data=None):
		scenario = self.box_batch.get_active_text()
		if config.SCENARIOS.has_key(scenario):
			count = len(config.SCENARIOS[scenario])
			self.lbl_order_count.set_text(str(count))
		else:
			self.lbl_order_count.set_text('n/a')

	def on_box_type_changed(self, widget, data=None):
		'''Handles sensitivity of spin buttons'''		
		# enable/disable interval/lifetime buttons		
		if self.box_type.get_active_text() in time_types:
			self.sbtn_interval.set_sensitive(True)
			self.sbtn_lifetime.set_sensitive(True)
		else:
			self.sbtn_interval.set_sensitive(False)
			self.sbtn_lifetime.set_sensitive(False)
		# enable/disable threshold buttons		
		if self.box_type.get_active_text() in threshold_types:
			self.sbtn_upper_threshold.set_sensitive(True)
			self.sbtn_lower_threshold.set_sensitive(True)
		else:
			self.sbtn_upper_threshold.set_sensitive(False)
			self.sbtn_lower_threshold.set_sensitive(False)

	def on_box_dataitem_changed(self, widget, data=None):
		'''Updates status bar with operation in plain text and enable/disable second name box'''
		# index of selected dataitem
		index = self.box_dataitem.get_active()
		status = "Selected Single-Order: " + self.dataitems._explanations_[index]
		# remove old stuff from statusbar and add new status
		self.statusbar.pop(self.statusbar_cid)
		self.statusbar.push(self.statusbar_cid, status)
		# check whether the dataitem is a node/interface-request or a link-request
		# note/interface-requests are only for one host. disable second name field
		if self.dataitems._types_[index] in single_name_types:
			self.box_name2.set_sensitive(False)
		else:
			self.box_name2.set_sensitive(True)

	def on_treeview_selection_changed(self, treeselection):
		'''Note: This method is linked manually in this file, not in the glade- or xml-file'''
		(model, iter) = treeselection.get_selected()
		if iter != None:
			index = model.get_path(iter)[0]
			orderid = self.orderlist[index]
			self.__update_results(orderid)

	def __init__(self):
		'''Prepares Data for GUI and order-commit'''		
		builder = gtk.Builder()
		builder.add_from_file("loadapp.xml") 

		self.orderlist = []
		self.logloader = ConnectorLogLoader()
		# general widgets
		self.window = builder.get_object("window")
		self.statusbar = builder.get_object("statusbar")
		self.lbl_order_count = builder.get_object("lbl_order_count")
		self.notebook = builder.get_object("notebook")
		self.txt_results = builder.get_object("txt_results")
		self.txt_results.set_sensitive(False)
		# comboboxes
		self.box_name1 = builder.get_object("box_name1")
		self.box_name2 = builder.get_object("box_name2")
		self.box_dataitem = builder.get_object("box_dataitem")
		self.box_type = builder.get_object("box_type")
		self.box_batch = builder.get_object("box_batch")
		# spin buttons
		self.sbtn_interval = builder.get_object("sbtn_interval")
		self.sbtn_lifetime = builder.get_object("sbtn_lifetime")
		self.sbtn_upper_threshold = builder.get_object("sbtn_upper_threshold")
		self.sbtn_lower_threshold = builder.get_object("sbtn_lower_threshold")

		builder.connect_signals(self)   

		self.statusbar_cid = self.statusbar.get_context_id("CLIO LoadApp")
		
		# load dataitems from text file
		dil = DataItemsLoader()
		# let DataItems() class prepare its own data (by passing a list of
		# DataItem() objects
		self.dataitems 	= DataItems(dil.get_data_items())
		types = Types()
		names = Names()
		# fill all comboboxes with data
		self.__update_box(self.box_dataitem, self.dataitems._fields_)
		self.__update_box(self.box_name1, names._fields_)
		self.__update_box(self.box_name2, names._fields_)
		self.__update_box(self.box_type, types._fields_)
		# fill scenario combobox with data from config file and add empty selection
		scenarios = config.SCENARIOS.keys()
		self.__update_box(self.box_batch, scenarios)
		# select default values
		self.box_name1.set_active(0)
		self.box_dataitem.set_active(16)
		self.box_type.set_active(0)
		self.box_batch.set_active(0)

		# create a ListBox (not supported in libglade, so we have to do it manually)
		self.orderlist_widget = gtk.ListStore(TYPE_STRING)
		self.treeview_orders = gtk.TreeView()
		self.treeview_orders.set_model(self.orderlist_widget)

		column = gtk.TreeViewColumn()
		cell = gtk.CellRendererText()
		column.pack_start(cell)
		column.add_attribute(cell, 'text', 0)
		self.treeview_orders.append_column(column)
		self.treeview_orders.get_selection().set_mode(gtk.SELECTION_SINGLE)
		builder.get_object("content_orderlist").add(self.treeview_orders)
		self.treeview_orders.set_headers_visible(False)
		self.treeview_orders.show()
		self.treeview_orders.get_selection().connect('changed', lambda s: self.on_treeview_selection_changed(s))

		# connect to RPC server
		try:		
			self.rpc_server = xmlrpclib.ServerProxy(config.RPC_URL)
		except StandardError, e:
			print "Error on loading RPC-server: ", e

	def __send_batch_requests(self, scenario_key):
		orders = config.SCENARIOS[scenario_key]
		print "Executing "+str(len(orders))+" batch-orders from scenario '"+str(scenario_key)+"':"
		for order in orders:
			compose_order = {}
			compose_order['name1'] 		= order[1]
			# if name2 is empty, don't submit it with the order (17.08.09: UNISONO would crash)
			if order[2] != '':
				compose_order['name2'] = order[2]
			compose_order['dataitem'] 	= order[3]
			compose_order['type'] 		= order[4]
			parameters = {}
			if compose_order['type'] in time_types:
				parameters['interval'] = str(order[5])
				parameters['lifetime'] = str(order[6])
			if compose_order['type'] in threshold_types:
				parameters['upper_threshold'] = str(order[7])
				parameters['lower_threshold'] = str(order[8])
			compose_order['parameters'] = parameters
			# now try to submit order after a waiting period
			wait = order[0] / 1000.0
			print 'Comitting order: ' + repr(order) + ' in ' + str(wait) + ' seconds'
			Timer(wait, self.__deploy_order, [compose_order]).start()

	def hello(self):
		print "HELLO WORLD!"

	def __send_request(self):
		'''Build the order-string (a dictionary) and submit it to the RPC-Server'''		
		order = {}
		# name 1
		order['name1'] = str(self.box_name1.get_active_text())
		# name 2 (not required for all dataitems)
		index = self.box_dataitem.get_active()
		if self.dataitems._types_[index] in multi_name_types:
			order['name2'] = str(self.box_name2.get_active_text())
		# dataitem
		order['dataitem'] = str(self.box_dataitem.get_active_text())
		# type
		order['type'] = str(self.box_type.get_active_text())
		# check if any required data is empty
		if 'None' in (order.values()):
			print 'Invalid order. Skip.'
			return
		# prepare additional parameters for TRIGGER/PERIODIC
		parameters = {}
		if self.box_type.get_active_text() in time_types:
			parameters['interval'] = str(self.sbtn_interval.get_value_as_int())
			parameters['lifetime'] = str(self.sbtn_lifetime.get_value_as_int())
		if self.box_type.get_active_text() in threshold_types:
			parameters['upper_threshold'] = str(self.sbtn_upper_threshold.get_value_as_int())
			parameters['lower_threshold'] = str(self.sbtn_lower_threshold.get_value_as_int())

		order['parameters'] = parameters		

		print 'Comitting order: ' + str(order)
		self.__deploy_order(order)

	def __deploy_order(self, order):
		try:
			orderid = self.rpc_server.commit_load_order(order)
			print 'RPC-Response: ' + orderid
		except StandardError, e:
			print "Error on committing order: ", e
		self.orderlist_widget.append((orderid,))
		self.orderlist.append(orderid)

	def __update_box(self, box, dic):
		'''Loads a dictionary into the given combo-box'''		
		box.remove_text(0)
		for key in dic:
			box.append_text(str(key))

	def __update_results(self, orderid):
		self.txt_results.set_sensitive(False)
		buf = self.txt_results.get_buffer()
		data = self.logloader.get_order_results(orderid)
		buf.set_text(data)
		buf.set_modified(False)
		self.txt_results.set_sensitive(True)

	def main(self):
		'''Init GUI-Window'''
		gtk.gdk.threads_init()
		self.window.show()
		gtk.main()


def print_info():
	text = '''Welcome to CLIO LoadApp GUI'''
	print text

if __name__ == "__main__":
	print_info()
	editor = ClioLoadApp()
	editor.main()


