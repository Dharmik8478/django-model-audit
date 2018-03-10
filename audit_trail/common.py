'''
Created on 03-Feb-2017

@author:dharmikp
'''

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) all added, removed and changed values keys.
    """
    def __init__(self, past_dict, current_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if str(self.past_dict[o]) != str(self.current_dict[o]))

    def get_diff(self):
        return {'added': self.added(), 'removed':self.removed(), 'changed': self.changed()}

