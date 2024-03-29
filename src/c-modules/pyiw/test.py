#!/usr/bin/env python

import sys
#import time
import pyiw

INTERFACE = "wlan0"

def PrintAllValues(iface):
    for val in iface:
        print("%-9s = %s" % (val, iface[val]))
    
if __name__ == "__main__":
    print("Using device:", INTERFACE, "\n")
    print("Version [ PyIW      ]:", pyiw.version())
    print("Version [ libiw/WE  ]:", pyiw.iw_version())
    print("Version [ kernel/WE ]:", pyiw.we_version(), "\n")

    try:
        iface = pyiw.WirelessInterface(INTERFACE)
        print("\n current settings \n")
        for i in iface:
            print(i, "-", iface[i])

        #iface["essid"]   = "01234567890123456789fasdfasdfas"
        #iface["channel"] = 1.0
        #print("\n settings after essid and channel set\n")
        #for i in iface:
            #print(i, "-", iface[i])

    except pyiw.error as error:
        print("Error:", error)

		#sys.exit(1)

    print("\nScanning...\n")

    for net in iface.Scan():
        print(net["essid"], "- WPA Active:", net["wpa"])

