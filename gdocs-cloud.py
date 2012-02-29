import gdata.docs.data
import gdata.docs.client
import gdata.auth
import os
import redis
import re

r = redis.StrictRedis()

client = gdata.docs.client.DocsClient(source='cfaphl-gdocscloud-v1')
client.ssl = True
client.http_client.debug = False

files = os.getcwd()+'/files/'

if not os.path.exists(files):
    os.makedirs(files)

if r.get('token'):
  client.auth_token = gdata.gauth.ClientLoginToken(r.get('token')) # https://code.google.com/apis/gdata/docs/auth/clientlogin.html#RecallAuthToken
  print 'token found: ' + r.get('token')
else:
  print 'no token'
  user = raw_input('User: ')
  pwd = raw_input('Pass: ')
  try:
    client.ClientLogin(user, pwd, client.source)
    r.set('token', client.auth_token.token_string)
    print 'token' + str(r.get('token'))
  except:
    exit('Error logging in')

def PrintFeed(feed):
  feed = client.GetResources(feed)
  print '\n'
  if not feed.entry:
    print 'No entries in feed.\n'
  for entry in feed.entry:
    print entry.title.text
    filename = files + '/' + entry.id.text.split('/')[5] + '.html'
    print filename
    r.sadd("filenames", filename)
    client.download_resource(entry, filename)

PrintFeed('https://docs.google.com/feeds/default/private/full/folder%3A0B_k36WQYssQgYzU2NTcwNDYtZWZmOC00NTY2LWI2MzAtNTEwZDE0ZmJkNTVj/contents')



