test:
	python masersim.py /dev/ttyUSB0 9600 &
	python3 masermon.py efosb &

run:
	python3 masermon.py efosb &

clean:
	rm -f *.pyc *~
