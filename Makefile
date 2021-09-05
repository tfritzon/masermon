test:
	python masersim.py /dev/ttyUSB0 9600 &
	python3 masermon.py maserdata /dev/ttyUSB1 9600

run:
	python3 masermon.py maserdata /dev/ttyUSB1 9600 &

clean:
	rm -f *.pyc *~
