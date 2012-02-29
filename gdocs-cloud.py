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

def ProcessFeed(feed):
  feed = client.GetResources(feed)
  print '\n'
  if not feed.entry:
    print 'No entries in feed.\n'
  for entry in feed.entry:
    if entry.get_resource_type() == 'document':
      print entry.title.text
      filename = files + entry.id.text.split('/')[5] + '.html'
      print filename
      if r.sadd("filenames", filename):
        client.download_resource(entry, filename) # is this synchronous?

def ScrapeFiles():
  for filename in r.smembers("filenames"):
    if filename not in r.smembers("scraped_files"):
      try:
        f = open(filename, 'r').read()
        r.sadd("scraped_text", f)
        r.sadd("scraped_files", filename)
        f.close()
      except:
        print 'error scraping file: '+filename
  print r.smembers("scraped_files")
  print r.smembers("scraped_text")

ProcessFeed('https://docs.google.com/feeds/default/private/full/folder%3A0B_k36WQYssQgYzU2NTcwNDYtZWZmOC00NTY2LWI2MzAtNTEwZDE0ZmJkNTVj/contents')
ScrapeFiles()