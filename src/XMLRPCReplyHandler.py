'''
XMLRPCReplyHandler.py

 Created on: Mar 23, 2009
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
import threading

class XMLRPCReplyHandler:
    def run(self):
        '''
        get events from unisono and forward them to the corresponding connector
        '''

# Create server
replyhandler = XMLRPCReplyHandler()

# Start a thread with the server -- that thread will then start one
# more thread for each request
reply_thread = threading.Thread(target=replyhandler.run)
# Exit the server thread when the main thread terminates
reply_thread.setDaemon(True)
reply_thread.start()
print("XMLRPC reply handler loop running in thread:", reply_thread.name)