#! /usr/bin/python

"""Datalog Profiler:
Profiles the datalog to print some statistics about the datalog size of different tests.

Usage: 
log_profiler.py [options] file_name

Options:
	-o ..., --output=...    redirect the output of this script to a file
	-h, --help              show this help
	-d                      show debugging information

Examples:
	log_profiler 1254842127.6816292.0.6292-04.FPP.00.B63A.W26S.log:0                 generates the statistics for the datalog
	log_profiler 1254842127.6816292.0.6292-04.FPP.00.B63A.W26S.log:0 -o profile.txt  generates the statistics and writes them to the file profile.txt
"""

__author__ = "Amjith Ramanujam (amjidanutpan@imftech.com)"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2009/10/06 $"
__copyright__ = "(c) 2006-2009 IMFlash Technologies, Inc."


import sys
import getopt
import re


err = sys.stderr
_debug = 0
log = sys.stdout

def usage():
	print >>err, __doc__

def main(argv):                          
	outf = sys.stdout
	inp_file = None
	try:                                
		opts, args = getopt.getopt(argv, "ho:d ",["help","output="])
	except getopt.GetoptError, error_string:          
		print str(error_string);
		usage() 
		sys.exit(2)
	for opt, arg in opts:                
		if opt in ("-h", "--help"):      
			usage()
			sys.exit()
		elif opt == '-d':                
			global _debug
			_debug = 1
		elif opt in ("-o", "--output"): 
			if (_debug):
				print >>log, "Output File:",arg
			try:
				outf = open(arg, 'w')
			except IOError:
				print >>err,'cannot open output file:', arg
		
	if (not args):  # If no arguments are left then no input file is specified
		print >>err, "Missing input arguement: Input file"
		usage()
		sys.exit(2)
	else: 
		inp_file = args[0]  # Get the first argument as the input file, if more files are specified, ignore others
		dlog = open(inp_file, 'r')
		if (_debug):
			print >>log, "Input File:",inp_file

	trend = re.compile(r"""
			^			# anchor the beginning
			\s*			# leading optional space
			TREND_DEF	# TREND_DEF string
			\s*			# optional space in between
			(\S+)		# non-space characters - Trend name
			""", re.VERBOSE)

	series = re.compile(r"""
			^			# anchor the beginning
			\s*			# leading optional space
			SERIES_DEF	# SERIES_DEF string
			\s*			# optional space in between
			(\S+)		# non-space characters - Series name
			""", re.VERBOSE)
	start_flow = re.compile(r"""
			^\s*{\s*$	# A line that only has "{" and some space
			""",re.VERBOSE)
	end_flow = re.compile(r"""
			^\s*}\s*$	# A line that only has "}" and some space
			""", re.VERBOSE)

	bin_line = re.compile(r"""
			^			   # Begining of line
			\s*			   # Optional space
			Bin\sResults   # Bin Results
			\s*			   # Optional space
			\((\S)\)	   # (non_space_char) inside paranthesis
			\s*			   # Optional space
			\((\S)\)	   # (non_space_char) inside paranthesis
			""", re.VERBOSE)

	test_start = re.compile(r""" 
			^
			\+
			=+
			\+		# A line with +=======...=====+
			\s*
			""", re.VERBOSE)

	dut_xy =  re.compile(r""" 
			\(X,Y\)=\((\d+),(\d+)\)  # Match (X,Y)=(\num,\num) 
			""", re.VERBOSE)

	trend_names = []
	while True:
		line = inf.readline()
		if not line:
			break
		# Look for Trends and Series Registers
		if trend.search(line):
			match = trend.search(line)
			trend_name.append(match.group[0])
		elif series.search(line):
			match = series.search(line)
			series_name.append(match.group[0])
			






if __name__ == "__main__":
	main(sys.argv[1:])

