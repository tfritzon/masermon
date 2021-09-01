test:
	python masersim.py /dev/ttyUSB0 9600 &
	python masermon.py /dev/ttyUSB1 9600

clean:
	rm -f *.pyc *~
