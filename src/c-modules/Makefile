MODULES = PathMTU Delays libMeasure

all:
	for dir in $(MODULES); do \
		(cd $$dir; ${MAKE} all); \
	done

install:
	for dir in $(MODULES); do \
		(cd $$dir; ${MAKE} install); \
	done

clean:
	for dir in $(MODULES); do \
		(cd $$dir; ${MAKE} clean); \
	done
