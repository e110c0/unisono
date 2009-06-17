CC = gcc
CFLAGS = -g -O2 -std=gnu99 -Wall -pedantic
LD = /usr/bin/ld
LDFLAGS = 

LINK_TARGET = libDelays.so
INSTALL_DIR = ../../unisono/mmplugins/

OBJS =  \
	mathfunctions.o \
	networkfunctions.o \
	Delays.o

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
