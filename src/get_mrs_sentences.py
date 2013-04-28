import re

# this is still very much a work in progress



# strips SENT: from each sentence
def process_sentence(sentence):
    return re.sub('SENT: ', '', sentence)


def process_parse(parse):
    pass


# will store mrs parses in some way
def store_data(s, p):
    sentence = process_sentence(s)
    process_parse(p)


def main():
    mrs_parses = open('ace.mrs.out')

    i = 0
    while True:
        line = mrs_parses.readline()
        if 'SENT' in line:
            sentence = line.strip()
            parse = mrs_parses.readline().strip()
            store_data(sentence, parse)
            break       # currently only working with the first sentence


        if not line:
            break

if __name__=='__main__':
    main()
