= Requirements =

 * libiw
 * python3

= Installation =

to install UNISONO, run:

	cd src
	python3 setup.py install


to create html documentation, run:

	cd doc
	pydoc -w ../src


If you want to run UNISONO without installing it, you have to compile the M&Ms
written in C. To do so, just run:

	cd src
	python3 setup.py build_ext --inplace
	
This will install the .so-files into the correct directory in src. You can
run UNISONO now via:

	cd src
	python3 unisono-startup



