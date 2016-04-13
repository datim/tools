#!/usr/bin/python
#
###############################################################################################################
# simple script to backup a file or a directory structure to a timestamped location
#
# History:
# v1.0: Creation
# v1.4: Move backup to new class
# v1.5: Add ability to preserve directory structure
# v1.6: Make archived files read only, create Archive class
# v1.7: Add option to list archive directory contents
# v1.8: Add ability to only archive files that have been modified in subversion
# v1.9: List requested archived directories. Remove spaces from archive name

# To Do: Add Logger
# To Do: Add ability to backup subversion controlled files in specific sub directories
# To Do: Prune archive directories
# To Do: Add Debug Flag and Simulate/Test only flag
# To Do: Replace OptionParser with argparse library
###############################################################################################################

import sys
import os
import datetime
import getopt
import subprocess
import time
import re
from optparse import OptionParser

# OptionParser prog arguments
PROGRAM_NAME="archive" 
PROGRAM_VERSION = "1.9"

# get home directory
DEFAULT_BACKUP_DIR = os.path.join(os.path.expanduser('~'), "archive")

# files to ignore
ignore_list = [".svn"]

# -----------------------------------------------------
# Class SvnHandler
# -----------------------------------------------------
class SvnHandler(object):
	""" Handle SVN processing """

	SVN_MODIFIED_FILE_STATUS = ['A', 'M']

	# -----------------------------------------------------
	# __init__
	# -----------------------------------------------------
	def __init__(self):
		""" constructor """
		pass
		
	# -----------------------------------------------------
	# getModifiedSvnFiles
	# -----------------------------------------------------
	def getModifiedSvnFiles(self, debug=False):
		""" 
		Return a list of file files in the current directory
		path that are marked as modified in subversion.

		ARGS:
			debug: If true, enable debug printing

		RETURNS:
			A list constaining the absolute path to files (and optionally)
			directories that have been marked as modified in subversion
		"""

		# first get all svn file status
		svnFileStatusList = self.getSvnFileStatus(debug)

		# now sort out all those files that are modified
		modifiedFiles = []

		# get the current path

		for fileStatusTuple in svnFileStatusList:
		
			# check if the file is modified
			if fileStatusTuple[0] in self.SVN_MODIFIED_FILE_STATUS:

				# save the full path to this file
				fullFilePath = os.path.abspath(fileStatusTuple[1])

				# only back up files, not directories
				if not os.path.isdir(fullFilePath):
					modifiedFiles.append(fullFilePath)

				elif debug:
					print "Dont save directories: %s" % fullFilePath

			elif debug:
				print "file is not in an svn modified state %s:%s" % (fileStatusTuple[0], fileStatusTuple[1])

		return modifiedFiles

	# -----------------------------------------------------
	# getSvnFileStatus
	# -----------------------------------------------------
	def getSvnFileStatus(self, debug=False):
		""" 
		Get the file status for the current directory and 
		all sub directories

		RETURNS:
			A list containing tuple entries of svn status for each 
			file in the format (STATUS, path)
		"""

		returnList = []

		# execute svn query command
		cmd = ["svn status"]
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

		output, err = proc.communicate()
		rc = proc.returncode

		if rc != 0 or err:
			# if there was an error, dont continue processing
			print "error running command %s. Return code %d, errors: %s" % (cmd, rc, err)
			return returnList

		# seperate the output into individual lines
		output = output.split(os.linesep)

		# for each line, seperate out file status and place both items in a list
		for line in output:

			# look for lines with the format like "?      file/path"
			EXPRESSION = "^(.)\s+([^\s]+)"
			matchobj = re.match(EXPRESSION, line)

			if matchobj:
				# we found a match, seperate out the pieces and store in a list
				status = matchobj.group(1)
				path = matchobj.group(2)

				if debug:
					print "Successfully parsed file. Status %s, file %s" % (status, path)

				statusTuple = (status, path)
				returnList.append(statusTuple)

		# return the parsed output
		return returnList


# -----------------------------------------------------
# Class Archive
# -----------------------------------------------------
class Archive(object):
	"""
	Class defining archive tool
	"""

	# -----------------------------------------------------
	# __init__
	# -----------------------------------------------------
	def __init__(self):
		""" constructor """
		pass

	# -----------------------------------------------------
	# pruneArchiveDir
	# -----------------------------------------------------
	def pruneArchiveDir(self, pruneDate, archivePath):
		"""
		Prune the archive directory of folders that were 
		created before pruneDate

		ARGS:
			pruneDate: date to prune archive folders. Expected format is YYYY-MM-DD
			archivePath: root archive directory where sub directories will be removed

		RETURNS:
			Return true if directories attempted to be removed, false if there was
			an error
		"""

		# check input parameter
		if not os.path.exists(archivePath) or not os.path.isdir(archivePath):
			print "%s is not a directory or doesn't exist!" % archivePath
			return false

		if not pruneDate:
			print "no prune date specified!" 
			return false

		# validate that pruneDate is in the format YYYY-MM-DD
		pruneDateTime = None
		try:
			pruneDateTime = time.strptime(pruneDate, "%Y-%m-%d")
		except ValueError, e:
			print "Cannot convert %s to datetime. Expected format: YYYY-MM-DD" % pruneDate
			return false
		except Exception, e:
			print "Unexpected exception parsing prune date"
			print "Expected format for input %s is: YYYY-MM-DD" % pruneDate
			return false

		print "Valid date time specified" 

		# now that pruneDate is validated, gather a list of all sub directories that
		# preceed pruneDateTime
		candidateDirs = []


	# -----------------------------------------------------
	# listArchiveContents
	# -----------------------------------------------------
	def listArchiveContents(self, archiveDirList):
		""" for a list of directories, print out the contents """

		for dir in archiveDirList:
			self._listArchive(dir)
			
	# -----------------------------------------------------
	# listArchive
	# -----------------------------------------------------
	def _listArchive(self, archivePath):
		"""
		list the immediate directories and files in the archive directory
		archivePath. 

		ARGS:
			archivePath: archive path to be checked

		RETURNS:
			Prints out contents of archivePath, if it 
		"""

		print "Checking archive path %s " % archivePath

		# make sure the backup directory exists
		if not os.path.exists(archivePath):
			print "Archive path %s doesn't exist" % archivePath
			return
		
		# get immediate files and directories
		dirList = os.listdir(archivePath)

		if not dirList:
			# list is empty
			print "Archive dir %s is empty" % archivePath
			return

		# sort the results
		list.sort(dirList)

		for name in dirList:
			fullNamePath = os.path.join(archivePath, name)
			if os.path.isfile(fullNamePath):
				print "(file) %s" % fullNamePath
			else:
				print "(dir) %s" % fullNamePath
			
	# -----------------------------------------------------
	# createDirectory
	# -----------------------------------------------------
	def createDirectory(self, dir):
		"""
		Create directory if it doesn't exist

		ARGS:
			dir: directory to create
		"""

		if not os.path.exists(dir):
			print "creating directory ", dir
			os.makedirs(dir)

	# -----------------------------------------------------
	# makeFilesReadOnly
	# -----------------------------------------------------
	def makeFilesReadOnly(self, dir_path):
		""" 
		Make files in path read only

		Args:
		dir_path: directory in which to recursively make all files read only
		"""

		read_only_chmod = 0444

		# make sure directory exists before we change permissions
		if not os.path.exists(dir_path):
			return

		# walk through all files and directories in the backup path
		for path, dirnames, filenames in os.walk(dir_path):

			# change all file permissions to read only for User, global, and other
			for name in filenames:
				full_name = os.path.join(path, name)
				os.chmod(full_name, read_only_chmod)

	# -----------------------------------------------------
	# formatArchiveFolderName
	# -----------------------------------------------------
	def formatArchiveFolderName(self, folderName):
		"""
		Remove any spaces in the folder name and replace them with '_'
		characters.
		ARGS:
			folderName: the name of a target archive folder

		RETURNS:
			A formatted folder name with spaces replaced by '_'
		"""

		SPACE = ' '
		UNDERSCORE = '_'

		if SPACE in folderName:
			# found at least once SPACE in the folder. Replace with UNDERSCORE
			folderName = folderName.replace(SPACE, UNDERSCORE)

		return folderName

	# -----------------------------------------------------
	# backupFiles
	# -----------------------------------------------------
	def backupFiles(self, fileList, folderName, backupPath, preservePath, debug=False):
		"""
		main backup routine
		
		Args:
		fileList: list of files and folders to backup
		folderName: optional name to tack on to backup folder
		backupPath: path where backup folder will be created
		preserverPath: If True, preserve directory hierarchy for backed up files
		"""

		# check input parameters
		if not fileList:
			print "No files to archive!"
			return

		if debug:
			for file in fileList:
				print "Backing up File %s" % file

		# create the backup directory
		directoryName = self.createTSString()

		folderName = self.formatArchiveFolderName(folderName)

		# add optional folder name to the backup directory
		if folderName:
			directoryName = '%s_%s' % (directoryName, folderName)

		# construct the full backup path
		fullBackupPath = '%s/%s' % (backupPath, directoryName)

		# create the entire backup directory path
		self.createDirectory(fullBackupPath)

		copyCmd = "cp -v"

		# if specified, preserve the directory structure
		if preservePath:
			copyCmd += " --parents"

		for fileToCopy in fileList:

			# construct copy command
			cmd = "%s %s %s" % (copyCmd, fileToCopy, fullBackupPath)

			if debug:
				"copy cmd: %s" % cmd

			# perform the copy
			os.system(cmd)

		# change permissions on archive file
		self.makeFilesReadOnly(fullBackupPath)

	# -----------------------------------------------------
	# createTSString
	# -----------------------------------------------------
	def createTSString(self):
		""" Generate a timestamp string """

		return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

	# -----------------------------------------------------
	# getAbsoluteFilePaths
	# -----------------------------------------------------
	def getAbsoluteFilePaths(self, fileList, traverse=True):
		""" 
		For a list of files and directories, return absolute
		path to all files, including files in subdirectories.

		If traverse is false, just return absolute path
		of items in fileList

		ARGS:
			fileList: list of files or directories

		RETURNS:
			List of absolute FILE paths, no directories
		"""

		returnList = []

		if fileList:

			if traverse:
				# find all sub directories and and sub files in fileList
				for candidateFile in fileList:

					if not os.path.exists(candidateFile):
					 	print "Unable to discover %s. Skipping" % candidateFile
						continue

					# get the absolute path for the file
					fullFilePath = os.path.abspath(candidateFile)

					# if this is a directory, walk the directory and get all fiels
					if os.path.isdir(fullFilePath):

						for root, dirs, files in os.walk(fullFilePath, topdown=False):
							# record all the files in the directory structure
							for name in files:
								fullName = os.path.join(root, name)
								returnList.append(os.path.abspath(fullName))
					else:
						# Not a directory. Simply save file
						returnList.append(fullFilePath)

			else:
				# only provide absolute path to items in fileList
				for item in fileList:
					if os.path.exists(item):
						returnList.append(os.path.abspath(item))

		return returnList

# -----------------------------------------------------
# usage
# -----------------------------------------------------
def usage():
	print argv[0], "-s <name of archive folder> --svn"
	print argv[0], "-s <name of archive folder> <list of files to backup>"
	print argv[0], "--backup <backup location> [--dir <dir path to backup>]]"
	print "if given a directory, back that directory up. If no directory provided, backup current directory"
	print argv[0], "--l"
	print argv[0], "--l <folder>"

# -----------------------------------------------------
# addOptions
# -----------------------------------------------------
def addOptions(parser):
	""" add command line options """
	parser.add_option("--backup", "-b", dest="backupPath", default=DEFAULT_BACKUP_DIR, help="specify a backup directory")
	parser.add_option("--folderName", "-s", dest="folderName", help="add a string to default timestamp backup directory")
	parser.add_option("--preservePath", "-p", dest="preservePath", action='store_const', const=True,  help="preserve directory structure in destination directory")
	parser.add_option("--list", "-l", dest="listArchive", action='store_const', const=True,  help="List the contents of an archived directory")
	parser.add_option("--svn", dest="svnModified", action='store_const', const=True,  help="Only archive files that are marked as modified ('A', 'M') by subversion ")

# -----------------------------------------------------
# main
# -----------------------------------------------------
def main():

	# set up argument parser
	parser = OptionParser( prog=PROGRAM_NAME, description=__doc__, \
                               version=PROGRAM_VERSION, \
                               usage="%prog [options] <file or directory to backup>")

	# add parse options
	addOptions(parser)

	# parse the arguments
	(options, args) = parser.parse_args()

	# perform the backup
	archiver = Archive()

    # create a backup directory, if it doesn't exist
	if not os.path.exists(options.backupPath):
		print "Unable to find backup directory '%s'. Unable to continue." % options.backupPath
		sys.exit(1)


	if options.listArchive:
		####################################
		# list archive files
		####################################

		fileList = [options.backupPath]

		# if arguments are provided, list them instead of default
		# backup directory
		if args:
			fileList = archiver.getAbsoluteFilePaths(args, False)

			if not fileList:
				print "Unable to parse %s to obtain file lists" % args

		# user requesting to list contents of the archive directory
		archiver.listArchiveContents(fileList)

	elif options.svnModified:
		####################################
		# backup modified svn files
		####################################

		handler = SvnHandler()
		backupFiles = handler.getModifiedSvnFiles(debug=False)
		archiver.backupFiles(backupFiles, options.folderName, options.backupPath, options.preservePath)
		
	else:
		####################################
		# backup files and directories specified on the command line
		####################################

		if not args:
			parser.error("No arguments received")
			parser.print_help()
			sys.exit(1)

		# get the absolute path file files to backup
		fileList = archiver.getAbsoluteFilePaths(args)

		# backup files and directories specified by the command line
		archiver.backupFiles(fileList, options.folderName, options.backupPath, options.preservePath, debug=False)

# execute main
if __name__ == "__main__":
	main()
