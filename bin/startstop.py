#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from subprocess import call
import sys

scriptpath = '/home/pi/development/icinga-flashlight/bin/blinkdingsdo.py'
# Kommandozeilenparameter abfangen
if __name__ == "__main__":
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			call([scriptpath, "start"])
		elif 'stop' == sys.argv[1]:
			call([scriptpath, "stop"])
		elif 'restart' == sys.argv[1]:
			call([scriptpath, "restart"])
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
