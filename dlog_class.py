#! /usr/bin/python

"""Datalog Profiler:
Profiles the datalog to print some statistics about the datalog size of different tests.

Usage: 
log_profiler.py [options] file_name

Options:
	-o <filename>, --output=<filename>    Redirect the output of this script to a file
	-c, --csv                             Print the output in the csv format
	-m, --max                             Pick the die with maximum number of lines
	-x  x,y                               Specify the die's (x,y) location
	-e EC_BIN, --EC=EC_BIN				  Specify the EC_Bin to match when looking for a die
	-h, --help                            Show this help
	-D                                    Show debugging information


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
if (2,2) != sys.version_info[:2]:   # if Python version is 2.6
	import csv
	from operator import itemgetter

err = sys.stderr
log = sys.stdout
outf = sys.stdout
debug_ = 0

def debug_log( string, var):
	global debug_
	if debug_:
		print >>log, string, var

def dic_sort(dict,by_value=False, reverse=False):
    if by_value:
        items = [(v,k) for k,v in dict.items()] # make a list of tuples with (values, keys)
    else:
        items = dict.items()
    items.sort()
    if reverse:
        items.reverse()
    if by_value:
        items = [(k,v) for v, k in items] # swap (values,keys) -> (keys,values) 
    return items

class CmdLineParser:
	"Command Line parser."

	def __init__(self,arguments):
		self.argv = arguments
		self.inpFile = self.outFile = None
		self.csv = False
		self.max = False
		self.xy  = ()
		self.EC = []

	def usage(self, exit_code):
		print >>err, __doc__
		sys.exit(exit_code)


	def parser(self):
		try:
			opts, args = getopt.getopt(self.argv, "e:x:mho:Dc",["EC=","max","help","output=","csv"])
		except getopt.GetoptError, error_string:          
			print str(error_string);
			self.usage(2) 
		for opt, arg in opts: 
			if opt in ("-h", "--help"):      
				self.usage(0)
			elif opt == '-D':
				global debug_
				debug_ = 1
			elif opt == '-x':
				self.xy = tuple(arg.split(','))
			elif opt in ("-c","--csv"):
				self.csv = True
			elif opt in ("-m","--max"):
				self.max = True
			elif opt in ("-e", "--EC"): 
				self.EC = [arg]
			elif opt in ("-o", "--output"): 
				self.outFile = arg
				debug_log( "Output File:",self.outFile )
				try:
					out_fp = open(self.outFile, 'w')
				except IOError:
					print >>err,'Cannot open output file:', self.outFile
					sys.exit(2)
				global outf
				outf = out_fp
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
		print >>err, "Command Line Arguments:"
		print >>err, "inpFile:",self.inpFile
		print >>err, "outFile:",self.outFile
		print >>err, "csv:",self.csv
		print >>err, "max:",self.max
		print >>err, "die xy:",self.xy
		print >>err, "EC:",self.EC
		print >>err

class Datalog:
	"A datalog class that parses and stores various statistics about the datalog"

	def __init__(self, EC = []):
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
			   \d+   		# Numbers
			   \s*			# optional space in between
			   (\S+)        # Series def name
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
			   ^\s*(\S+)
			   """, re.VERBOSE)

		self.reDutXY =  re.compile(r""" 
			   \(X,Y\)=\((\d+),(\d+)\)  # Match (X,Y)=(\num,\num) 
			   """, re.VERBOSE)
		self.reDutA = re.compile(r"""
				^TESTER_SUB_SITE\s*(\d)
				""",re.VERBOSE)

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

		debug_log('FindDie inpFile:',inpFile)
		debug_log('FindDie max:',max)
		debug_log('FindDie EC:',EC)

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
					debug_log( 'Bin Line:',(BinMatch.groups()[0],BinMatch.groups()[1]))
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
		return self.DieXY


	def ParseDie(self, inpFile, X, Y):
		try:
			inp_file = open(inpFile, 'r')
		except IOError:
			print >>err,'Cannot open input file:', inpFile
			sys.exit(2)
		
		testHeader = False
		flowOn = False
		TestName = "Header"
		self.TestStat[TestName] = [ 0, 0, 0, 0 ]

		for line in inp_file:
			if flowOn:
				DutLineCount += 1
				if self.reDutXY.search(line):
					DutMatch = self.reDutXY.search(line)
					DutXY = (DutMatch.groups()[0], DutMatch.groups()[1])
					debug_log("Dut XY:",DutXY)
					if  DutXY != (X,Y):
						debug_log("Current die",DutXY)
						debug_log("Chosen die",(X,Y))
						debug_log("Not the chosen die",None)
						flowOn = False
						TestName = "Header"
						self.TestStat[TestName] = [ 0, 0, 0, 0]
				elif self.reBinLine.search(line): # Bin line 
					debug_log("Bin Line", None)
					break
				elif self.reTestStart.search(line): # First header line +=== ... ===+
					testHeader = not(testHeader)
					debug_log("Test Header",None)
				elif testHeader and self.reTestName.search(line): # Test Name, only after first header
					TestName = self.reTestName.search(line).groups()[0]
					self.TestStat[TestName] = [ 0, 0, 0, 0]
					debug_log("TestName:", TestName)
				elif self.reFirstWord.search(line): # A non-blank line
					self.TestStat[TestName][0] += 1
					if self.reFirstWord.search(line).groups()[0] in self.Trend:
						self.TestStat[TestName][1] += 1 # Trend Line
					elif self.reFirstWord.search(line).groups()[0] in self.Series:
						self.TestStat[TestName][2] += 1 # Series Line
					debug_log("TestStat:",self.TestStat[TestName])
				else:  # Blank line
					self.TestStat[TestName][0] += 1 # Total line count in test
					self.TestStat[TestName][3] += 1 # Blank line count
			elif self.reFlowStart.search(line):
				DutLineCount = 0
				flowOn = True
				debug_log("TestFlow Start",None)

		
	def PrintResults(self, csv_opt = False):
		if csv_opt:
			if (2,2) != sys.version_info[:2]:   # if Python version is 2.6
				csvFile = csv.writer(outf, delimiter=',')
				csvFile.writerow(['TestName','Trends','Series','Non-extractables','Total','Blank','Non-Blank'])
				for test, stat in sorted(self.TestStat.iteritems(),key=itemgetter(1),reverse=True):
					csvFile.writerow([test,stat[1],stat[2], stat[0]-stat[1]-stat[2],
						stat[0],stat[3],stat[0]-stat[3] ])
			else:
				print >>outf,'TestName,','Trends,','Series,','Non-extractables,','Total,','Blank,','Non-Blank'
				for test, stat in dic_sort(self.TestStat,by_value=True,reverse=True):
					print >>outf, test, ',',stat[1],',',stat[2],',', stat[0]-stat[1]-stat[2],',', stat[0],',',stat[3],',',stat[0]-stat[3]
		else:
			print >>outf, "Total Number of Trends:", len(self.Trend)
			print >>outf, "Total Number of Series:", len(self.Series)
			print >>outf, "Die         :", self.DieXY
			print >>outf, "Lines       :", self.MaxLines
			print >>outf 

			if (2,2) != sys.version_info[:2]:   # if Python version is 2.6
				for test, stat in sorted(self.TestStat.iteritems(),key=itemgetter(1),reverse=True):
					print >>outf,"+=====================================+"
					print >>outf,"|TestName:",test
					print >>outf,"+=====================================+"
					print >>outf,"Trends          :", stat[1]
					print >>outf,"Series          :", stat[2]
					print >>outf,"Non-extractables:", stat[0] - stat[1] - stat[2]
					print >>outf,"      ---------------"
					print >>outf,"Total Lines     :", stat[0], "   (Blanks:", stat[3], "Non-Blanks:", stat[0]-stat[3], ")"
					print >>outf,"      ---------------"
					print >>outf
			else:
				for test, stat in dic_sort(self.TestStat,by_value=True,reverse=True):
					print >>outf,"+=====================================+"
					print >>outf,"|TestName:",test
					print >>outf,"+=====================================+"
					print >>outf,"Trends          :", stat[1]
					print >>outf,"Series          :", stat[2]
					print >>outf,"Non-extractables:", stat[0] - stat[1] - stat[2]
					print >>outf,"      ---------------"
					print >>outf,"Total Lines     :", stat[0], "   (Blanks:", stat[3], "Non-Blanks:", stat[0]-stat[3], ")"
					print >>outf,"      ---------------"
					print >>outf
	

def main(argv):
	cmdLine = CmdLineParser(argv)
	cmdLine.parser()
	cmdLine.print_args()

	dlog = Datalog(cmdLine.EC)
	dlog.TrendSeriesParser(cmdLine.inpFile)
	if cmdLine.xy:
		dlog.ParseDie(cmdLine.inpFile, cmdLine.xy[0], cmdLine.xy[1])
		dlog.PrintResults(cmdLine.csv)
	elif dlog.FindDie(cmdLine.inpFile, cmdLine.max, cmdLine.EC):
		dlog.ParseDie(cmdLine.inpFile, dlog.DieXY[0], dlog.DieXY[1])
		dlog.PrintResults(cmdLine.csv)
	else:
		print "No die found in the datalog"
	

if __name__ == "__main__":
	main(sys.argv[1:])

