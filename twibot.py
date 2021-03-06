import twitter
import urllib, cStringIO
import oauth2
import requests
from PIL import Image
import os
import ast

def oauth_req(url, http_method, post_body="", http_headers=None):
    consumer = oauth2.Consumer(key=os.environ['CONSUMER_KEY'], secret=os.environ['CONSUMER_SECRET'])
    token = oauth2.Token(key=os.environ['ACCESS_KEY'], secret=os.environ['ACCESS_SECRET'])
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url, method=http_method, headers=None)
    return content
    
def fetch_image(media_url):
	photo = oauth_req(media_url, 'GET') 

	file = cStringIO.StringIO(photo)
	img = Image.open(file)
	img.save('foto.jpg')


def get_real_text(prevText):
	
	text = prevText
	#Deleting media links from tweet
	while prevText.find('https://t.co') != -1:
		start_index = prevText.find('https://t.co')
		prevText = prevText[:start_index]


	#Check if the only text of the message was the media link
	text = prevText
	prevText = prevText.replace(' ', '')
	
	if len(prevText) == 0:
		text = messages[current]['text']

	return text

def fetch_gifVideo(media_url):
	urllib.urlretrieve(media_url, 'video.mp4')

if __name__ == '__main__':
	current = 0
	end = 0
	api = twitter.Api(consumer_key=os.environ['CONSUMER_KEY'],
	                  consumer_secret=os.environ['CONSUMER_SECRET'],
	                  access_token_key=os.environ['ACCESS_KEY'],
	                  access_token_secret=os.environ['ACCESS_SECRET'])

	lastTweet = api.GetHomeTimeline(count=1)
	messages = api.GetDirectMessages(return_json=True)

	text_last_tweet = get_real_text(lastTweet[0].text)
	
	for item in messages:
		text = get_real_text(item['text'])

		if text == text_last_tweet:
			break

		end += 1

	messages = messages[:end]
	messages = messages[::-1]

	while(current < len(messages)):
		prevText = messages[current]['text']
		mediaToPost = ""

		#Url from media
		try:
			media = messages[current]['entities']['media']
			media_type = media[0]['type']

			if media_type == 'photo':
				media_url = media[0]['media_url_https']
				fetch_image(media_url)
				mediaToPost = 'foto.jpg'
			elif media_type == 'animated_gif':
				media_url = media[0]['video_info']['variants'][0]['url']
				fetch_gifVideo(media_url)
				mediaToPost = 'video.mp4'
			elif media_type == 'video':
				media_url = media[0]['video_info']['variants'][1]['url']
				fetch_gifVideo(media_url)
				mediaToPost = 'video.mp4'

		except KeyError:
			pass

		if mediaToPost != "":
			text = get_real_text(prevText)
		else:
			text = prevText

		api.PostUpdate(status=text, media=mediaToPost)

		#Deleting media from disc
		if mediaToPost != "":
			os.remove(mediaToPost)

		current += 1
