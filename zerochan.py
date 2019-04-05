import urllib.request
import requests

import re

picsite = 'https://www.zerochan.net/{0}?s=random'


def get_pic(tag, attempts = 1):
	imagesource, err = __FindPic(tag)
	if imagesource == None:
		return err
	errors = []
	for i in range(attempts):
		image, err = __ExtractPic(imagesource)
		if image != None:
			return (imagesource, image)	
		errors.append(err)
	
	return "\n".join(errors)

def __FindPic(tag):
	try:
		with urllib.request.urlopen(picsite.format(tag)) as response:
			if response.status != 200:
				return None, "Site returned status %d" % response.status
			text = response.read().decode()
			text = text.split('<ul id="thumbs2">')[1]
			text = text.split('"')[1]
	except Exception as e:
		return None, f"Encountered error while finding pic:\n{e}"
	return 'https://www.zerochan.net' + text, None


def __ExtractPic(url):
	try:
		with urllib.request.urlopen(url) as response:
			if response.status != 200:
				print("Site returned status %d" % response.status)
				return None
			text = response.read().decode()
			text = text.split('&quot;')[3]
			text = text.replace('.240.', '.full.')
			print(text)
	except Exception as e:
		return None, f"Encountered error while extracting pic:\n{e}"
	return text, None
