import os
import xml.etree.ElementTree as ET
from sentence import Sentence
from term import Term
from event import Event


def get_filenames(directories):
    file_paths = []
    for directory in directories:
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if os.path.isfile(path) and path.endswith('xml'):
                file_paths.append(path)
    return file_paths

def store_data(input_file, filename, all_sentences):
    semantic_roles = ['Agent', 'Theme', 'Manner', 'Instrument', 'Location', \
                        'Source', 'Destination', 'Temporal', 'Condition', \
                        'Rate', 'Descriptive-Theme', 'Descriptive-Agent']

    tree = ET.parse(input_file)
    root = tree.getroot()

    for article in root.iter('Article'):
        events = []
        for event in article.iter('event'):
            event_id = event.get('id')
            event_type = event.find('type').get('class')
            event_word = event.find('clue/clueType').text

            event_roles = {}
            for child in event:
                if child.tag in semantic_roles:
                    semantic_role = child.tag
                    IDs = event_roles.setdefault(semantic_role, [])
                    for k, v in child.attrib.iteritems():
                        IDs.append(v)
            new_event = Event(event_id, event_word, event_type, event_roles)
            events.append(new_event)


        for sentence in article.iter('sentence'):
            ID = sentence.get('id')
            text = ET.tostring(sentence, encoding='utf8', method="text").strip()

            new_sentence = Sentence(filename, ID, text)
            all_sentences.append(new_sentence)

            for term in sentence.iter('term'):
                term_sem = term.get('sem')
                term_id = term.get('id')
                term_lex = term.get('lex')
                new_term = Term(term_sem, term_id, term_lex)
                new_sentence.terms.append(new_term)

                # loop through events.  Add events to sentences.
                for event in events:
                    for role, ID in event.roles.iteritems():
                        if term_id in ID and event not in new_sentence.events:
                            new_sentence.events.append(event)




def output_sentences(all_sentences):
    #f = open('sentences_for_erg', 'w')
    for s in all_sentences:
        if len(s.terms) > 0:
            print s.text
 




def main():
    directories = ['../GREC_XML/Ecoli', '../GREC_XML/Human']
    all_filenames = get_filenames(directories)

    all_sentences = []

    for f in all_filenames:
        filename = f.split('/')[3][:-4]
        store_data(f, filename, all_sentences)

    annotated_sentences = []
    for sentence in all_sentences:
        if len(sentence.terms) > 0:
            annotated_sentences.append(sentence)


    output_sentences(annotated_sentences)








if __name__=='__main__':
    main()
