#!/usr/bin/env python3
'''
unisono_gui.py

 Created on: Aug 03, 2009
 Authors: korscheck (zxmmi77)
 
 $LastChangedBy: haage $
 $LastChangedDate: 2009-07-22 13:40:53 +0200 (Wed, 22 Jul 2009) $
 $Revision: 1555 $
 
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
import xmlrpclib
import gtk
import copy
from datetime import datetime
from datetime import timedelta

'''
TODO:
- fill "VIEW"-Notebook with data (all three pages)
- make adding several nodes possible. currently, the GUI connects only
  to localhost and fills the GUI with data.
  -> notebook-frame must be deepcopied
  -> list of pages must distinguish between different XML-RPC-hosts
'''

# main class
class UnisonoGUI:
	'''GUI-Client for UNISONO'''

	def __init__(self):
		'''Prepares Data for GUI and order-commit'''		
		self.builder = gtk.Builder()
		self.builder.add_from_file("unisono_gui.xml") 

		# general widgets
		self.window = self.builder.get_object("window")
		self.notebook = self.builder.get_object("notebook")
		self.notebook_frame = self.builder.get_object("notebook_frame")
		self.statusbar = self.builder.get_object("statusbar")
		self.statusbar_cid = self.statusbar.get_context_id("UNISONO GUI")
		# buttons
		self.btn_connect = self.builder.get_object("btn_connect")
		self.btn_refresh = self.builder.get_object("btn_refresh")
		# text views
		self.builder.connect_signals(self)   

		self.rpc_server = None
		self.node_count = 0
		self.connected = False

	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()

	def on_btn_refresh_clicked(self, widget, data=None):
		self.__load_node_data()

	def on_btn_connect_clicked(self, widget, data=None):
		self.__connect_node('http://localhost:45678')
		# after connect, load data from host
		if self.connected == True:
			self.__load_node_data()

	def __connect_node(self, url):
		'''Connects to UNISONO XML-RPC'''
		try:		
			self.rpc_server = xmlrpclib.ServerProxy(url)
			self.connected = True
			self.__update_status_bar('Successfully connected to RPC-server ('+ url +')')
			self.node_count += 1
		except StandardError, e:
			self.__update_status_bar("Error on connecting to RPC-server: " + repr(e))
		
	def __load_node_data(self):
		'''Load data from UNISONO host'''
		if self.connected == False:
			self.__update_status_bar("Can't load data, not connected to server!")
			return
		
		stats = self.rpc_server.getStats()
		self.__refresh_stats(stats)
		log = self.rpc_server.getLog()
		self.__refresh_log(log)

		db = self.rpc_server.getDB()
		print 'DB:'
		print db
		print('-------------------------------------------------------')
		
	def __refresh_stats(self, stats):
		'''Fills GUI elements with stats received from UNISONO'''		
		# identifier
		buf = "\n".join(stats['identifiers'])
		self.__update_textbox(self.builder.get_object("txt_identifier"), buf)
		# connectors
		buf = "\n".join(stats['connectors'])
		self.__update_textbox(self.builder.get_object("txt_connectors"), buf)

		# print these fields in date-format, not directly as strings
		date_fields = ['starttime', 'db_purge']
		# ignore these fields, because they have no GUI representation or are
		# handled somewhere else already
		ignore_fields = ['identifiers', 'connectors', 'cputimestamp']

		# assign all fields to the according labels in GUI
		for field in stats.keys():
			if field in ignore_fields:
				continue
			if field in date_fields:
				val = str(datetime.fromtimestamp(int(stats[field])))
			elif field == 'uptime':
				val = str(timedelta(0, int(stats[field])))
			else:
				val = str(stats[field])
			# labels in gui are named lbl_fieldname
			obj = self.builder.get_object("lbl_" + field)
			# check whether we can find this label or not. this comes in handy, if
			# UNISONO stats are extended such that more fields are returned by
			# the XML-RPC, but the GUI isn't adjusted yet
			if obj != None:
				obj.set_text(val)
			else:
				print "Stats for '"+ field +"' can't be displayed. No label in GUI."

		self.__update_status_bar('Last Refresh: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

	def __refresh_log(self, log):
		'''Fills GUI element with log file data'''
		self.__update_textbox(self.builder.get_object("txt_log"), log)

	def __update_textbox(self, obj, text):
		'''Helper to disable text field, update text and re-enable'''		
		obj.set_sensitive(False)		
		buff = obj.get_buffer()
		buff.set_text(text)
		buff.set_modified(False)        
		obj.set_sensitive(True)
	
	def __update_status_bar(self, status):
		'''Helper to update status bar'''
		self.statusbar.pop(self.statusbar_cid)
		self.statusbar.push(self.statusbar_cid, status)

	def main(self):
		'''Init GUI-Window'''
		self.window.show()
		gtk.main()

if __name__ == '__main__':
	gui = UnisonoGUI()
	gui.main()

