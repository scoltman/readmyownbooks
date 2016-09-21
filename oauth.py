# oauth example for goodreads
#
# based on code found in https://gist.github.com/gpiancastelli/537923 by Giulio Piancastelli
#
# edit script with your dev key and secret
# run it
# visit the url
# confirm that you have accepted
# write down token!
#

import oauth2 as oauth
import urllib
import urlparse
import config

url = 'http://www.goodreads.com'
request_token_url = '%s/oauth/request_token' % url
authorize_url = '%s/oauth/authorize' % url
access_token_url = '%s/oauth/access_token' % url

consumer = oauth.Consumer(key=config.CONSUMER_KEY,
                          secret=config.CONSUMER_SECRET)

client = oauth.Client(consumer)

response, content = client.request(request_token_url, 'GET')
if response['status'] != '200':
    raise Exception('Invalid response: %s, content: ' % response['status'] + content)

request_token = dict(urlparse.parse_qsl(content))

authorize_link = '%s?oauth_token=%s' % (authorize_url,
                                        request_token['oauth_token'])
print "Use a browser to visit this link and accept your application:"
print authorize_link
accepted = 'n'
while accepted.lower() == 'n':
    # you need to access the authorize_link via a browser,
    # and proceed to manually authorize the consumer
    accepted = raw_input('Have you authorized me? (y/n) ')

token = oauth.Token(request_token['oauth_token'],
                    request_token['oauth_token_secret'])

client = oauth.Client(consumer, token)
response, content = client.request(access_token_url, 'POST')
if response['status'] != '200':
    raise Exception('Invalid response: %s' % response['status'])

access_token = dict(urlparse.parse_qsl(content))

# this is the token you should save for future uses
print 'Save this for later: '
print 'oauth token key:    ' + access_token['oauth_token']
print 'oauth token secret: ' + access_token['oauth_token_secret']

token = oauth.Token(access_token['oauth_token'],
                    access_token['oauth_token_secret'])


#
# As an example, let's add a book to one of the user's shelves
#
add_to_list = False

def addABook():
    client = oauth.Client(consumer, token)
    # the book is: "Generation A" by Douglas Coupland
    body = urllib.urlencode({'name': 'to-read', 'book_id': 6801825})
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response, content = client.request('%s/shelf/add_to_shelf.xml' % url,
                                   'POST', body, headers)
    # check that the new resource has been created
    if response['status'] != '201':
        raise Exception('Cannot create resource: %s' % response['status'])
    else:
        print 'Book added!'


if add_to_list:
    addABook()

## END ##
