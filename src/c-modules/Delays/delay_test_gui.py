'''
delay_test.py

 Created on: July 14, 2009
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

'''
This script is only for testing purposes. It is used to test the PathMTU M&M
without UNISONO running.
'''
import sys
import gtk
from ctypes import *
from os import path, getcwd

class DelaysRequest(Structure):
    '''
    Request structure for the Delays module
    '''
    _fields_ = [('identifier1', c_char_p),
                ('identifier2', c_char_p)]

class DelaysResult(Structure):
    '''
    Result structure for the Delays module
    '''
    _fields_ = [('HOPCOUNT', c_int),
                ('RTT', c_int),
                ('RTT_MIN', c_int),
                ('RTT_MAX', c_int),
                ('RTT_DEVIATION', c_int),
                ('RTT_JITTER', c_int),
                ('OWD', c_int),
                ('OWD_MIN', c_int),
                ('OWD_MAX', c_int),
                ('OWD_DEVIATION', c_int),
                ('OWD_JITTER', c_int),
                ('LOSSRATE', c_int),
                ('error', c_int),
                ('errortext', c_char_p)]

class DelayTester:
 	'''
	GUI-class that runs tests on Delays-module
	'''
	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()
     
	def on_btn_go_clicked(self, widget, data=None):
		self.run_tests()

	def __init__(self):
		'''Prepare Data for GUI and Tests'''		
		builder = gtk.Builder()
		builder.add_from_file("delay_test.xml") 

		self.window = builder.get_object("window")
		self.textview_log = builder.get_object("textview_log")
		self.txt_ip_from = builder.get_object("txt_ip_from")
		self.txt_ip_to = builder.get_object("txt_ip_to")
		builder.connect_signals(self)   

		# load Delays-module
		print(path.join(getcwd(),'libDelays.so'))
		cdll.LoadLibrary(path.join(getcwd(),'libDelays.so'))
		self.libmodule = CDLL(path.join(getcwd(),'libDelays.so'))
		self.libmodule.measure.restype = DelaysResult		
		# some default IPs
		self.txt_ip_from.set_text('127.0.0.1')
		self.txt_ip_to.set_text('209.85.135.99') # Google

	def run_tests(self):
		'''Runs tests on Delays-module using IPs from textfields in GUI'''		
		req = DelaysRequest()
		req.identifier1 = c_char_p(self.txt_ip_from.get_text())
		req.identifier2 = c_char_p(self.txt_ip_to.get_text())
		result = self.libmodule.measure(req)
		text = ''
		for i in result._fields_:
			text = text + str(i[0]) + ': ' + str(getattr(result,i[0])) + '\n'

		# output results
		buff = self.textview_log.get_buffer()
		buff.set_text(text)
		buff.set_modified(False)

	def main(self):
		'''Init GUI-Window'''
		self.window.show()
		gtk.main()

if __name__ == "__main__":
	editor = DelayTester()
	editor.main()
