# jeremy@emperorlinux.com
# haage@net.in.tum.de

NAME  = pyiw
GCC   = gcc -Wall
FLAGS = -I/usr/include/python3.1
LIBS  = -liw

INSTALL_DIR = ../../unisono/utils

all: dynamic

dynamic: pyiw.c
	@echo "Dynamically Building/Linking $(NAME)"
	@$(GCC) $(FLAGS) $(LIBS) $(<) -shared -o $(NAME).so

static: pyiw.c
	@echo "Statically Building/Linking $(NAME)"
	@$(GCC) $(FLAGS) -Istaticlibiw $(<) -shared -o $(NAME).so /usr/lib/libiw.a

clean:
	@rm -rf *.o
	@rm -rf $(NAME).so
	@rm -rf $(NAME).so.t*

install:
	cp $(NAME).so $(INSTALL_DIR)
	echo Installed to $(INSTALL_DIR)
