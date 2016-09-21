#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import Template
import oauth2 as oauth
import urlparse
import urllib
import time
import xml.dom.minidom
import sys, getopt
import config

url = 'http://www.goodreads.com'
consumer = oauth.Consumer(key=config.CONSUMER_KEY,
                          secret=config.CONSUMER_SECRET)
token = oauth.Token(config.ACCESS_TOKEN,config.ACCESS_TOKEN_SECRET)
client = oauth.Client(consumer, token)

#############################
#
# who are we?
#
def getUserId():
    response, content = client.request('%s/api/auth_user' % url,'GET')
    if response['status'] != '200':
        raise Exception('Cannot fetch resource: %s' % response['status'])
#    else:
#        print 'User loaded.'

    userxml = xml.dom.minidom.parseString(content)
    user_id = userxml.getElementsByTagName('user')[0].attributes['id'].value
    return str(user_id)


#############################
#
# fetch xml for a page of books on a shelf
#
def getShelfBooks(page, shelf_name):
    owned_template = Template('${base}/review/list?format=xml&v=2&id=${user_id}&sort=author&order=a&key=${dev_key}&page=${page}&per_page=100&shelf=${shelf_name}')

    body = urllib.urlencode({})
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    request_url = owned_template.substitute(base=url, user_id=user_id, page=page, dev_key='gYPjS9uMjMC5CnWuSohlw', shelf_name=shelf_name)
    response, content = client.request(request_url, 'GET', body, headers)
    if response['status'] != '200':
        raise Exception('Failure status: %s for page ' % response['status'] + page)
#    else:
#        print 'Page loaded!'
    return content


#############################
#
# grab id and title from a <book> node
#
def getBookInfo(book):
    book_id = book.getElementsByTagName('id')[0].firstChild.nodeValue
    book_title = book.getElementsByTagName('title')[0].firstChild.nodeValue
    return book_id, book_title



#############################
#
# grab id and title from a <book> node
#
def addBookToList(book_id, shelf_name):
    body = urllib.urlencode({'name': shelf_name, 'book_id': book_id})
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response, content = client.request('%s/shelf/add_to_shelf.xml' % url,'POST', body, headers)

    if response['status'] != '201':
        raise Exception('Failure status: %s' % response['status'])
#    else:
#        print 'Book added!'
    return True


#############################
#
# loop over each page of owned books
#     loop over each book
#         add book to list
#
user_id = getUserId()

current_page = 0
total_books = 0
owned_books = []
while True:
    current_page = current_page + 1

    content = getShelfBooks(current_page, 'owned')
    xmldoc = xml.dom.minidom.parseString(content)

    page_books = 0
    for book in xmldoc.getElementsByTagName('book'):
        book_id , book_title = getBookInfo(book)
        owned_books.append(book_id)
        page_books += 1
        total_books += 1

    if (page_books == 0):
        break;

print 'I own ' + str(total_books) + ' books.'

current_page = 0
total_owned_and_read_books = 0;

while True:
    current_page = current_page + 1

    content = getShelfBooks(current_page, 'read')
    xmldoc = xml.dom.minidom.parseString(content)

    page_books = 0
    for book in xmldoc.getElementsByTagName('book'):
        book_id , book_title = getBookInfo(book)
        page_books += 1
        if(book_id in owned_books):
            total_owned_and_read_books += 1


    if (page_books == 0):
        break;

print str(total_owned_and_read_books) + ' of which I have read.'
print 'That’s ' + str(int(((float(total_owned_and_read_books) / float(total_books)) * 100))) + '% read.'


## END ##
