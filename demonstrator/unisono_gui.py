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
- observe behavior if target host is unreachable
- auto-scroll to end in log file
- manage list with "last hosts" for ComboBoxEntry
'''

default_hosts = ['http://localhost:45678', 'http://134.2.172.173:45678']

class Node:

	def __init__(self, host, node_number):
		self.builder = gtk.Builder()
		self.host = host
		self.node_number = node_number
		self.rpc_server = xmlrpclib.ServerProxy(host)
		self.connected = False
		self.frame = None
		self.last_refresh = 0

	def load_frame(self):
		self.builder.add_from_file("unisono_gui.xml")
		frame = self.builder.get_object("notebook_frame")
		nb = self.builder.get_object("notebook")
		nb.set_tab_detachable(frame, True)
		nb.remove(frame)
		self.builder.get_object("lbl_host").set_text("UNISONO @ " + self.host);
		return frame

# main class
class UnisonoGUI:
	'''GUI-Client for UNISONO'''

	def __init__(self):
		'''Prepares Data for GUI and order-commit'''		
		self.nodes = []

		self.main_builder = gtk.Builder()
		self.main_builder.add_from_file("unisono_gui.xml")

		# general widgets
		self.window = self.main_builder.get_object("window")
		self.notebook = self.main_builder.get_object("notebook")
		self.statusbar = self.main_builder.get_object("statusbar")
		self.statusbar_cid = self.statusbar.get_context_id("UNISONO GUI")
		# buttons
		self.btn_connect = self.main_builder.get_object("btn_connect")
		self.btn_refresh = self.main_builder.get_object("btn_refresh")
		# misc

		# workaround: somehow the comboboxentry created with glade seems to be buggy.
		# for that reason, the glade-file doesn't contain any childs for the connector-frame in
		# the lower left corner. a child is added dynamically here.
		self.box_hosts = gtk.combo_box_entry_new_text()
		self.main_builder.get_object("frame_connect").add(self.box_hosts)
		self.box_hosts.set_name("box_hosts")
		for hn in default_hosts:
			self.box_hosts.append_text(hn)
		self.box_hosts.set_active(0)
		self.box_hosts.show()
#		self.box_hosts = self.main_builder.get_object("box_hosts")
#		self.box_hosts.remove_text(0)		
#		self.box_hosts.append_text('http://localhost:45678')
#		self.box_hosts.append_text('http://134.2.172.173:45678')
#		self.box_hosts.set_active(0)
		self.main_builder.connect_signals(self)   

		main_frame = self.main_builder.get_object("notebook_frame")

		self.notebook.set_tab_detachable(main_frame, True)
		self.notebook.remove(main_frame)

		self.node_count = 0

	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()

	def on_btn_refresh_clicked(self, widget, data=None):
		self.__load_node_data(self.notebook.get_current_page())

	def on_notebook_switch_page(self, notebook, page, page_num):
		index = page_num
		# update statusbar when page is changed
		if len(self.nodes) > index:
			self.__update_status_bar('Last Refresh of Node ' + str(self.nodes[index].node_number) +': ' + self.nodes[index].last_refresh)

	def on_btn_connect_clicked(self, widget, data=None):
		host = self.box_hosts.get_active_text()
		num = self.__node_exists(host)
		if num > -1:
			self.__update_status_bar("I'm already connected to " + host + " (check Node " + str(num) + ")")
			return
		self.__connect_node(host)
		# after connect, load data from host
		self.__load_node_data(self.notebook.get_current_page())

	def __connect_node(self, url):
		'''Setup connection to UNISONO XML-RPC'''
		self.node_count += 1		
		node = Node(url, self.node_count)
		node.connected = True
		frame = node.load_frame()
		self.notebook.append_page(frame, gtk.Label("Node %d" % (self.node_count)))
		self.nodes.append(node)
		self.notebook.set_current_page(self.node_count - 1)
		
	def __load_node_data(self, index):
		'''Load data from UNISONO host'''
		if self.nodes[index].connected == False:
			self.__update_status_bar("Can't load data, not connected to server!")
			return
		
		try:
			rpc_server = self.nodes[index].rpc_server
			stats = rpc_server.getStats()
			self.__refresh_stats(stats, index)
			log = rpc_server.getLog()
			self.__refresh_log(log, index)
			db = rpc_server.getDB()
			print 'DB:'
			print db
			print('-------------------------------------------------------')
		except StandardError, e:
			self.__update_status_bar("Error on loading data from RPC-server: " + str(e))

		
	def __refresh_stats(self, stats, index):
		'''Fills GUI elements with stats received from UNISONO'''		
		# identifier
		buf = "\n".join(stats['identifiers'])
		self.__update_textbox(self.nodes[index].builder.get_object("txt_identifier"), buf)
		# connectors
		buf = "\n".join(stats['connectors'])
		self.__update_textbox(self.nodes[index].builder.get_object("txt_connectors"), buf)

		# print these fields in date-format, not directly as strings
		date_fields = ['starttime', 'db_purge']
		# ignore these fields, because they have no GUI representation or are
		# handled somewhere else already
		ignore_fields = ['identifiers', 'connectors', 'cputimestamp']
		# data arrives in bytes. we want megabytes
		megabyte_fields = ['memory_hwn', 'memory_rss', 'memory_alloc', 'memory_alloc_max']
		# data arrives as float with many digits after point, round a bit
		float_fields = ['cpuuser_current', 'cpusys_current']
		# assign all fields to the according labels in GUI
		for field in stats.keys():
			if field in ignore_fields:
				continue
			if field in date_fields:
				val = str(datetime.fromtimestamp(int(stats[field])))
			elif field == 'uptime':
				val = str(timedelta(0, int(stats[field])))
			elif field in megabyte_fields:
				val = str("%.2f" % (stats[field] / (1024 * 1024))) + ' MB'
			elif field in float_fields:
				val = str("%.2f" % stats[field]) + ' %'
			else:
				val = str(stats[field])
			# labels in gui are named lbl_fieldname
			obj = self.nodes[index].builder.get_object("lbl_" + field)
			# check whether we can find this label or not. this comes in handy, if
			# UNISONO stats are extended such that more fields are returned by
			# the XML-RPC, but the GUI isn't adjusted yet
			if obj != None:
				obj.set_text(val)
			else:
				print "Stats for '"+ field +"' can't be displayed. No label in GUI."
		self.nodes[index].last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.__update_status_bar('Last Refresh of Node ' + str(self.nodes[index].node_number) +': ' + self.nodes[index].last_refresh)

	def __refresh_log(self, log, index):
		'''Fills GUI element with log file data'''
		self.__update_textbox(self.nodes[index].builder.get_object("txt_log"), log)

	def __update_textbox(self, obj, text):
		'''Helper to disable text field, update text and re-enable'''		
		obj.set_sensitive(False)		
		buf = obj.get_buffer()
		buf.set_text(text)
		buf.set_modified(False)
		itr = buf.get_end_iter()
		obj.scroll_to_iter(itr, 0.0, False, 0, 0)
		obj.set_sensitive(True)
	
	def __update_status_bar(self, status):
		'''Helper to update status bar'''
		self.statusbar.pop(self.statusbar_cid)
		self.statusbar.push(self.statusbar_cid, status)

	def __node_exists(self, host):
		for node in self.nodes:
			if node.host == host:
				return node.node_number
		return -1

	def main(self):
		'''Init GUI-Window'''
		self.window.show()
		gtk.main()

if __name__ == '__main__':
	gui = UnisonoGUI()
	gui.main()

