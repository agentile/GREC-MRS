class Sentence:
    def __init__(self, text):
        self.text = text
        self.GREC_start_offset = None
        self.GREC_end_offset = None
        self.GREC_events = []
        self.MRS_relations = []
        self.mapped_GREC_events = []

    def print_GREC_representation(self):

        print 'GREC representation:\n'
        for event in self.GREC_events:
            print event.ID,
            print '\t\tTrigger type: %s (%s)' % (event.trigger_type, ','.join(event.trigger_ID))
            print '\t\tTrigger text: %s'  % (event.trigger_text)
            print '\t\tTrigger span: %s:%s' % (event.start_offset, event.end_offset)

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
                if arg.start_offset != None:
                    print '\t\t\t%s: %s (%s:%s)' % (arg.name, arg.root, arg.start_offset, arg.end_offset)
                else:
                    print '\t\t\t%s: %s' % (arg.name, arg.root)

            print


    def print_mapped_GREC_representation(self):
        print 'Mapped GREC representation:\n'
        for event in self.mapped_GREC_events:
            print event.ID,
            print '\t\tTrigger type:'
            print '\t\tTrigger text: %s' % (event.trigger_text)
            print '\t\tTrigger span: %s:%s' % (event.start_offset, event.end_offset)
            print
            for role in event.thematic_roles:
                print '\t\tThematic role:'
                print '\t\tText:'
                print '\t\tText span: %s:%s' % (role.start_offset, role.end_offset)

                print
            print

# GREC event
class Event:
    def __init__(self, ID):
        self.ID = ID
        self.trigger_ID = None
        self.trigger_type = None
        self.trigger_text = None
        self.trigger_ID = None
        self.start_offset = None
        self.end_offset = None
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
    def __init__(self, name, root):
        self.name = name
        self.root = root
        self.start_offset = None
        self.end_offset = None

# mapped events
class MappedEvent:
    def __init__(self, ID, trigger_text, start_offset, end_offset):
        self.ID = ID
        self.trigger_type = None
        self.trigger_text = trigger_text 
        self.start_offset = start_offset
        self.end_offset = end_offset 
        self.thematic_roles = []

# mapped thematic roles
class MappedThematicRole:
    def __init__(self, start_offset, end_offset):
        self.role_type = None
        self.text = None
        self.ID = None
        self.start_offset = start_offset
        self.end_offset = end_offset

