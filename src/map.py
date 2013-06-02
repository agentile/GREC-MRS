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
from sentence import Sentence, Event, ThematicRole, Relation, Argument, MappedEvent, MappedThematicRole

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
        bracket_end = getMatchingBracket(rels_str, bracket_start, '"')
        
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
            

def getMatchingBracket(string, start_pos, disregard_context_character=False):
    length = len(string)
    bracket = 1
    disregard = 0
    for i in xrange(start_pos + 1, length):
        if disregard_context_character != False and string[i] == disregard_context_character:
            if disregard == 0:
                disregard = 1
            else:
                disregard = 0
        if string[i] == '[' and disregard == 0:
            bracket += 1
        elif string[i] == ']' and disregard == 0:
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
        if a['abstract_text'].find(s) != -1:
            abstract = a

    if not abstract:
        raise Exception('Did not find sentence')

    # get sentence offsets
    start = abstract['abstract_text'].index(s)
    end = start + len(s)


    # pull relevant info from existing data structures
    triggers = abstract['annotations']['trigger_annotations']
    events = abstract['annotations']['event_annotations']
    thematic_spans = abstract['text_spans']

    trigger_ids = set()
    triggers_this_sent = []
    for t in triggers:
        if t['start_offset'] >= start and t['end_offset'] <= end:
            triggers_this_sent.append(t)
            trigger_ids.add(t['ID'])

    thematic_this_sent = []
    for t in thematic_spans:
        if t['start_offset'] >= start and  t['end_offset'] <= end:
            trigger_ids.add(t['ID'])
            thematic_this_sent.append(t)

    events_this_sent = []
    for e in events:
        for t in e['tuples']:
            for trigger in trigger_ids:
                if trigger in t['ids'] and (e['ID'], e['tuples']) not in events_this_sent:
                    events_this_sent.append((e['ID'], e['tuples']))



    return (start, end, events_this_sent, triggers_this_sent, thematic_this_sent)



# to do:  some fields are None - why is this?
# to do: recursive events are not dealt with
def create_GREC_structure(sentence, GREC_events, semantic_roles):
    start, end, sentence_events, sentence_triggers, sentence_thematic = GREC_events

    # create new sentence object
    sentence.GREC_start_offset = start
    sentence.GREC_end_offset = end

    for event_id, event_types in sentence_events:
        new_event = Event(event_id)
        sentence.GREC_events.append(new_event)


        for event in event_types:
            if event['event_type'] in semantic_roles:
                new_role = ThematicRole()
                new_event.thematic_roles.append(new_role)
                new_role.role_type = event['event_type']
                new_role.ID = event['ids']

                for ID in new_role.ID:
                    for t in sentence_thematic:
                        if ID == t['ID']:
                            new_role.text = t['span']
                            new_role.start_offset = t['start_offset'] - start
                            new_role.end_offset = t['end_offset'] - start
            else:
                new_event.trigger_type = event['event_type']
                new_event.trigger_ID = event['ids']

                for ID in new_event.trigger_ID:
                    for t in sentence_triggers:
                        if ID ==  t['ID']:
                            new_event.trigger_text = t['span']
                            new_event.start_offset = t['start_offset'] - start
                            new_event.end_offset = t['end_offset'] - start




# to do: key errors w two records: {'ARGN': {}} and {'ARGN': {}} - why?
def create_MRS_structure(sentence, s, mrs):
    for rel in mrs['RELS']:
        new_relation = Relation()
        sentence.MRS_relations.append(new_relation)
        try:
            new_relation.rel_type = rel['label']
            new_relation.rel_text = s[rel['offset_start']:rel['offset_end']]
            new_relation.start_offset = rel['offset_start']
            new_relation.end_offset = rel['offset_end']
        except KeyError:
            print 'not found'

        for arg, arg_details in rel['ARGN'].iteritems():
            if 'ARG' in arg:
                new_arg = Argument(arg, arg_details['root'])
                new_relation.argument_list.append(new_arg)

   # to do: fix this to restrict relations 
    for relation in sentence.MRS_relations:
        for argument in relation.argument_list:
            if argument.name != 'ARG0':
                find = argument.root
                for search_relation in sentence.MRS_relations:
                    for search_argument in search_relation.argument_list:
                        if search_argument.name == 'ARG0' and search_argument.root == find:
                            argument.start_offset = search_relation.start_offset
                            argument.end_offset = search_relation.end_offset



def output():
    pass


# two dictionaries are returned
def create_lexical_resource(sentences):
    triggers_and_roles = {} # trigger : {(role, len(roles)) : count, ...}
    triggers_and_types = {}
    for sentence in sentences:
        for event in sentence.GREC_events:
            trigger_types = triggers_and_types.setdefault(event.trigger_text, {})
            trigger_types[event.trigger_type] = trigger_types.get(event.trigger_type, 0) + 1
            for tr in event.thematic_roles:
                roles = triggers_and_roles.setdefault((event.trigger_text, len(event.thematic_roles)), {})
                roles[tr.role_type] = roles.get(tr.role_type, 0) + 1
    return triggers_and_roles, triggers_and_types


def map_MRS_to_GREC(triggers, types, sentence):
    i = 1
    ignore = ['udef_q_rel', 'parg_d_rel']
    for relation in sentence.MRS_relations:
        for trigger, num in triggers.iteritems():

            # if  the text of the relation matches a trigger from GREC, create
            # an event for it
            if relation.rel_text == trigger[0] and relation.rel_type not in ignore:
                mapped_event_id = 'E%d' % (i)
                i += 1
                new_mapped_event = MappedEvent(mapped_event_id, relation.rel_text,\
                        relation.start_offset, relation.end_offset)
                sentence.mapped_GREC_events.append(new_mapped_event)

                # get the most likely trigger type for the relation text/trigger
                possible_types = types[relation.rel_text]
                most_likely_type = max(possible_types.iterkeys(), key=(lambda x: possible_types[x]))
                new_mapped_event.trigger_type = most_likely_type


                # create new thematic role for each argument from the relation
                for argument in relation.argument_list:
                    if argument.name != 'ARG0':
                        new_thematic_role = MappedThematicRole(argument.start_offset, argument.end_offset)
                        new_mapped_event.thematic_roles.append(new_thematic_role)









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

    semantic_roles = ['Agent', 'Theme', 'Manner', 'Instrument', 'Location', \
                    'Source', 'Destination', 'Temporal', 'Condition', \
                    'Rate', 'Descriptive-Theme', 'Descriptive-Agent']

    # Lets parse our MRS file to get sentence, mrs, and grec info 
    # in a python data structure to make things sane to work with.
    i = 0

    # create list for sentence objects
    all_sentences = []

    for line in lines:
        if line[:5] == 'SENT:':
            sentence = line[6:].strip()

            # store GREC and MRS details in data structures
            GREC_events = get_GREC_events(sentence, GREC)
            mrs = parseMRS(lines[i+1].strip())


            # create new sentence object and append to sentences list
            new_sentence = Sentence(sentence)
            all_sentences.append(new_sentence)


            # add GREC and MRS details to sentence object
            create_GREC_structure(new_sentence, GREC_events, semantic_roles)
            create_MRS_structure(new_sentence, sentence, mrs)


            """
            print 'POSSIBLE HEAD NOUN CANDIATES - ' + sentence
            print

            #<DT|PP\$>?<JJ>*<NN|NNP>+
            print 'ALL NOUNS'
            for rel in mrs['RELS']:
                #All nouns
                if '/N' in rel['label'] or '_n_' in rel['label']:
                    print rel['label']
                    
            z = 0
            print 'HEAD NOUNS ?'
            for rel in mrs['RELS']:
                #All nouns
                if '/N' in rel['label'] or '_n_' in rel['label']:
                    try:
                        if '/JJ' in mrs['RELS'][z-1]['label'] or '_a_' in mrs['RELS'][z-1]['label']:
                            print rel['label']
                    except:
                        pass
                z += 1
                
            print '*' * 100
            
            
            """
            break


        i += 1
    f.close()

    # create lexical resource
    triggers_and_roles, triggers_and_types = create_lexical_resource(all_sentences)

    # map and output sentences
    j = 1
    for sentence in all_sentences:
        # output GREC and MRS representations
        #print 'SENTENCE #%d\n' % (j)
        #print sentence
        #sentence.print_GREC_representation()
        #sentence.print_MRS_representation()

        map_MRS_to_GREC(triggers_and_roles, triggers_and_types, sentence)
        sentence.print_mapped_GREC_representation()
        #print '*' * 100
        j += 1



    # End Timer
    end = datetime.now()
    print 'Time elapsed: ' + str(end - start)
