# -*- coding: utf-8 -*-

"""
    OrgDate
    ~~~~~~~~~~~~~~~~~~

    This module contains all date representations that exist in orgmode.

    Types a date can be
    * date
    * datetime
    * timerange

    They can be active or inactive
"""


def get_orgdate():
    """
    parse the given text and return an OrgDate if text contains a string
    representation of an OrgDate.
    """
    pass


class OrgDate(object):
    """
    OrgDate represents a normal date like '2011-08-29 Mon'.

    OrgDates can be active or inactive

    """
    def __init__(self, arg):
        super(OrgDate, self).__init__()
        self.arg = arg


# vim: set noexpandtab:
