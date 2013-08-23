#!/usr/bin/env python

'''import ratings from imdb to filmtipset using 
ratings.csv exported from the imdb rating history. 
filmtipset grade = ceil(imdb rating / 2).

usage: filmtipset-imdb-import.py [-h] -a accesskey -u userkey ratings.csv

positional arguments:
  ratings.csv   ratings.csv exported from imdb

optional arguments:
  -h, --help    show this help message and exit
  -a accesskey  accesskey from filmtipset
  -u userkey    userkey from filmtipset
'''

import argparse
import csv
import urllib2
import json
import math

def main(args):
    # IMDB ratings.csv format
    # "position","const","created","modified","description","Title","Title type",
    # "Directors","You rated","IMDb Rating","Runtime (mins)","Year","Genres",
    # "Num. Votes","Release Date (month/day/year)","URL"
    
    reader = csv.reader(args.imdb_ratings_csv)
    
    for idx, row in enumerate(reader):
        imdb_id, imdb_rating = row[1], row[8]
        try:
            filmtipset_id = get_filmtipset_id_from_imdb_id(args.accesskey, 
                                                           args.userkey, 
                                                           imdb_id)
            grade = vote(args.accesskey, 
                         args.userkey, 
                         filmtipset_id, 
                         imdb_rating)
            print '{0:4d} {1:8s} {2}/5 {3}'.format(idx, "OK", grade, row[5])
            
        except IndexError as ie:
            print '\033[1m{0:4d} {1:12s} {2}\033[0m'.format(idx, "MISSING", row[5])
            log_error(args.imdb_ratings_csv.name[:-4]+"_missing.csv", row)
            
        except Exception as e:
            print '\033[1m{0:4d} {1:12s} {2}\033[0m'.format(idx, "FAILED", row[5])
            log_error(args.imdb_ratings_csv.name[:-4]+"_failed.csv", row)
    
def get_filmtipset_id_from_imdb_id(accesskey, userkey, imdb_id):
    # strip tt from tt0337921 
    imdb_id = imdb_id[2:]
    
    imdb_action = ("http://www.filmtipset.se/api/api.cgi?"
                   "accesskey={akey}&"
                   "userkey={ukey}&"
                   "returntype=json&"
                   "action=imdb&"
                   "id={imdbid}&"
                   "nocomments=1").format(akey=accesskey, 
                                          ukey=userkey, 
                                          imdbid=imdb_id)

    response = urllib2.urlopen(imdb_action)
    if response.getcode() != 200:
        raise Exception("HTTP response != 200")   

    jsonData = json.loads(unicode(response.read(), "ISO-8859-1"))
    return jsonData[0]["data"][0]["movie"]["id"]
        
def vote(accesskey, userkey, filmtipset_id, imdb_rating):
    filmtipset_grade = int(math.ceil(float(imdb_rating)/2.0)) 

    vote_action = ("http://www.filmtipset.se/api/api.cgi?"
                   "accesskey={akey}&"
                   "userkey={ukey}&"
                   "returntype=json&"
                   "action=grade&"
                   "id={filmtipsetid}&"
                   "grade={grade}").format(akey=accesskey,
                                           ukey=userkey,
                                           filmtipsetid=filmtipset_id,
                                           grade=filmtipset_grade)
                                          
    response = urllib2.urlopen(vote_action)
    if response.getcode() != 200:
        raise Exception("HTTP response != 200") 
    
    # vote action returns the movie information, just as the imdb action.
    # to validate the response was ok, try to get the id of the movie.
    jsonData = json.loads(unicode(response.read(), "ISO-8859-1"))
    jsonData[0]["data"][0]["movie"]["id"]
    return filmtipset_grade
    
def log_error(error_file, error_row):
    with open(error_file, 'ab') as f:
        writer = csv.writer(f)
        writer.writerow(error_row)
    
if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description=("import ratings from imdb to filmtipset "
                                                  "using ratings.csv exported from the "
                                                  "imdb rating history. filmtipset grade = "
                                                  "ceil(imdb rating / 2)."))
    parser.add_argument("-a", metavar="accesskey", dest="accesskey", 
                        required=True, 
                        help="accesskey from filmtipset")
    parser.add_argument("-u", metavar="userkey", dest="userkey",
                        required=True, 
                        help="userkey from filmtipset")
    parser.add_argument("imdb_ratings_csv", metavar="ratings.csv",
                        type=argparse.FileType('rb'), 
                        help="ratings.csv exported from imdb")
    args = parser.parse_args()
    
    main(args)
