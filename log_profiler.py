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
_debug = 1
log = sys.stdout
#test_stat = {}
#test_name = "Header"

def usage():
	print >>err, __doc__


def reset(test_stat, test_name):
	#print "Reset()"
	test_stat = {} # Reset the dictionary
	test_name = "Header" # test_name is reset to header
	test_stat[test_name] = [0,0,0] # Create a dictionary item for header
	return test_stat, test_name

def debug_log(string, var):
	if _debug:
		print >>log, string, var


def main(argv):                          

	outf = sys.stdout
	inp_file = None
	test_stat = {}
	test_name = "Header"
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
			debug_log( "Output File:",arg)
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
			debug_log( "Input File:",inp_file)

	EC_bin = ['*', 1,2,3,4,5,6,7,8,9]

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

	testname = re.compile(r"""
			^\|\s*(\S+)
			""", re.VERBOSE)

	first_word = re.compile(r"""
			^(\S+)
			""", re.VERBOSE)

	dut_xy =  re.compile(r""" 
			\(X,Y\)=\((\d+),(\d+)\)  # Match (X,Y)=(\num,\num) 
			""", re.VERBOSE)

	trend_name = []
	series_name = []

	line = dlog.readline()
	done = False
	while line:
		num_lines = 0
		# Look for Trends and Series Registers
		if trend.search(line):
			match = trend.search(line)
			trend_name.append(match.groups()[0])
			debug_log( "Trend appended:", trend_name[-1])
		elif series.search(line):
			match = series.search(line)
			series_name.append(match.groups()[0])
			debug_log( "Series appended:", series_name[-1])
		elif start_flow.search(line):
			#match = start_flow.search(line)
			test_stat, test_name = reset(test_stat, test_name)
			line = dlog.readline() # Read the first line in the flow
			num_lines += 1
			debug_log( "num_lines:", num_lines)
			while line:
				test_stat[test_name][0] += 1 # Increment the first element in list
				if test_start.search(line): # +===...===+
					debug_log("test_start",0)
					line = dlog.readline()  # Next line
					if testname.search(line): # Look for test_name
						test_name = testname.search(line).groups()[0] # | TESTNAME
						debug_log( "Test Name:", test_name)
					dlog.readline() # Throw away +===...===+
					test_stat[test_name] = [0,0,0] # New key added and stats initialized
					debug_log( "test_stat initialized:",test_stat[test_name])
				elif bin_line.search(line):
					match = bin_line.search(line)
					debug_log("Bin line:",match.groups())
					if match.groups()[1] in EC_bin:  # If second char matches something in EC_bin then full-flow
						debug_log("Full Flow Pass:",1)
						done = True
						break
					else:
						debug_log("Full Flow Fail:",0)
						test_stat, test_name = reset(test_stat, test_name)
						break
				else:
					match = first_word.search(line)
					if match and match.groups()[0] in trend_name: # if first word is a trend
						test_stat[test_name][1] += 1
						debug_log("Line is a Trend. Trend Count:",test_stat[test_name][1])
					elif match and match.groups()[0] in series_name: # if first word is a series
						test_stat[test_name][2] += 1
						debug_log("Line is a Series. Series Count:",test_stat[test_name][2])

				line = dlog.readline() # Read next line in flow
				num_lines += 1
		if done:
			debug_log("Success:",1)
			break
		line = dlog.readline() # Read next line in dlog

	print "Total number of line:",num_lines 



if __name__ == "__main__":
	main(sys.argv[1:])

