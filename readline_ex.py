#! /usr/bin/python
import sys
import getopt
import re

def main(argv):
	inp_file = argv[0]
	print inp_file
	inf = open(inp_file, 'r')
	i = 0
	line = True
	line1 = True
	while line:
		line = inf.readline()
		print i, line,
		i+=1
		if i>4:
			while line1:
				line1 = inf.readline()
				print line1,
	

if __name__ == "__main__":
	main(sys.argv[1:])
