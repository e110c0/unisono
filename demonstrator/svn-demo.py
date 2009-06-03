#!/usr/bin/env python
'''
svn-demo.py

 Created on: Jun 03, 2009
 Authors: dh

 $LastChangedBy: zxmoo46 $
 $LastChangedDate: 2009-05-28 21:37:23 +0200 (Thu, 28 May 2009) $
 $Revision: 1244 $

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

class DemoNotebook:

    # Remove a page from the notebook
    def remove_book(self, button, notebook):
        page = notebook.get_current_page()
        notebook.remove_page(page)
        # Need to refresh the widget -- 
        # This forces the widget to redraw itself.
        notebook.queue_draw_area(0,0,-1,-1)

    def delete(self, widget, event=None):
        gtk.main_quit()
        return False

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # Set the window title
        window.set_title("SpoVNet Demonstrator: TP2")


        window.connect("delete_event", self.delete)
        window.set_border_width(10)

        table = gtk.Table(2,4,False)
        window.add(table)

        # Create a new notebook, place the position of the tabs
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_LEFT)
        table.attach(notebook, 0,4,0,1,yoptions=gtk.FILL)
        notebook.show()
        self.show_tabs = True
        self.show_border = True

        # Let's append a bunch of pages to the notebook
        for i in range(5):
            bufferf = "UNISONO @ Node %d" % (i)
            bufferl = "Node %d" % (i)

            frame = gtk.Frame(bufferf)
            frame.set_border_width(10)
            frame.set_size_request(800, 600)
            frame.show()

            label = gtk.Label(bufferf)
            frame.add(label)
            label.show()

            label = gtk.Label(bufferl)
            notebook.append_page(frame, label)

    
        # Set what page to start at (node 1)
        notebook.set_current_page(0)

#        bbox = gtk.HButtonBox()
#        bbox.set_layout(gtk.BUTTONBOX_END)
#        bbox.set_spacing(20)
#        table.attach(bbox,0,6,1,2)#

        # Create a bunch of buttons
        button = gtk.Button(stock=gtk.STOCK_CLOSE)
        button.connect("clicked", self.delete)
#        bbox.add(button)
        table.attach(button, 0,1,1,2 , yoptions=gtk.EXPAND)
        button.show()

        button = gtk.Button(stock=gtk.STOCK_GO_BACK)
        button.connect("clicked", lambda w: notebook.next_page())
#        bbox.add(button)
        table.attach(button, 1,2,1,2,yoptions=gtk.EXPAND)
        button.show()

        button = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        button.connect("clicked", lambda w: notebook.prev_page())
#        bbox.add(button)
        table.attach(button, 2,3,1,2,yoptions=gtk.EXPAND)
        button.show()

        button = gtk.Button(stock=gtk.STOCK_REFRESH)
#        bbox.add(button)
        table.attach(button, 3,4,1,2,yoptions=gtk.EXPAND)
        button.show()
#        bbox.show()

        table.show()
        window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    DemoNotebook()
    main()

