import requests
import requests.auth
import praw
import re
import emoji
from textblob import TextBlob
import pandas as pd


# user information and auth info

user_id = 'kaythomedu'
user_pass = None
client_id = 'Ww1gfcX500dqWg'
secret = 'YiQCz4XAinioTTO0Xczzk5lITV25tQ'
user_agent = 'User-Agent:com.example.politicsresearch:v1.0.0 (by u/kaythomedu)'

client_auth = requests.auth.HTTPBasicAuth(client_id, secret)

# initializing Reddit 
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=secret,
    user_agent=user_agent)

# Cleaning
def clean(x):
    x = re.sub(r'https?:\/\/.*[\r\n]*', '', x)
    x = re.sub(r'#', '', x) # remove hashtag
    x = re.sub(r'u/[A-Za-z0-9]+', '', x) # remove reference to other users
    x = re.sub(r'\*', '', x)
    x = emoji.replace_emoji(x, '')
    return x

# assign subreddit
subreddit = reddit.subreddit('politics')

# searching for top posts within the last year that match the search query on the assigned subreddit
counter = 0
all_comms = []
posts = []
for post in subreddit.top(time_filter='year'):
    print(str(post.id) + '  ' + str(post.created_utc) + '  ' + str(post.title) + '\n')
    post.comment_sort = 'top'
    post.comments.replace_more(limit=None)
    posts.append((post.id, posts.title))
    # collecting and cleaning comments from each post
    all_comments = []
    for init_comment in post.comments.list():
        comm_body = clean(init_comment.body)
        blob_text = TextBlob(comm_body)
        all_comments.append((init_comment.author, 
        init_comment.id, 
        init_comment.body, 
        init_comment.link_id, #link id tracks the post a user comments on
        blob_text.polarity)) # polarity is positive or negative sentiment, -1 negative, +1 postitive
    print(len(all_comments))
    all_comms.append(all_comments)
    counter += 1
    if counter == 50:
        break

# preparing for dataframe

post_id = []
post_title = []

for post in posts:
    for id, title in post:
        post_id.append(id)
        post_title.append(title)

orig_post_info = {'post_id' : post_id, 'title' : post_title}

author = []
author_id = []
comment_text = []
orig_post_id = []
sentiment = []
for comm in all_comms:
    for author_name, id, body, post_id, sentiment_score in comm:
        author.append(author_name)
        author_id.append(id) 
        comment_text.append(body) 
        orig_post_id.append(post_id) 
        sentiment.append(sentiment_score)

commenter_info = {'author' : author, 
'author_id' : author_id, 
'comment' : comment_text, 
'post_id' : orig_post_id, 
'sentiment' : sentiment}

# create dataframes and save as csv
orig_post_df = pd.DataFrame(orig_post_info)
all_comms_df = pd.DataFrame(commenter_info)

orig_post_df.to_csv('reddit_posts.csv')
all_comms_df.to_csv('reddit_comments.csv')