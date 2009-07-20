#!/usr/bin/env python
'''
svn-demo.py

 Created on: Jun 03, 2009
 Authors: dh

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
import pygtk
pygtk.require('2.0')
import gtk

class DemoWindow:
    def add_buttons(self):

        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_spacing(20)

        # Create a bunch of buttons
        button = gtk.Button(stock=gtk.STOCK_CLOSE)
        button.connect("clicked", self.delete)
        bbox.add(button)
#        table.attach(button, 0,1,1,2 , yoptions=gtk.EXPAND)
#        button.show()

        button = gtk.Button(stock=gtk.STOCK_GO_BACK)
        button.connect("clicked", lambda w: self.notebook.prev_page())
        bbox.add(button)
#        table.attach(button, 1,2,1,2,yoptions=gtk.EXPAND)
#        button.show()

        button = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        button.connect("clicked", lambda w: self.notebook.next_page())
        bbox.add(button)
#        table.attach(button, 2,3,1,2,yoptions=gtk.EXPAND)
#        button.show()

        button = gtk.Button(stock=gtk.STOCK_REFRESH)
        bbox.add(button)
#        table.attach(button, 3,4,1,2,yoptions=gtk.EXPAND)
#        button.show()
#        bbox.show()
        return bbox
    def add_notebook(self):
        # Create a new notebook, place the position of the tabs
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_LEFT)
        notebook.show()
        self.show_tabs = True
        self.show_border = True

        # Let's append a bunch of pages to the notebook
        for i in range(5):
            frame = self.layout_notebook_page(i)
            label = gtk.Label("Node %d" % (i))
            notebook.append_page(frame, label)

    
        # Set what page to start at (node 1)
        notebook.set_current_page(0)
        return notebook

    # Remove a page from the notebook
    def remove_book(self, button, notebook):
        page = notebook.get_current_page()
        notebook.remove_page(page)
        # Need to refresh the widget -- 
        # This forces the widget to redraw itself.
        notebook.queue_draw_area(0,0,-1,-1)

    def layout_notebook_page(self, no):
        bufferf = "UNISONO @ Node %d" % (no)

        frame = gtk.Frame(bufferf)
        frame.set_border_width(10)
        frame.set_label_align(1.0, 0.5)
        frame.set_size_request(800, 600)
        frame.show()
        table = gtk.Table(3, 3, True)
        table.set_row_spacings(10)
        table.set_col_spacings(10)
        vbox = gtk.VBox(False,0)
        table.attach(vbox,0,1,0,3)
        # IPs
        ipframe = gtk.Frame("Identifiers")
        ipview = gtk.TextView()
        ipview.set_editable(False)
        ipbuffer = ipview.get_buffer()
        # Load the file textview-basic.py into the text window
        infile = open("ip.txt", "r")

        if infile:
            string = infile.read()
            infile.close()
            ipbuffer.set_text(string)
        ipframe.add(ipview)
        # connectors
        conframe = gtk.Frame("Connectors")
        conview = gtk.TextView()
        conview.set_editable(False)
        conbuffer = conview.get_buffer()
        # Load the file textview-basic.py into the text window
        infile = open("con.txt", "r")

        if infile:
            string = infile.read()
            infile.close()
            conbuffer.set_text(string)
        conframe.add(conview)
        # global stats
        gsframe = gtk.Frame("Global Statistics")
        gstable = gtk.Table(2,3)
        gstable.set_row_spacings(5)
        gstable.set_col_spacings(5)
        label = gtk.Label('# Requests')
        gstable.attach(label,0,1,0,1)
        label = gtk.Label('100')
        gstable.attach(label,1,2,0,1)

        label = gtk.Label('# Aggregations')
        gstable.attach(label,0,1,1,2)
        label = gtk.Label('17')
        gstable.attach(label,1,2,1,2)

        label = gtk.Label('# from Cache')
        gstable.attach(label,0,1,2,3)
        label = gtk.Label('32')
        gstable.attach(label,1,2,2,3)
        gsframe.add(gstable)
        # current stats
        csframe = gtk.Frame("Current Statistics")
        cstable = gtk.Table(2,3)
        cstable.set_row_spacings(5)
        cstable.set_col_spacings(5)
        label = gtk.Label('# active Requests')
        cstable.attach(label,0,1,0,1)
        label = gtk.Label('12')
        cstable.attach(label,1,2,0,1)

        label = gtk.Label('# queued Requests')
        cstable.attach(label,0,1,1,2)
        label = gtk.Label('8')
        cstable.attach(label,1,2,1,2)

        label = gtk.Label('# aggregated Requests')
        cstable.attach(label,0,1,2,3)
        label = gtk.Label('2')
        cstable.attach(label,1,2,2,3)
        csframe.add(cstable)

        # db stats
        dbframe = gtk.Frame("Database Statistics")
        dbtable = gtk.Table(2,4)
        dbtable.set_row_spacings(5)
        dbtable.set_col_spacings(5)
        label = gtk.Label('Size')
        dbtable.attach(label,0,1,0,1)
        label = gtk.Label('1.874.548')
        dbtable.attach(label,1,2,0,1)

        label = gtk.Label('# Entries')
        dbtable.attach(label,0,1,1,2)
        label = gtk.Label('3532')
        dbtable.attach(label,1,2,1,2)

        label = gtk.Label('Oldest Entry')
        dbtable.attach(label,0,1,2,3)
        label = gtk.Label('2009-06-04 14:59:46')
        dbtable.attach(label,1,2,2,3)

        label = gtk.Label('Last Purge')
        dbtable.attach(label,0,1,3,4)
        label = gtk.Label('2009-06-04 15:00:03')
        dbtable.attach(label,1,2,3,4)

        dbframe.add(dbtable)

        # unisono stats
        uframe = gtk.Frame("UNISONO Statistics")
        utable = gtk.Table(2,4)
        utable.set_row_spacings(5)
        utable.set_col_spacings(5)
        label = gtk.Label('Start time')
        utable.attach(label,0,1,0,1)
        label = gtk.Label('2009-06-04 14:32:11')
        utable.attach(label,1,2,0,1)

        label = gtk.Label('Memory Usage')
        utable.attach(label,0,1,1,2)
        label = gtk.Label('71.788')
        utable.attach(label,1,2,1,2)

        label = gtk.Label('CPU Usage')
        utable.attach(label,0,1,2,3)
        label = gtk.Label('0.11')
        utable.attach(label,1,2,2,3)

        uframe.add(utable)


        vbox.pack_start(ipframe,expand=False, fill=False, padding=5)
        vbox.pack_start(conframe,expand=False, fill=False, padding=5)
        vbox.pack_start(gsframe,expand=False, fill=False, padding=5)
        vbox.pack_start(csframe,expand=False, fill=False, padding=5)
        vbox.pack_start(dbframe,expand=False, fill=False, padding=5)
        vbox.pack_start(uframe,expand=False, fill=False, padding=5)
        
        # known nodes graph
        switchbook = gtk.Notebook()
        switchbook.set_tab_pos(gtk.POS_TOP)
        switchbook.show()

        gframe = gtk.Frame()
        label = gtk.Label("Network View")
        gframe.set_size_request(0, 400)
        garea = gtk.DrawingArea()
        gframe.add(garea)
        gframe.show()
        switchbook.append_page(gframe, label)
        # and the other tabs
        

        switchbook.append_page(gtk.Frame(), gtk.Label('Database View'))
        switchbook.append_page(gtk.Frame(), gtk.Label('Measurement View'))

        table.attach(switchbook,1,3,0,2)
        
        switchbook.set_current_page(0)
        # log file
        logframe = gtk.Frame("Logfile")
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textview.set_editable(False)
        textbuffer = textview.get_buffer()
        # Load the file textview-basic.py into the text window
        infile = open("/home/dh/unisono.log", "r")

        if infile:
            string = infile.read()
            infile.close()
            textbuffer.set_text(string)

        
        
        sw.add(textview)
        logframe.add(sw)
        logframe.show()
        sw.show()
        textview.show()
        table.attach(logframe,1,3,2,3)


        table.show()
        frame.add(table)
        return frame

    
    def delete(self, widget, event=None):
        gtk.main_quit()
        return False

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # Set the window title
        window.set_title("SpoVNet Demonstrator: TP2")

        window.connect("delete_event", self.delete)
        window.set_border_width(10)

#        table = gtk.Table(2,4,False)
#        window.add(table)
#

#
#        
        mainbox = gtk.VBox(False, 0)
        mainbox.set_border_width(10)
        self.notebook = self.add_notebook()
        mainbox.pack_start(self.notebook,expand=True, fill=True, padding=0)
        mainbox.pack_start(self.add_buttons(),expand=False, fill=False, padding=0)
        window.add(mainbox)
        self.layout_notebook_page(self.notebook.get_current_page())
        window.show_all()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    DemoWindow()
    main()

