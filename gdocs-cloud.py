import gdata.docs.data
import gdata.docs.client
import gdata.auth
import os
import redis
import lxml.html


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

# http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
# class MLStripper(HTMLParser):
#     def __init__(self):
#         self.reset()
#         self.fed = []
#     def handle_data(self, d):
#         self.fed.append(d)
#     def get_data(self):
#         return ' '.join(self.fed)

def strip_tags(html):
  string = ''
  html = lxml.html.fromstring(html)
  string += html.cssselect('title')[0].text_content() + ' '
  string += html.cssselect('body')[0].text_content() + ' '
  return string
    # s = MLStripper()
    # s.feed(html)
    # return s.get_data()

def ScrapeFiles():
  
  for filename in r.smembers("filenames"):
    if filename not in r.smembers("scraped_files"):
      print 'scraping ' + filename
      f = open(filename, 'r')
      text = strip_tags(f.read())
      
      r.sadd("scraped_text", text)
      r.sadd("scraped_files", filename)
      f.close()
  
  output_file = open(files + 'output.txt', 'a')
  for string in r.smembers("scraped_text"): output_file.write(string)
  output_file.close()


ProcessFeed('https://docs.google.com/feeds/default/private/full/folder%3A0B_k36WQYssQgYzU2NTcwNDYtZWZmOC00NTY2LWI2MzAtNTEwZDE0ZmJkNTVj/contents')
ScrapeFiles()

