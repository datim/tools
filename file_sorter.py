#!/bin/python
#
# This program sorts files into directorys by year. It also re-names the files to put a date and timestamp at the front

import sys
import os
import argparse
import time
import shutil
import datetime
import pdb
import hashlib

######################################
class FileSorter:
    """ Sorts and copies files into destination directories by year. Discovers duplicates by checksum """
    
    DUPLICATE_PATH = "duplicates"

    def __init__(self):
        """ initialize the destination directory """
        
        self.total_file_count = 0
        self.duplicates_count = 0
        self.yearCount = {}
        self.duplicateYearCount = {}

    def sortFiles(self, source_dirs, dest_dir, tag, by_month, test_only):
        """ Initialize the sorting of files by year """
        
        if test_only:
            print "Test only mode"
        
        file_metadata_dict = self._parseFiles(source_dirs)
        
        # create destination directories
        st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        dest_dir = os.path.join(os.path.dirname(dest_dir), st + "_" + os.path.basename(dest_dir))
        
        # create duplicate path directory
        duplicate_dir = os.path.join(dest_dir, self.DUPLICATE_PATH)

        # we've finished reading every file. Now copy and re-name them
        self._transferFiles(file_metadata_dict, dest_dir, duplicate_dir, tag, test_only)

        # print statistics when we're done
        self._printStatistic()

    def _parseFiles(self, source_dirs):
        """ Parse each file in the list of source directories for meta data """
        
        file_list = []
        file_metadata_dict = {}
        files_dict = {}
        
        # validate every source directory
        for source in source_dirs:
            if not os.path.exists(source):
                raise Exception("Source directory %s does not exist!" % source)
        
            # read all files in the nested directory structure
            for root, dirs, files in os.walk(source):

                # save metadata for each file in the discovered in the file path
                for name in files:
                    full_file_path = os.path.join(source, root, name)
                    
                    file_list.append(full_file_path)
                    
                    
        file_count = len(file_list)
                    
        print "Discovered %d files" % file_count
        
        count = 0
                    
        for full_file_path in file_list:
        
            count += 1
            sys.stdout.write("Parsing file %d of %d \r" % (count, file_count))
            sys.stdout.flush()

            # extract the file's meta data
            year, create_datetime, file_checksum = self._extractFileMetaData(full_file_path)
                    
            # save metadata for the file
            file_metadata_dict[full_file_path] = {"year" : year, "create_dt" : create_datetime, "chksum" : file_checksum}
                    
        return file_metadata_dict

    def _extractFileMetaData(self, file_name):
        """ For each file path, internally catalog the file by getting its timestamp and checksum """
               
        # FIXME -log it
        # print "reading file %s\n" % file_name

        # get the hash of the file, used for detecting duplicates later
        file_checksum = self._getFileChecksum(file_name)

        # get the file creation time stamp
        create_time = os.path.getmtime(file_name)
        create_datetime = datetime.datetime.fromtimestamp(create_time)

        # get the create year
        create_year = str(create_datetime.year)

        return create_year, create_datetime, file_checksum
        
    def _getFileChecksum(self, file_name_and_path):
        """ Generate the checksum of a file """

        # algorithm from http://pythoncentral.io/hashing-files-with-python/
        hasher = hashlib.md5()
        with open(file_name_and_path, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
            return hasher.hexdigest()

    def _transferFiles(self, file_metadata_dict, dest_dir, duplicate_dir, tag, test_only):
        """ copy files from a source location to the destiation location.  Copy duplicates
            to a duplicate directory """

        # look for duplicates
        checksum_list = []
        count = 0
        file_count = len(file_metadata_dict.keys())
        
        pdb.set_trace()
                
        # iterate through every file
        for file_path, metadata in file_metadata_dict.iteritems():
        
            create_ts = metadata.get("create_dt")
            checksum = metadata.get("chksum")
            year = metadata.get("year")
        
            # create the new directory for the year
            year_dir_name = os.path.join(dest_dir, year, tag)
            
            if not os.path.exists(year_dir_name):
                os.makedirs(year_dir_name)
            
            # generate the destination file name
            dest_file_name = create_ts.strftime("%Y%m%d_%H%M%S") + "_" + os.path.basename(file_path)

            # check whether this file has been encountered before
            if checksum in checksum_list:
                
                ## This is a duplicate file. Move it to the duplicate directory ##
                if not os.path.exists(duplicate_dir):
                    os.makedirs(duplicate_dir)  
                    
                # copy the file to the duplicate directory
                dest_file_name = os.path.join(duplicate_dir, dest_file_name)
            
                # lower case file names only
                dest_file_name = dest_file_name.lower()
                    
                # write statistics
                self._recordDuplicate(year)

            else:
            
                ## Copy the file
                checksum_list.append(checksum)

                # file is not a duplicate, copy it
                dest_file_name = os.path.join(year_dir_name, dest_file_name)

                # lower case file names only
                dest_file_name = dest_file_name.lower()

                # write statistics
                self._recordCopy(year)
                
            # print status
            count += 1
            sys.stdout.write("Copying file %d of %d \r" % (count, file_count))
            sys.stdout.flush()
            
            if not test_only:
                # Copy the file to the destination
                shutil.copyfile(file_path, dest_file_name)

    def _recordDuplicate(self, year):
        """ Record statistics about duplicate files """
        self._recordStatistic(year, True)
        
    def _recordCopy(self, year):
        """ Record statistics about successful copies """
        self._recordStatistic(year, False)
        
    def _recordStatistic(self, year, duplicate):
        """ record statistics about the copying of files """

        # increment total count
        self.total_file_count += 1

        if duplicate:
            # this was a duplicate file. Record it
            self.duplicates_count += 1

            # track duplicate by year
            if year in self.duplicateYearCount:
                self.duplicateYearCount[year] += 1
                
            else:
                # first duplicate of this year
                self.duplicateYearCount[year] = 1
        
        else:
            # create a year statistic directory if it doesn't exist
            if year in self.yearCount:
                self.yearCount[year] += 1

            else:
                # first file of this year
                self.yearCount[year] = 1

    def _printStatistic(self):
        print "\n============================================================================"
        print "Total files organized: %d" % self.total_file_count
        
        for year, count in self.yearCount.iteritems():
            print "   For year %s: %d" % (year, count)

        # print duplicate statistics
        print "Total duplicates: %d" % self.duplicates_count

        for year, count in self.duplicateYearCount.iteritems():
            print "   For year %s : %d" % (year, count)
        print "============================================================================"

def defineArgs(parser):
        """ Set the arguments of the arg parser """
        parser.add_argument('-d', '--dest', required=False, default="./parse_output", help='the destination directory to write files to')
        parser.add_argument('-m', '--month', required=False, action='store_true', help='if set, organize files by month in addition to year')
        parser.add_argument('-l', '--label', required=False, default="mobile", help='the label to apply to result directories')
        parser.add_argument('source_dirs', nargs='+', help='the source directories')
        parser.add_argument('-t', '--test', required=False, action='store_true', help='test only')
        
def main(): 
    print "Sorting files"

    parser = argparse.ArgumentParser(description = "Sort files into directories by year and optionally by month")
    defineArgs(parser)

    # parse the arguments
    args = parser.parse_args()

    sorter = FileSorter()
    sorter.sortFiles(args.source_dirs, args.dest, args.label, args.month, args.test)
       
if __name__ == "__main__":
    main()