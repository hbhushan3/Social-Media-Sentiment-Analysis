from tweetanalysis import *

from flask import Flask, render_template, request
from flask_table import Table, Col

app = Flask(__name__)



# for adding initial table values in index.html - 2d array        
itemsI = [
    ('a', 'b', 'c'),
    ('d', 'd', 'd')
]

# initialize values in index.html
@app.route("/")
def index():
    objects = itemsI
    
    tAnalyzed = 2
    tTweets = 2
    tFirstPostDate = '12/12/2020'
    tLastPostDate = '11/11/2022'
    return render_template('index.html', **locals())


# After clicking submit button, change values
@app.route("/predict", methods =['POST','GET'])
def predict():
    username = request.form['twitterUserName']
    

    tweet_strs = scrapeTweets(username, 50)

    avg_phrase_sentiments = analyzeTweetStrings(tweet_strs)

    # Convert thedictionary to a 2d table where each row is a tuple

    itemsF = []

    for phrase, info in avg_phrase_sentiments.items():
        polarity_num = round(info[0], 1)
        confidence_num = round(info[1], 1)
        num_times_referenced = info[2]

        polarity_str = str(polarity_num)
        confidence_str = str(confidence_num)
        # num_times_referenced_str = str(info[2])

        if polarity_str == '-0.0':
            polarity_str = '0.0'
        if confidence_str == '-0.0':
            confidence_str = '0.0'

        itemsF.append((phrase, polarity_str, confidence_str, num_times_referenced))

    itemsF = sorted(itemsF, key=lambda row: -row[3])
    
    objects = itemsF
    
    tAnalyzed = 5
    tTweets = 5
    tFirstPostDate = '12/12/2020'
    tLastPostDate = '11/11/2022'
    
    # return locals - all local vars within scope
    return render_template('index.html', **locals()) 

if __name__ == '__main__':
     app.run(host='0.0.0.0',port=5000)