
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
from operator import itemgetter

err = sys.stderr
_debug = 0
log = sys.stdout
outf = sys.stdout

def debug_log(string, var):
	if _debug:
		print >>log, string, var

class Datalog:
	"A datalog class that parses and stores various statistics about the datalog"

	def __init__(self):


	_reTrend = re.compile(r"""
			^			# anchor the beginning
			\s*			# leading optional space
			TREND_DEF	# TREND_DEF string
			\s*			# optional space in between
			(\S+)		# non-space characters - Trend name
			""", re.VERBOSE)

	_reSeries = re.compile(r"""
			^			# anchor the beginning
			\s*			# leading optional space
			SERIES_DEF	# SERIES_DEF string
			\s*			# optional space in between
			(\S+)		# non-space characters - Series name
			""", re.VERBOSE)
	_reFlowStart = re.compile(r"""
			^\s*{\s*$	# A line that only has "{" and some space
			""",re.VERBOSE)
	_reFlowEnd = re.compile(r"""
			^\s*}\s*$	# A line that only has "}" and some space
			""", re.VERBOSE)

	_reBinLine = re.compile(r"""
			^			   # Begining of line
			\s*			   # Optional space
			Bin\sResults   # Bin Results
			\s*			   # Optional space
			\((\S)\)	   # (non_space_char) inside paranthesis
			\s*			   # Optional space
			\((\S)\)	   # (non_space_char) inside paranthesis
			""", re.VERBOSE)

	_reTestStart = re.compile(r""" 
			^
			\+
			=+
			\+		# A line with +=======...=====+
			\s*
			""", re.VERBOSE)

	_reTestName = re.compile(r"""
			^\|\s*(\S+)
			""", re.VERBOSE)

	_reFirstWord = re.compile(r"""
			^(\S+)
			""", re.VERBOSE)

	_reDutXY =  re.compile(r""" 
			\(X,Y\)=\((\d+),(\d+)\)  # Match (X,Y)=(\num,\num) 
			""", re.VERBOSE)

	_Trend
	_Series





if __name__ == "__main__":
	main(sys.argv[1:])
