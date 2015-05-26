#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys, time, socket, logging, signal
import RPi.GPIO as GPIO
from threading import Thread
from daemon import Daemon


def blinkdingsdo():
	HOST = ''   # Symbolic name meaning all available interfaces
	PORT = 8888 # Arbitrary non-privileged port
	logfile = '/var/log/blinkdingdo.log'
	logging.basicConfig(filename=logfile,format='%(asctime)s %(name)s %(levelname)s:%(message)s' ,level=logging.DEBUG)
	mylog = logging.getLogger("default")
	mylog.info("Beginn Log")
	#Function for handling connections. This will be used to create threads
	def clientthread(conn, addr):
		#Sending message to connected client
		conn.send('Wilkommen auf dem Server.\nFuer Hilfe bitte schreiend im Kreis herumrennen oder \'help\' eingeben.\n') #send only takes string

		#infinite loop so that function do not terminate and thread do not end.
		while True:

			#Receiving from client
			data = conn.recv(1024).strip()
			if data == 'help':
				reply = '''\
Blinkdingsdo v0.1

blink_on		Schaltet das Blinklicht an.
blink_off		Schaltet das Blinklicht aus.
alert			Löst einen Cordlessalarm aus.
weather			Zeigt den aktuellen Wetterbericht für ihre Region an.
quit			Beendet die Verbindung.
'''
			elif data == 'blink_on':
				# hier sollte das Blinken angeschaltet werden
				mylog.info('blink_on von ' + addr[0] + ':' + str(addr[1]))
				try:
					GPIO.remove_event_detect(12)
					GPIO.output(8, GPIO.HIGH)
					time.sleep(2)
					GPIO.add_event_detect(12, GPIO.FALLING, callback= switchoff2, bouncetime=200)
				except Exception as e:
					mylog.info(str(e))
				reply = 'Blinklicht eingeschaltet\n'
			elif data == 'blink_off':
				# hier sollte das Blinklicht ausgeschaltet werden
				mylog.info('blink_off von ' + addr[0] + ':' + str(addr[1]))
				GPIO.output(8, GPIO.LOW)
				reply = 'Blinklicht ausgeschaltet\n'
			elif data == 'alert':
				# hier sollte der Alarm ausgelöst werden
				alertthread = Thread(target=alert, args=(1,))
				alertthread.start()
				reply = 'Alarm ausgelöst\n'
			elif data == 'weather':
				reply = 'Seriously ????????????????????????\n'
			elif data == 'quit':
				conn.sendall('ByeBye\n')
				break
			else:
				reply = 'Sie chönts afacht nöd\n'
			conn.sendall(reply)
		mylog.warning('Disconnected with ' + addr[0] + ':' + str(addr[1]))
		conn.close()

	def alert(x):
		GPIO.output(10, GPIO.HIGH)
		mylog.info('alarm ausgeloest')
		time.sleep(2)
		GPIO.output(10, GPIO.LOW)
		
	def switchoff(x):
		while True:
			GPIO.wait_for_edge(12, GPIO.FALLING, bouncetime=200)
			mylog.info('Switch betaetigt')
			GPIO.output(8, GPIO.LOW)

	def switchoff2(channel):
		mylog.info('Switch betaetigt')
		GPIO.output(8, GPIO.LOW)
		
			
	def handler(signum, frame):
		mylog.info('Programm wird beendet')
		try:
			s.close()
			mylog.info('Socket geschlossen')
			GPIO.remove_event_detect(12)
			GPIO.output(8, GPIO.LOW)
			GPIO.output(10, GPIO.LOW)
			mylog.info('GPIOs zurueckgesetzt')
		except Exception as e:
			mylog.info(str(e))
		mylog.info("Ende Log")
		logging.shutdown()
		self.delpid()
		sys.exit(0)

	mylog.info('Beginn initialisierung')
	# RPi.GPIO Layout verwenden (wie Pin-Nummern)
	GPIO.setmode(GPIO.BOARD)
	# Pins auf Output setzen
	GPIO.setup(8, GPIO.OUT)
	GPIO.setup(10, GPIO.OUT)
	# Pins auf Input setzen und PullUp aktivieren
	GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	# Outputs auf Low setzen
	GPIO.output(8, GPIO.LOW)
	GPIO.output(10, GPIO.LOW)
	mylog.info('Initialisierung abgeschlossen')
	
	#signal.signal(signal.SIGTERM, handler)
	for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
		signal.signal(sig, handler)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mylog.info('Socket created')

	#Bind socket to local host and port
	try:
		s.bind((HOST, PORT))
	except socket.error as msg:
		mylog.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
	mylog.info('Socket bind complete')

	#Start listening on socket
	s.listen(10)
	mylog.info('Socket now listening')
	
	#thread01 = Thread(target=switchoff, args=(1,))
	#thread01.start()
	GPIO.add_event_detect(12, GPIO.FALLING, callback= switchoff2, bouncetime=200)
		
	# Loop
	while True:
		#wait to accept a connection - blocking call
		conn, addr = s.accept()
		mylog.info('Connected with ' + addr[0] + ':' + str(addr[1]))
		#start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
		x1 = Thread(target=clientthread, args=(conn, addr,))
		x1.start()


#########################################################################
# Klasse ueberschreiben
class MyDaemon(Daemon):
	def run(self):
			blinkdingsdo()
		
#########################################################################
# Kommandozeilenparameter abfangen
if __name__ == "__main__":
	daemon = MyDaemon('/tmp/daemon-example.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)

