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
import os, sys, operator, re
from datetime import datetime
import mmap
import pprint

# store all GREC data
def getGRECData(grec_files):
    all_grec = {}
    for path, file_num in grec_files:
        abstract = {}

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

        abstract_text = '%s %s' % (txt_lines[0], txt_lines[1].strip())
        abstract = {
                'abstract_text' : abstract_text,
                'text_spans' : parseA1(a1_lines),
                'annotations' : parseA2(a2_lines)
                }

        all_grec[file_num] = abstract

    return all_grec


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
    INDEX = parseIndex(mrs_string[mrs_string.find('INDEX:') + 6:mrs_string.find('RELS:')].strip())
    RELS = parseRels(mrs_string[mrs_string.find('RELS:') + 5:mrs_string.find('HCONS:')].strip())
    HCONS = mrs_string[mrs_string.find('HCONS:') + 6:mrs_string.rfind(']')].strip()[2:-2].split(' ')

    # TODO: for INDEX and RELS, parse and break down the nested [] arguments 
    # so that we can work with those easily.
    return {
        'LTOP' : LTOP, 
        'INDEX' : INDEX, 
        'RELS' : RELS, 
        'HCONS' : HCONS
    }
    
def parseRels(rels_str):

    args = {}
    
    eps = []
    start = 0
    bracket_start = rels_str.find('[', start)
    while bracket_start != -1:
        bracket_end = getMatchingBracket(rels_str, bracket_start)
        
        e = rels_str[bracket_start + 1:bracket_end].strip()

        arg = {}
        
        if e.find('<') != -1:
            arg['label'] = e[:e.find('<')] # this probably should be renamed, what is the proper name for this?
            arg['offset_start'] = int(e[e.find('<') + 1:e.find(':', e.find('<'))])
            arg['offset_end'] = int(e[e.find(':', e.find('<')) + 1:e.find('>', e.find(':', e.find('<')))])
            
        if e.find('LBL: ') != -1:
            arg['LBL'] = e[e.find('LBL: ') + 5:e.find(' ', e.find('LBL: ') + 5)]
            
        if e.find('CARG: ') != -1:
            arg['CARG'] = e[e.find('CARG: ') + 6:e.find(' ', e.find('CARG: ') + 6)]
            
        if e.find('RSTR: ') != -1:
            arg['RSTR'] = e[e.find('RSTR: ') + 6:e.find(' ', e.find('RSTR: ') + 6)]
            
        if e.find('BODY: ') != -1:
            arg['BODY'] = e[e.find('BODY: ') + 6:e.find(' ', e.find('BODY: ') + 6)]
            
        if e.find('BODY: ') != -1:
            arg['BODY'] = e[e.find('BODY: ') + 6:e.find(' ', e.find('BODY: ') + 6)]
            
        if e.find('L-INDEX: ') != -1:
            arg['L-INDEX'] = parseIndex(getArgValue(e, 'L-INDEX'))
            
        if e.find('R-INDEX: ') != -1:
            arg['R-INDEX'] = parseIndex(getArgValue(e, 'R-INDEX'))

        if e.find('L-HNDL: ') != -1:
            arg['L-HNDL'] = parseIndex(getArgValue(e, 'L-HNDL'))
            
        if e.find('R-HNDL: ') != -1:
            arg['R-HNDL'] = parseIndex(getArgValue(e, 'R-HNDL'))
        
        # Handle ARG
        for m in re.finditer("ARG:", e):
            arg['ARG'] = parseIndex(getArgValue(e, m.group(0)[:-1]))
            
        # Handle ARGN
        arg['ARGN'] = {}
        for m in re.finditer("ARG[0-9]:", e):
            arg['ARGN'][m.group(0)[:-1]] = parseIndex(getArgValue(e, m.group(0)[:-1]))
        
        eps.append(arg)
        
        # find next eps
        bracket_start = rels_str.find('[', bracket_end + 1)
        
    return eps
    
# given ARG: x4 [ x PERS: 3 NUM: sg ] or ARG: h4 return x4 [ x PERS: 3 NUM: sg ] or h4 respectively
# making sure not to collide with other args/nested brackets
def getArgValue(e, key):
    s = e.find(key + ': ')
    s_bracket_pos = e.find(' ',s + (len(key) + 2)) + 1
    s_bracket = e[s_bracket_pos]
    if s_bracket == '[':
        e_bracket = getMatchingBracket(e,s_bracket_pos)
        return e[s + (len(key) + 2):e_bracket + 1]
    else:
        m = re.search("[A-Z0-9-]+:", e[e.find(key + ': ') + (len(key) + 2):])
        if m:
            return e[e.find(key + ': ') + (len(key) + 2):e.find(m.group(0), e.find(key + ': ') + (len(key) + 2)) - 1]
        else:
            # assume it is the last arg in the string and there is none after it
            return e[e.find(key + ': ') + (len(key) + 2):]
            

def getMatchingBracket(string, start_pos):
    length = len(string)
    bracket = 1
    for i in xrange(start_pos + 1, length):
        if string[i] == '[':
            bracket += 1
        elif string[i] == ']':
            bracket -= 1
        if bracket == 0:
            return i

def parseIndex(index_str):
    # I don't think e2 is called root or the e is child, but I don't know what they 
    # are called properly
    args = {}

    if index_str.find(' ') != -1:
        args['root'] = index_str[:index_str.find(' ')]
    else:
        args['root'] = index_str
    
    if index_str.find('[') != -1:
        args['child'] = index_str[index_str.find('[')+2:index_str.find(' ', index_str.find('[')+2)]
        
    if index_str.find('SF: ') != -1:
        args['SF'] = index_str[index_str.find('SF: ') + 4:index_str.find(' ', index_str.find('SF: ') + 4)]
        
    if index_str.find('TENSE: ') != -1:
        #print index_str
        args['TENSE'] = index_str[index_str.find('TENSE: ') + 7:index_str.find(' ', index_str.find('TENSE: ') + 7)]
        
    if index_str.find('MOOD: ') != -1:
        args['MOOD'] = index_str[index_str.find('MOOD: ') + 6:index_str.find(' ', index_str.find('MOOD: ') + 6)]
        
    if index_str.find('PROG: ') != -1:
        args['PROG'] = index_str[index_str.find('PROG: ') + 6:index_str.find(' ', index_str.find('PROG: ') + 6)]
        
    if index_str.find('PERF: ') != -1:
        args['PERF'] = index_str[index_str.find('PERF: ') + 6:index_str.find(' ', index_str.find('PERF: ') + 6)]
        
    if index_str.find('PERS: ') != -1:
        args['PERS'] = index_str[index_str.find('PERS: ') + 6:index_str.find(' ', index_str.find('PERS: ') + 6)]
        
    if index_str.find('GEND: ') != -1:
        args['GEND'] = index_str[index_str.find('GEND: ') + 6:index_str.find(' ', index_str.find('GEND: ') + 6)]
        
    if index_str.find('NUM: ') != -1:
        args['NUM'] = index_str[index_str.find('NUM: ') + 5:index_str.find(' ', index_str.find('NUM: ') + 5)]
        
    if index_str.find('IND: ') != -1:
        args['IND'] = index_str[index_str.find('IND: ') + 5:index_str.find(' ', index_str.find('IND: ') + 5)]

    return args

# takes a sentence and returns associated events from GREC
def get_GREC_events(s, GREC):
    abstract = {}
    for file_num, a in GREC.iteritems():
        if a['abstract_text'].find(sentence) != -1:
            abstract = a

    if not abstract:
        raise Exception('Did not find sentence')

    start = abstract['abstract_text'].index(s)
    end = start + len(s)

    triggers = abstract['annotations']['trigger_annotations']
    events = abstract['annotations']['event_annotations']

    trigger_ids = set()
    triggers_this_sent = []
    for t in triggers:
        if t['start_offset'] >= start and t['end_offset'] <= end:
            triggers_this_sent.append(t)
            trigger_ids.add(t['ID'])


    events_this_sent = []
    for e in events:
        for t in e['tuples']:
            for trigger in trigger_ids:
                if trigger in t['ids']:
                    events_this_sent.append((e['ID'], e['tuples']))

    return start, end, events_this_sent, triggers_this_sent







if __name__=='__main__':
    # Start timer
    start = datetime.now()

    # Load up GREC corpus .txt into memory 
    standoff_dirs = ['../GREC_Standoff/Ecoli/', '../GREC_Standoff/Human/']
    grec_files = []
    for sdir in standoff_dirs:
        for r,d,files in os.walk(sdir):
            for f in files:
                if f.endswith(".txt"):
                    file_num = f.replace('.txt', '')
                    path = os.path.join(r,f)
                    grec_files.append((path, file_num))


    # Put all GREC data into a dict
    GREC = getGRECData(grec_files)

    # Fetch our ace MRS file
    ace_mrs = os.path.realpath(sys.argv[1])

    f = open(ace_mrs)
    lines = f.readlines()

    data = []

    # Lets parse our MRS file to get sentence, mrs, and grec info 
    # in a python data structure to make things sane to work with.
    i = 0
    j = 1
    for line in lines:
        if line[:5] == 'SENT:':
            sentence = line[6:].strip()


            print 'SENTENCE #%d\n' % (j)
            print sentence


            sent_start, sent_end, sentence_events, sentence_triggers = get_GREC_events(sentence, GREC)
            mrs = parseMRS(lines[i+1].strip())

            # lets just do one so we can see the output, comment this out 
            # when ready to move on.
            print 'MRS representation:\n'
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(mrs)
            print

            # needs stuff from .a1 files for thematic roles
            print 'GREC representation:\n'
            for event_id, event_types in sentence_events:
                print event_id,
                for event in event_types:
                    print '\tEvent type: %s' % (event['event_type'])
                    for ID in event['ids']:
                        for t in sentence_triggers:
                            if ID ==  t['ID']:
                                print '\tTrigger word: %s' % (t['span'])
                                print '\tTrigger Span: %s:%s' % (t['start_offset'], t['end_offset'])
                                print
                print
            print


            print '*' * 100
            j += 1
            break

        i += 1
    f.close()

    # End Timer
    end = datetime.now()
    print 'Time elapsed: ' + str(end - start)
