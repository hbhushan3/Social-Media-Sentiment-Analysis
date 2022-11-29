from tweetanalysis import *

from flask import Flask, render_template, request
from flask_table import Table, Col

app = Flask(__name__)

# for adding initial table values in index.html - 2d array        
itemsI = [('Help', 0.5, 0.7),
         ('Car', 0.8, 0.9)]

# initialize values in index.html
@app.route("/")
def index():
    objects = itemsI
    
    tAnalyzed = 2
    tTweets = 2
    tFirstPostDate = '12/12/2020'
    tLastPostDate = '11/11/2022'
    return render_template('index.html', **locals())

# for adding final values to table in index.html - 2d array        
# itemsF = [('Name1', 'Description1', 'Conf1'),
#          ('Name2', 'Description2', 'Conf2'),
#          ('Name3', 'Description3', 'Conf3')]

# After clicking submit button, change values
@app.route("/predict", methods =['POST','GET'])
def predict():
    username = request.form['twitterUserName']
    
    # for testing values in 2d array
    # for p in items:
    #     for z in p:
    #         print ("lol ", z)

    tweet_strs = scrapeTweets(username, 5)

    avg_phrase_sentiments = analyzeTweetStrings(tweet_strs)

    # Convert thedictionary to a 2d table where each row is a tuple
    itemsF = [(phrase, str(sentiment)[:3]) for phrase, sentiment in avg_phrase_sentiments.items()]
    
    objects = itemsF
    
    tAnalyzed = 5
    tTweets = 5
    tFirstPostDate = '12/12/2020'
    tLastPostDate = '11/11/2022'
    
    # return locals - all local vars within scope
    return render_template('index.html', **locals()) 

if __name__ == '__main__':
     app.run(host='0.0.0.0',port=5000)