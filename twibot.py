import twitter
import urllib, cStringIO
import oauth2
import requests
from PIL import Image
import os
import ast

def oauth_req(url, http_method, post_body="", http_headers=None):
    consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth2.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
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
	print 'Limpiando: ' + prevText
	#Eliminando los hipervinculos del texto
	while prevText.find('https://t.co') != -1:
		start_index = prevText.find('https://t.co')
		prevText = prevText[:start_index]

	#En caso de que se adjunte solo como texto un link a una imagen, para que no crashee
	text = prevText
	prevText = prevText.replace(' ', '')
	
	print len(prevText)

	if len(prevText) == 0:
		text = messages[current]['text']

	return text

def fetch_gifVideo(media_url):
	video = oauth_req(media_url, 'GET') 

	file_name = 'video.mp4'
	file = open(file_name,'wb')
	file.write(video)
	file.close()

if __name__ == '__main__':
	current = 0
	end = 0
	api = twitter.Api(consumer_key=CONSUMER_KEY,
	                  consumer_secret=CONSUMER_SECRET,
	                  access_token_key=ACCESS_KEY,
	                  access_token_secret=ACCESS_SECRET)

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

		text = get_real_text(prevText)

		#Url from media
		try:
			media = messages[current]['entities']['media']
			media_type = media[0]['type']

			if media_type == 'photo':
				media_url = media[0]['media_url_https']
				fetch_image(media_url)
				mediaToPost = 'foto.jpg'
			else:
				media_url = media[0]['video_info']['variants'][0]['url']
				fetch_gifVideo(media_url)
				mediaToPost = 'video.mp4'

		except KeyError:
			pass

		api.PostUpdate(status=text, media=mediaToPost)

		#Deleting media from disc
		if mediaToPost != "":
			os.remove(mediaToPost)

		current += 1
