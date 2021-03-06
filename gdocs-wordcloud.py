'''
This haxx0red app scrapes a given folder in google docs and builds a txt file suitable for feeding into a word cloud generator like:
* http://tagul.com/api
* http://www.wordle.net
* www.tagxedo.com/app.html
v 1.?
a Yuletide #cfaPHL production
requires a running redis instance
'''

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

if r.get('gdocs-wordcloud:token'):
  client.auth_token = gdata.gauth.ClientLoginToken(r.get('gdocs-wordcloud:token')) # https://code.google.com/apis/gdata/docs/auth/clientlogin.html#RecallAuthToken
  print 'token found: ' + r.get('gdocs-wordcloud:token')
else:
  print 'no token'
  user = raw_input('User: ')
  pwd = raw_input('Pass: ')
  try:
    client.ClientLogin(user, pwd, client.source)
    r.set('gdocs-wordcloud:token', client.auth_token.token_string)
    print 'token' + str(r.get('gdocs-wordcloud:token'))
  except:
    exit('Error logging in')

feed = get_folder_feed()
if feed != r.get('gdocs-wordcloud:feed'): # new feed
  r.delete('gdocs-wordcloud:filenames')
  r.delete('gdocs-wordcloud:scraped_text')
  r.delete('gdocs-wordcloud:scraped_files')
  r.set('gdocs-wordcloud:feed', feed)
process_feed(feed)
scrape_files()


def get_folder_feed():
  feed = client.GetResources('https://docs.google.com/feeds/default/private/full/-/folder?showroot=true') #show all folders
  for (i, entry) in enumerate(feed.entry):
    print str(i) + ': ' + entry.title.text # i really should learn python string substitutions... later
  folder_index = raw_input('enter index of folder to scrape: ')
  return feed.entry[int(folder_index)].content.src

def process_feed(feed):
  feed = client.GetResources(feed)
  print '\n'
  if not feed.entry:
    print 'No entries in feed.\n'
  for entry in feed.entry:
    if entry.get_resource_type() == 'document':
      print entry.title.text
      filename = files + entry.id.text.split('/')[5] + '.html'
      print filename
      if r.sadd('gdocs-wordcloud:filenames', filename):
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

def scrape_files():
  output_string = ''
  for filename in r.smembers('gdocs-wordcloud:filenames'):
    if filename not in r.smembers('gdocs-wordcloud:scraped_files'):
      print 'scraping ' + filename
      f = open(filename, 'r')
      text = strip_tags(f.read())
      
      r.sadd('gdocs-wordcloud:scraped_text', text)
      r.sadd('gdocs-wordcloud:scraped_files', filename)
      f.close()
  
  for string in r.smembers('gdocs-wordcloud:scraped_text'): output_string += string
  output_file = open(files + 'output.txt', 'w') # overwrite any existing file
  output_file.write(output_string)
  output_file.close()
  print 'successfully wrote word cloud text to ' + files + 'output.txt'


