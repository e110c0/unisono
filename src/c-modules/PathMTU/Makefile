CC = gcc
CFLAGS = -g -O2
LD = /usr/bin/ld
LDFLAGS = 

LINK_TARGET = libPathMTU.so
INSTALL_DIR = ../../unisono/trunk/src/unisono/mmplugins/

OBJS =  \
	networkfunctions.o \
	PathMTU.o

REBUILDABLES = $(OBJS) $(LINK_TARGET)

all : $(LINK_TARGET)
	echo All done

$(LINK_TARGET) : $(OBJS)
	$(CC) $(CFLAGS) -shared -Wl,-soname,$@ -o $@ $^

%.o : %.c
	$(CC) $(CFLAGS) -c -fPIC $< -o $@

clean : 
	rm -f $(REBUILDABLES)
	echo Clean done

install:
	cp $(LINK_TARGET) $(INSTALL_DIR)
	echo Installed to $(INSTALL_DIR)