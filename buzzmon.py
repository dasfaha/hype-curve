from __future__ import division
from collections import Counter
import dateutil.parser
import datetime
import feedparser
import nltk
from itertools import tee, islice
import json
import re
import sqlite3

#Pick a word and and plot it over time
#Remove marketing "stop words"

def ngrams(lst, n):
  tlst = lst
  while True:
    a, b = tee(tlst)
    l = tuple(islice(a, n))
    if len(l) == n:
      yield l
      next(b)
      tlst = b
    else:
      break
	  
def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    return re.sub(r'<[^>]*?>', '', value.encode('utf-8', 'ignore'))

def get_all():
	conn = sqlite3.connect('example.db')
	c = conn.cursor()	
	sources = c.execute('SELECT id, url from source')
	for s in sources:
		get_data(feed_url = s[1], id=s[0])
		
	
def get_data(feed_url, id):
	#TODO:
	#	- Get new articles since last update
	#   - store website name in database
	#feed_url = 'http://econsultancy.com/uk/blog.atom'
	
	feed = feedparser.parse(feed_url)
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	
	db_titles = list(c.execute("SELECT title FROM data WHERE source_id=" + str(id))) 
	existing_titles = [t[0].encode('ascii', 'ignore') for t in db_titles]
	
	for x in existing_titles:
		print x
		
	to_insert=[]
	for entry in feed.entries:
		#print entry, "-", feed	
		if entry['title'].encode('ascii', 'ignore') not in existing_titles:
			yourdate = dateutil.parser.parse(entry.updated.encode('ascii', 'ignore'))
			entry_date = str(yourdate.year)+"-"+str(yourdate.month).zfill(2) + "-"+ str(yourdate.day).zfill(2) + " " + str(yourdate.hour) + ":" + str(yourdate.minute) 
			post_content = strip_tags(entry.content[0].value.encode('ascii', 'ignore'))
			c.execute("INSERT INTO data (id, title, date, body, source_id) VALUES (?, ?, ?, ?, ?)", (None, entry['title'], entry_date, post_content, id))
			#to_insert.append(( entry.title.encode('ascii', 'ignore'), entry_date, entry.content[0].value.encode('ascii', 'ignore')))	
			
	print to_insert
	#cur.executemany("INSERT INTO buzzmon.data (title, date, body) VALUES ( %s, %s, %s)", to_insert) 
		
	conn.commit()
	conn.close()

def get_word_count(start_date, end_date, count=False):
	""" Get word count"""
	
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	
	if start_date and end_date:
		print "running with a restricted time period {0} -- {1} ".format(start_date, end_date)
		c.execute("SELECT body FROM DATA WHERE date >= ? and date <= ?", (start_date, end_date))
	else:
		c.execute("SELECT body FROM DATA")
	data = c.fetchall()
	
	all_text = ""
	for row in data:
		all_text += row[0].encode('ascii', 'ignore')
	
	if all_text: print "processed data"
	all_text = all_text.translate(None, '!?;":(),-.')
	all_text = all_text.lower()
	all_words = []
	all_words = all_text.split()
	no_stop_words = [ word for word in all_words if word not in nltk.corpus.stopwords.words('english') ]
	wc = Counter(no_stop_words)
	
	#caculate frequencies
	if not count:
		wdict = {}
		total_word_count = 0
		for k in wc.keys():
			total_word_count += wc[k]
			wdict[k] = wc[k]
		
		for k in wdict.keys():
			wdict[k] = wdict[k]/total_word_count
		
		wc = wdict
		
		
		
	return wc

def trend_word(word, start_date, freq='days', period=7):

	s_dte = datetime.datetime(*start_date)	
	if freq == 'days':
		delta = datetime.timedelta( days = int(period) )
	else:
		raise Exception("Implement me")
	e_dte = s_dte + delta
	
	word_trend = {}
	
	while 1:
		wrd_count = get_word_count(s_dte, e_dte, count=False)
		word_trend[s_dte] = wrd_count.get(word, "")
		s_dte = e_dte
		e_dte += delta
		
		#Breaking on this condition so that we don't include incomplete time periods 
		if e_dte > datetime.datetime.now():
			break
		
	return word_trend


	
def clean_up_dates():
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	
	c.execute("SELECT date FROM DATA")
	
	rgx_middle = re.compile('.*-([0-9]{1,1})-.*')
	rgx_end = re.compile('.*-([0-9]{1,1})\s+.*')
	
	dates = []
	
	for d in c:
		orig_date = d[0]
		new_date = orig_date
		
		m_middle = re.match(rgx_middle, orig_date)
		m_end = re.match(rgx_end, orig_date)
		
		if m_middle:
			new_date = new_date.replace('-' + m_middle.group(1) + '-', '-0' + m_middle.group(1) + '-')
		if m_end:
			print "there", m_end.group(1)
			new_date = new_date.replace('-' + m_end.group(1) + ' ', '-0' + m_end.group(1) + ' ')
		
		if orig_date != new_date:
			print "Original data: {0} - New date {1}".format(orig_date, new_date)	
		dates.append((new_date, orig_date))
		
	update_sql = "UPDATE data SET date=? WHERE date=?"
	
			
#clean_up_dates()



get_all()
#print "Running"
#mobile_trend = trend_word(word='mobile', start_date = (2013,2,1))	
#print mobile_trend	

#wc = get_word_count()	
#print "Most commong words:"
#print wc.most_common(10)


"""12:35
Count the number of words 

"""