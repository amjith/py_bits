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
debug_ = 0

def debug_log( string, var):
	global debug_
	if debug_:
		print >>log, string, var

class CmdLineParser:
	"Command Line parser."

	def __init__(self,arguments):
		self.argv = arguments
		self.inpFile = self.outFile = None

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
				global debug_
				debug_ = 1
			elif opt in ("-o", "--output"): 
				self.outFile = arg
				debug_log( "Output File:",self.outFile )
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
			debug_log( "Input File:",self.inpFile)
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

	def __init__(self, debug=False, EC = []):
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

		self.Trend  = []
		self.Series = []
		self.DieXY = ()
		self.MaxLines = 0
		self.TestStat = {}

		if EC:
			self.EC= EC
		else:
			self.EC= ['*', '1','2','3','4','5','6','7','8','9']
		debug_log("EC:",self.EC)

	def TrendSeriesParser(self, inpFile):
		try:
			inp_file = open(inpFile, 'r')
		except IOError:
			print >>err,'Cannot open input file:', inpFile
			sys.exit(2)

		for line in inp_file:
			if self.reTrend.search(line):       # Trend Def match
				TrendMatch = self.reTrend.search(line)
				self.Trend.append(TrendMatch.groups()[0])
				debug_log("Append Trend:",TrendMatch.groups()[0])
			elif self.reSeries.search(line):    # Series Def match
				SeriesMatch = self.reSeries.search(line)
				self.Series.append(SeriesMatch.groups()[0])
				debug_log("Append Series:",SeriesMatch.groups()[0])
			elif self.reFlowStart.search(line): # Flow started no more trends/series
				inp_file.close();
				break;


	def FindDie(self, inpFile, max = True, EC = []):
		if not EC:
			EC = self.EC	
		try:
			inp_file = open(inpFile, 'r')
		except IOError:
			print >>err,'Cannot open input file:', inpFile
			sys.exit(2)
		
		flowOn = False
		DutLineCount = 0
		
		for line in inp_file:
			if flowOn:
				DutLineCount += 1
				if self.reDutXY.search(line):
					DutMatch = self.reDutXY.search(line)
					DutXY = (DutMatch.groups()[0], DutMatch.groups()[1])
					debug_log("Current die:",DutXY)
				elif self.reBinLine.search(line):
					BinMatch = self.reBinLine.search(line)
					flowOn = False
					if DutLineCount > self.MaxLines and BinMatch.groups()[1] in self.EC:
						self.MaxLines = DutLineCount
						self.DieXY = DutXY
						debug_log("New Max die found:",self.DieXY)
					if not max: # if max is False, then break the loop at the first match
						break
			elif self.reFlowStart.search(line):
				DutLineCount = 0
				flowOn = True
		debug_log("Chosen die:",self.DieXY)


	def ParseDie(self, inpFile, X, Y):
		try:
			inp_file = open(inpFile, 'r')
		except IOError:
			print >>err,'Cannot open input file:', inpFile
			sys.exit(2)
		
		testHeader = False
		flowOn = False
		TestName = "Header"
		self.TestStat[TestName] = [ 0, 0, 0 ]

		for line in inp_file:
			if flowOn:
				DutLineCount += 1
				if self.reDutXY.search(line):
					DutMatch = self.reDutXY.search(line)
					DutXY = (DutMatch.groups()[0], DutMatch.groups()[1])
					debug_log("Dut XY:",DutXY)
					if  DutXY != (X,Y):
						debug_log("Not the chosen die",None)
						flowOn = False
						TestName = "Header"
						self.TestStat[TestName] = [ 0, 0, 0 ]
				elif self.reBinLine.search(line):
					debug_log("Bin Line", None)
					break
				elif self.reTestStart.search(line):
					testHeader = True
					debug_log("First Test Header",None)
				elif testHeader and self.reTestName.search(line):
					TestName = self.reTestName.search(line).group()[0]
					self.TestStat[TestName] = [ 0, 0, 0 ]
					debug_log("TestName:", TestName)
				elif testHeader and self.reTestStart.search(line):
					testHeader = False
					debug_log("Second Test Header",None)
				elif self.reFirstWord.search(line):
					self.TestStat[TestName][0] += 1
					if self.reFirstWord.search(line).groups()[0] in self.Trend:
						self.TestStat[TestName][1] += 1
					elif self.reFirstWord.search(line).groups()[0] in self.Series:
						self.TestStat[TestName][2] += 1
					debug_log("TestStat:",self.TestStat[TestName])
			elif self.reFlowStart.search(line):
				DutLineCount = 0
				flowOn = True
				debug_log("TestFlow Start",None)

		
	def PrintResults(self):
		print "Number of Trends:", len(self.Trend)
		print "Number of Series:", len(self.Series)
		print "Max Die         :", self.DieXY
		print "Max Lines       :", self.MaxLines


	

def main(argv):
	cmdLine = CmdLineParser(argv)
	cmdLine.parser()
	#cmdLine.print_args()

	dlog = Datalog()
	dlog.TrendSeriesParser(cmdLine.inpFile)
	dlog.FindDie(cmdLine.inpFile)
	dlog.ParseDie(cmdLine.inpFile, dlog.DieXY[0], dlog.DieXY[1])
	dlog.PrintResults()
	

if __name__ == "__main__":
	main(sys.argv[1:])

