class Sentence:
    def __init__(self, text, start_offset, end_offset):
        self.text = text
        self.events = []
        self.start_offset = start_offset
        self.end_offset = end_offset 

    def print_GREC_representation(self):

        print 'GREC representation (from classes):\n'
        for event in self.events:
            print event.ID,
            print '\t\tTrigger type: %s (%s)' % (event.trigger_type, ','.join(event.trigger_ID))
            print '\t\tTrigger text: %s'  % (event.trigger_text)
            print '\t\tTrigger span: %s:%s' % (event.trigger_start_offset, event.trigger_end_offset)

            print
            for role in event.thematic_roles:
                print '\t\tThematic role: %s (%s)' % (role.role_type, ','.join(role.ID))
                print '\t\tText: %s' % (role.text)
                print '\t\tText span: %s:%s' % (role.start_offset, role.end_offset)

                print
            print

class Event:
    def __init__(self, ID):
        self.ID = ID
        self.trigger_ID = None
        self.trigger_type = None
        self.trigger_text = None
        self.trigger_ID = None
        self.trigger_start_offset = None
        self.trigger_end_offset = None
        self.thematic_roles = []

class ThematicRole:
    def __init__(self):
        self.role_type = None
        self.text = None
        self.ID = None
        self.start_offset = None
        self.end_offset = None
