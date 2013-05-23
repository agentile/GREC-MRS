#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 575 - Spring 2013 - GREC MRS Project
#
# Take MRS from ACE and compare/map with GREC
# 
# python2.7 map.py ace.mrs.out
#
# @author Anthony Gentile <agentile@uw.edu>
# @author Lisa Gress <gress@uw.edu>
import os, sys, operator
from datetime import datetime
import mmap
import pprint

# Take a sentence and find it in the GREC corpus 
# returning back the things we want to use
def getGRECData(grec_files, sentence):
    for k in grec_files:
        if sentence in grec_files[k]:
            path = k

            # Get abstract title and body from .txt file
            ff = open(path)
            txt_lines = ff.readlines()
            ff.close()
            
            # Get .a1 info
            ff = open(path.replace('.txt','.a1'))
            a1_lines = ff.readlines()
            ff.close()
            
            # Get .a2 info
            ff = open(path.replace('.txt','.a2'))
            a2_lines = ff.readlines()
            ff.close()
            
            return {
                'abstract_title' : txt_lines[0].strip(),
                'abstract_body' : txt_lines[1].strip(),
                'text_spans' : parseA1(a1_lines),
                'annotations' : parseA2(a2_lines)
            }
         
    return {}
    
    
# Parse a GREC .a1 file
def parseA1(lines):
    spans = []

    for line in lines:
        if line.strip() == '':
            continue
            
        parts = line.split("\t")
        triple = parts[1].split(' ')
        spans.append({
            'ID' : parts[0].strip(),
            'type' : triple[0],
            'start_offset' : int(triple[1]),
            'end_offset' : int(triple[2]),
            'span' : parts[2].strip()
        })
    
    return spans
    
# Parse a GREC .a2 file
def parseA2(lines):
    event_annotations = []
    trigger_annotations = []
    
    first_E = False
    i = 0
    for line in lines:
        # Skip the first section as we will use parseA1 to do that part
        if line.strip() == '' or line[0] == 'T':
            i += 1
            continue
            
        if first_E == False and line[0] == 'E':
            first_E = True
            trigger_annotations = parseA1(lines[:i])

        parts = line.split("\t")
        ID = parts[0].strip()
        tuples = parts[1].split(' ')
        e_tuples = []
        for t in tuples:
            parts = t.split(':')
            e_tuples.append({
                'event_type' : parts[0],
                'ids' : parts[1].strip().split(',')
            })

        event_annotations.append({
            'ID' : ID,
            'tuples' : e_tuples
        })
        i += 1
    
    return {'trigger_annotations' : trigger_annotations, 'event_annotations' : event_annotations}
    
# Lets take a ACE MRS string and turn it into a python dictionary
# that we can work with. Nothing fancy here just some substring matching
def parseMRS(mrs_string):
    LTOP = mrs_string[mrs_string.find('LTOP:') + 5:mrs_string.find('INDEX:')].strip()
    INDEX = mrs_string[mrs_string.find('INDEX:') + 6:mrs_string.find('RELS:')].strip()
    RELS = mrs_string[mrs_string.find('RELS:') + 5:mrs_string.find('HCONS:')].strip()
    HCONS = mrs_string[mrs_string.find('HCONS:') + 6:mrs_string.rfind(']')].strip()

    # TODO: for INDEX and RELS, parse and break down the nested [] arguments 
    # so that we can work with those easily.
    return {'LTOP' : LTOP, 'INDEX' : INDEX, 'RELS' : RELS, 'HCONS' : HCONS}

if __name__=='__main__':
    # Start timer
    start = datetime.now()
    
    # Load up GREC corpus .txt into memory 
    standoff_dirs = ['../GREC_Standoff/Ecoli/', '../GREC_Standoff/Human/']
    grec_files = {}
    for sdir in standoff_dirs:
        for r,d,files in os.walk(sdir):
            for f in files:
                if f.endswith(".txt"):
                    path = os.path.join(r,f)
                    grec_files[path] = open(path).read()
    
    # Fetch our ace MRS file
    ace_mrs = os.path.realpath(sys.argv[1])
    
    f = open(ace_mrs)
    lines = f.readlines()
    
    data = []
    
    # Lets parse our MRS file to get sentence, mrs, and grec info 
    # in a python data structure to make things sane to work with.
    i = 0
    for line in lines:
        if line[:5] == 'SENT:':
            data.append({
                'sentence' : line[6:].strip(), 
                'mrs' : parseMRS(lines[i+1].strip()),
                'grec' : getGRECData(grec_files, line[6:].strip())
            })
            # lets just do one so we can see the output
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(data)
            break
        i += 1
    f.close()
    
    # End Timer
    end = datetime.now()
    print 'Time elapsed: ' + str(end - start)
