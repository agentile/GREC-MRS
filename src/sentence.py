class Sentence:
    def __init__(self, filename, ID, text):
        self.filename = filename
        self.ID = ID
        self.text = text
        self.terms = []
        self.events = []
