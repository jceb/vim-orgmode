# -*- coding: utf-8 -*-

u"""
    Agenda
    ~~~~~~~~~~~~~~~~~~

    The agenda is one of the main concepts of orgmode. It allows to
    collect TODO items from multiple org documents in an agenda view.

    Features:
    * filtering
    * sorting
"""

from orgmode.liborgmode.agendafilter import filter_items
from orgmode.liborgmode.agendafilter import is_within_week_and_active_todo
from orgmode.liborgmode.agendafilter import contains_active_todo
from orgmode.liborgmode.agendafilter import contains_active_date
from orgmode.liborgmode.orgdate import OrgDateTime, OrgTimeRange
import datetime

def agenda_sorting_key(heading):
    orgtime = heading.active_date
    if orgtime is None or isinstance(orgtime, OrgDateTime):
        return orgtime
    if isinstance(orgtime, OrgTimeRange):
        return orgtime.start

    # It is an OrgDate. OrgDate cannot be compared with datetime-based Org* values by 
    # default, so it will be converted in such a way that:
    # * OrgDate value of _today_ will be displayed after today's passed events and before
    #   today's upcoming scheduled events.
    # * OrgDate value of a past day will be displayed after all other items of the same
    #   day.
    # * OrgDate value of a future day will be displayed before all other items of the same
    #   day.
    now = datetime.datetime.now()
    today = now.date()
    time_to_add = now.time() if today == orgtime else datetime.time(0, 0) if today < orgtime else datetime.time(23, 59)
    return datetime.datetime.combine(orgtime, time_to_add)

class AgendaManager(object):
    u"""Simple parsing of Documents to create an agenda."""
    # TODO Move filters in this file, they do the same thing

    def __init__(self):
        super(AgendaManager, self).__init__()

    def get_todo(self, documents):
        u"""
        Get the todo agenda for the given documents (list of document).
        """
        filtered = []
        for document in iter(documents):
            # filter and return headings
            filtered.extend(filter_items(document.all_headings(),
                                [contains_active_todo]))
        return sorted(filtered, key=agenda_sorting_key)

    def get_next_week_and_active_todo(self, documents):
        u"""
        Get the agenda for next week for the given documents (list of
        document).
        """
        filtered = []
        for document in iter(documents):
            # filter and return headings
            filtered.extend(filter_items(document.all_headings(),
                                [is_within_week_and_active_todo]))
        return sorted(filtered, key=agenda_sorting_key)

    def get_timestamped_items(self, documents):
        u"""
        Get all time-stamped items in a time-sorted way for the given
        documents (list of document).
        """
        filtered = []
        for document in iter(documents):
            # filter and return headings
            filtered.extend(filter_items(document.all_headings(),
                                [contains_active_date]))
        return sorted(filtered, key=agenda_sorting_key)
