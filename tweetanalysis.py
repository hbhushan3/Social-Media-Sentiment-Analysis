import tweepy, config, re, statistics
from pattern.en import parse, parsetree, sentiment


# This part somehow solves an SSL exception encountered by NLTK.
import ssl
try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	pass
else:
	ssl._create_default_https_context = _create_unverified_https_context



# returns a list of strings of the text in @user_handle's latest num_tweets_to_fetch tweets
def scrapeTweets(user_handle, num_tweets_to_fetch):
	client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

	user_id = client.get_user(username=user_handle.replace('@', '')).data.id
	tweet_objs = client.get_users_tweets(id=user_id, exclude=['retweets', 'replies'], max_results=num_tweets_to_fetch).data

	# tweet strings
	tweet_strs = []

	for tweet_obj in tweet_objs:
		tweet_str = tweet_obj.text
		# remove the hyperlinks to images and videos
		tweet_str = re.sub("https://t.co/.*$", "", tweet_str)
		# remove mentions (e.g. "I love you @jeffbezos!")
		tweet_str = re.sub("@\w.*", "", tweet_str)
		# remove hashtags
		tweet_str = re.sub("#\w.*", "", tweet_str)

		tweet_strs.append(tweet_str)

	return tweet_strs



# Returns a {phrase : polarity} dictionary
def analyzeTweetStrings(tweet_strs):
	# key = phrase (short sequence of contiguous or mostly contiguous words that belong together)
	# value = list of sentiments (floats) where each sentiment is calculated from a Tweet that uses that phrase
	phrase_sentiments = {}

	for tweet_str in tweet_strs:
		# index 0 is for sentiment polarity, 1 is for confidence score
		tweet_polarity, polarity_confidence = sentiment(tweet_str)
		
		# need to filter out the non-"conent" words like pronouns, prepositions, quantifiers, certain verbs, etc.
		# https://gist.github.com/nlothian/9240750
		
		content_chunk_tags = ['NP'] # only look at chunks with these tags
		to_remove_tags = ['PRP$', 'JJ', 'DT'] # remove words with these tags from the chunks we keep

		parsed = parsetree(tweet_str)

		for sentence in parsed:
			for chunk in sentence.chunks:
				if chunk.type in content_chunk_tags:
					content_words = [w.string for w in chunk.words]

					# Clean up the chunk by removing generic words in order to identify common phrases between tweets said phrases being intepreted as distinct phrases to to additional words unique to the tweet.
					for w in chunk.words:
						if w.type in to_remove_tags:
							content_words.remove(w.string)

					# TODO: check if uncapitalized words and n-grams are proper nouns (e.g. by checking if there's a Wikipedia page for it that uses the capitalized version in the body text). If so, capitalize them so they will be detected as proper nouns.

					# The chunk must contain at least one proper noun to be considered a "content phrase".
					found_proper_noun = False
					for w_str in content_words:
						# [first sentence][first "info" tuple][tag]
						if parse(w_str).split()[0][0][1] in ('NNP', 'NNPS'):
							found_proper_noun = True
							break
					
					if found_proper_noun:
						new_phrase = ''.join([w.lower() + ' ' for w in content_words])
						
						if new_phrase in phrase_sentiments.keys():
							phrase_sentiments[new_phrase][0].append(tweet_polarity)
							phrase_sentiments[new_phrase][1].append(polarity_confidence)
						else:
							phrase_sentiments[new_phrase] = [[tweet_polarity], [polarity_confidence]]

	# return the averaged out sentiments
	return {phrase : [statistics.mean(info[0]), statistics.mean(info[1]), len(info[0])] for phrase, info in phrase_sentiments.items()}
		


if __name__ == '__main__':
	sample_tweet_strs = [
		"Say what you will about Ariana Grande as a person, but Ariana Grande's song YYFPA is sooooo good!!!",
		"I kind of like Ariana Grande's music.",
		"Ariana Grande's new album is an pretty good! I really love the song GORRPHF. It has such a catchy beat.",
		"Ariana Grande is quite often a big nasty bitch.",
		"I hate Ariana Grande.",
		"Coca-Cola tastes amazing like heaven.",
		"What's your favorite soda? Mine is Coca-Cola. I love Coca-Cola."
	]

	real_tweet_strs = scrapeTweets('barackobama', 5)

	avg_phrase_sentiments = analyzeTweetStrings(real_tweet_strs)

	for phrase, info in avg_phrase_sentiments.items():
		print(phrase + ' ' + str(info[0])[:4] + ' ' + str(info[1]))
	

