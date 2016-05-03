# -*- coding: utf-8 -*-
"""
    unsub.py
    ~~~~~~~~~~~~
    Bulk unsubscribes email addresses using CSV file & the MailChimp 3.0 API
    :copyright: (c) 2016 by Nicolas Untz.
    :license: BSD, see LICENSE for more details.
"""

import config
import requests
import csv
import json
import hashlib


def get_lists():
    """Returns all the list IDs for the account with their name as the value.
    """
    r = requests.get('/'.join((config.BASE_URL, 'lists')),
                     auth=(config.USER, config.MC_API_KEY))
    lists = r.json()
    return dict([(l['id'], l['name']) for l in lists['lists']])


def get_member_pages(list_id):
    """Returns the pages of members for a list.
       The MailChimp API paginates the response.
    """
    offset = 0
    page_empty = False
    while not page_empty:
        payload = {'offset': str(offset), 'count': str(config.PAGE_SIZE)}
        r = requests.get('/'.join((config.BASE_URL, 'lists',
                                   list_id, 'members')),
                         params=payload, auth=(config.USER, config.MC_API_KEY))
        json_content = r.json()
        if len(json_content['members']) == 0:
            page_empty = True
        else:
            yield(json_content)
            offset += config.PAGE_SIZE


def get_subscriptions(list_ids):
    """Returns a dictionary of email addresses with the lists
       they are subscribed to.
    """
    subscriptions = {}
    for l in list_ids:
        for page in get_member_pages(l):
            for member in page['members']:
                subscriber = subscriptions.setdefault(member['email_address'],
                                                      [])
                subscriber.append({'list_id': l, 'status': member['status']})
    return subscriptions


def get_blacklist():
    """Returns a list of email addresses to unsubscribe.
       We only use the first column which contains the email addresses.
    """
    with open(config.BLACKLIST, 'rb') as csvfile:
        bl_reader = csv.reader(csvfile)
        return [row[0] for row in bl_reader]


def unsubscribe_member(list_id, email_address):
    """Unsubscribes a member.
    """
    hash = hashlib.md5(email_address.encode('utf-8')).hexdigest()
    data = {'status': 'unsubscribed'}
    r = requests.patch('/'.join((config.BASE_URL, 'lists', list_id,
                                 'members', hash)),
                       json.dumps(data),
                       auth=(config.USER, config.MC_API_KEY))
    status = r.json()['status']
    if status == 'unsubscribed':
        return True
    else:
        return False


lists = get_lists()
subscriptions = get_subscriptions(lists.keys())
blacklist = get_blacklist()

for b in blacklist:
    for s in subscriptions[b]:
        if s['status'] == 'subscribed':
            if unsubscribe_member(s['list_id'], b):
                print "UNSUBSCRIBED: {} <- {}".format(b, lists[s['list_id']])
            else:
                print "ERROR, CAN'T UNSUBSCRIBE{} <- {}".format(b,
                                                        lists[s['list_id']])
