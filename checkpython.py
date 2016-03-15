#!/usr/bin/python
# Compile python, and do tabnanny check

import os
import sys
import py_compile
import tabnanny

def print_usage():
	""" Print usage for program """
	print 'usage: %s [PYTHON FILE] [PYTHON FILE] ...' % (sys.argv[0])
	print 'usage: %s --help' % (sys.argv[0])

# ============================================================================
# main
# expect at least one file to compile
# ============================================================================
def main():
	"""
	Can receive multiple arguments, all of which are assumed to be python
	files.
	Perform the following checks:
		1) Compile Python files
		2) Tabnanny Python files
	"""

	# get arguments
	if len(sys.argv) == 2 and sys.argv[1] == "--help":
		print_usage()
		sys.exit(0)
	elif len(sys.argv) < 2:
		print 'At least 2 arguments are required. Received: %d arguments' % len(sys.argv)
		print_usage()
		sys.exit(1)

	# check all files
	for index in range(1, len(sys.argv)):

		fileToCheck = sys.argv[index]

		# make sure the file exists
		if not os.path.exists(fileToCheck):
			print "Unable to find file %s!" % fileToCheck
			continue

		# compile the file
		print "compile %s...." % fileToCheck
		py_compile.compile(fileToCheck)

		# perform tab check on file
		print "tabnanny %s...." % fileToCheck
		tabnanny.check(fileToCheck)

# ============================================================================
# call main
# ============================================================================
if __name__ == '__main__':
	main()
