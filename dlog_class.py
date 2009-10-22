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
log = sys.stdout
outf = sys.stdout


class CmdLineParser:
	"Command Line parser."

	def __init__(self,arguments):
		self.argv = arguments
		self.inpFile = self.outFile = None
		self.debug = 0

	def debug_log(self, string, var):
		if self.debug:
			print >>log, string, var


	def usage(self, exit_code):
		print >>err, __doc__
		sys.exit(exit_code)


	def parser(self):
		try:
			opts, args = getopt.getopt(self.argv, "ho:d",["help","output="])
		except getopt.GetoptError, error_string:          
			print str(error_string);
			self.usage(2) 
		for opt, arg in opts: 
			if opt in ("-h", "--help"):      
				self.usage(0)
			elif opt == '-d':                
				self.debug = 1
			elif opt in ("-o", "--output"): 
				self.outFile = arg
				self.debug_log( "Output File:",self.outFile )
				try:
					out_fp = open(self.outFile, 'w')
				except IOError:
					print >>err,'Cannot open output file:', arg
					sys.exit(2)
				else:
					out_fp.close()

		if (not args): # If no args left after options, no inpfile
			print >>err, "Missing input arguement: Input file"
			self.usage(2)
		else: 
			self.inpFile = args[0]  # Get the first argument as the input file, if more files are specified, ignore others
			self.debug_log( "Input File:",self.inpFile)
			try:
				inp_fp = open(self.inpFile, 'r')
			except IOError:
				print >>err, 'Cannot open input file:', self.inpFile
				sys.exit(2)
			else:
				inp_fp.close()

	def print_args(self):
		print "inpFile:",self.inpFile
		print "outFile:",self.outFile
		print "debug  :",self.debug

class Datalog:
	"A datalog class that parses and stores various statistics about the datalog"

	def __init__(self):
		self.reTrend = re.compile(r"""
			   ^			# anchor the beginning
			   \s*			# leading optional space
			   TREND_DEF	# TREND_DEF string
			   \s*			# optional space in between
			   (\S+)		# non-space characters - Trend name
			   """, re.VERBOSE)

		self.reSeries = re.compile(r"""
			   ^			# anchor the beginning
			   \s*			# leading optional space
			   SERIES_DEF	# SERIES_DEF string
			   \s*			# optional space in between
			   (\S+)		# non-space characters - Series name
			   """, re.VERBOSE)
		self.reFlowStart = re.compile(r"""
			   ^\s*{\s*$	# A line that only has "{" and some space
			   """,re.VERBOSE)
		self.reFlowEnd = re.compile(r"""
			   ^\s*}\s*$	# A line that only has "}" and some space
			   """, re.VERBOSE)

		self.reBinLine = re.compile(r"""
			   ^			   # Begining of line
			   \s*			   # Optional space
			   Bin\sResults   # Bin Results
			   \s*			   # Optional space
			   \((\S)\)	   # (non_space_char) inside paranthesis
			   \s*			   # Optional space
			   \((\S)\)	   # (non_space_char) inside paranthesis
			   """, re.VERBOSE)

		self.reTestStart = re.compile(r""" 
			   ^
			   \+
			   =+
			   \+		# A line with +=======...=====+
			   \s*
			   """, re.VERBOSE)

		self.reTestName = re.compile(r"""
			   ^\|\s*(\S+)
			   """, re.VERBOSE)

		self.reFirstWord = re.compile(r"""
			   ^(\S+)
			   """, re.VERBOSE)

		self.reDutXY =  re.compile(r""" 
			   \(X,Y\)=\((\d+),(\d+)\)  # Match (X,Y)=(\num,\num) 
			   """, re.VERBOSE)

#	def TrendSeriesParser(self):
	

def main(argv):
	cmdLine = CmdLineParser(argv)
	cmdLine.parser()
	cmdLine.print_args()
	

if __name__ == "__main__":
	main(sys.argv[1:])

