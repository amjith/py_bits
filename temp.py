#! /usr/bin/python
import sys
import getopt
import re

def main(argv):
	inp_file = argv[0]
	print inp_file
	inf = open(inp_file, 'r')
	i = 0
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


	line = True
	line1 = True

	while line:
		line = inf.readline()
		i+=1
		print i, line,

		#match = trend.search(line)
		#if match:
		if trend.search(line):
			match = trend.search(line)
			print "***TREND:", match.groups()[0]
	
		match = series.search(line)
		if match:
			print "***SERIES:", match.groups()[0]

		match = start_flow.search(line)
		if match:
			print "***START_FLOW"
		match = end_flow.search(line)
		if match:
			print "***END_FLOW"

		match = bin_line.search(line)
		if match:
			print "***BIN_LINE", match.groups()[0], match.groups()[1]

		match = dut_xy.search(line)
		if match:
			print "***DUT_XY", match.groups()[0], match.groups()[1]

		match = test_start.search(line)
		if match:
			print "***TEST_START"
			
if __name__ == "__main__":
	main(sys.argv[1:])
