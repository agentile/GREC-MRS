class Sentence:
    def __init__(self, text):
        self.text = text
        self.GREC_start_offset = None
        self.GREC_end_offset = None
        self.GREC_events = []
        self.MRS_relations = []

    def print_GREC_representation(self):

        print 'GREC representation:\n'
        for event in self.GREC_events:
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

    def print_MRS_representation(self):
        print 'MRS representation:\n'
        for relation in self.MRS_relations:
            print '\t\tRel type: %s' % (relation.rel_type)
            print '\t\tRel text: %s' % (relation.rel_text)
            print '\t\tRel span: %s:%s' % (relation.start_offset, relation.end_offset)
            print '\t\tARG list:'
            for arg in relation.argument_list:
                print '\t\t\t%s: %s' % (arg.name, arg.root)
            print

# GREC event
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

# GREC thematic role
class ThematicRole:
    def __init__(self):
        self.role_type = None
        self.text = None
        self.ID = None
        self.start_offset = None
        self.end_offset = None

# MRS relation
class Relation:
    def __init__(self):
        self.rel_type = None
        self.rel_text = None
        self.start_offset = None
        self.end_offset = None
        self.argument_list = []

# MRS argument of relation
class Argument:
    def __init__(self):
        self.name = None
        self.root = None
