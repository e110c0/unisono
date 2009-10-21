import unittest
import unisono.mission_control
import queue
import time

class MissionControlTest(unittest.TestCase):
    def testInternalConnection(self):
        '''a test message should be send locally'''
        msgout = "this is a test"
        senderID = "module1"
        receiverID = "module2"
        destIP = "127.0.0.1"
        destPort = -1
        mc1 = unisono.mission_control.MissionControl()
        # direct send
#        mc2.send(sender, receiver, msgout)
        ##
        # indirect send
        senderQueue = queue.Queue()
        receiverQueue = queue.Queue()
        mc1.register(senderID, senderQueue)
        mc1.register(receiverID, receiverQueue)
        mc1.put(senderID,receiverID,msgout,destIP,destPort)
        ##
        while True:
            data = mc1.get(senderID)
            msgin = data[1]
            print("message",msgin,"from",data[2],data[3])
            if msgin != "":
                break;
            print ("rescan in 5 seconds")
            time.sleep(5)
        print (msgout,msgin)
        self.assertEqual(msgout,msgin)

        msgout = "2nd test"
        mc1.put(receiverID,senderID,msgout,destIP,destPort)
        while True:
            data = mc1.get(receiverID)
            msgin = data[1]
            print("message",msgin,"from",data[2],data[3])
            if msgin != "":
                break;
            print ("rescan in 5 seconds")
            time.sleep(5)
        print (msgout,msgin)
        self.assertEqual(msgout,msgin)
        mc1.stop()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(MissionControlTest("testInternalConnection"))

    return suite
