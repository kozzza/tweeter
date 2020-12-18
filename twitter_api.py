from discord_webhook import DiscordWebhook

from decouple import config
import tweepy
import json

auth = tweepy.OAuthHandler(config('API_KEY'), config('API_KEY_SECRET'))
auth.set_access_token(config('ACCESS_TOKEN'), config('ACCESS_TOKEN_SECRET'))

tweet_base_url = 'https://twitter.com/twitter/statuses/'

class MyStreamListener(tweepy.StreamListener):
    def __init__(self, api, webhook_url, ids):
        self.api = api
        self.me = api.me()
        self.webhook_url = webhook_url
        self.ids = ids
        self.account = []
        self.keywords = []

    def on_status(self, tweet):
        matching_keywords = all([keyword in tweet.text.lower() for keyword in self.keywords[0].split(' ')]) if self.keywords[0] else True
        if (tweet.user.id_str in self.account or not self.account[0]) and matching_keywords:
            tweet_content = f'{tweet_base_url+str(tweet.id)}'
            tweet_webhook = DiscordWebhook(url=self.webhook_url, content=tweet_content)
            notification_content = f'```{("+"+" +".join(self.keywords[0].split(" "))) if self.keywords[0] else "@"+tweet.user.screen_name}```<@{"> <@".join(self.ids)}>'
            notification_webhook = DiscordWebhook(url=self.webhook_url, content=notification_content)
            
            tweet_response = tweet_webhook.execute()
            notification_response = notification_webhook.execute()

    def on_error(self, status):
        print(status)
        print("Error detected")

class Streamer:
    def __init__(self, webhook_url, ids):
        print(webhook_url, ids)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.tweets_listener = MyStreamListener(self.api, webhook_url, [str(user_id) for user_id in ids])
        self.stream = tweepy.Stream(self.api.auth, self.tweets_listener)

    def set_filter(self, account, keywords):
        if account:
            account = [self.get_user_id(username) for username in account]
            self.tweets_listener.account = account
        else:
            self.tweets_listener.account = [account]
        self.tweets_listener.keywords = keywords if keywords else [None]
        self.stream.filter(track=keywords, follow=account, is_async=True, languages=['en'])
    
    def get_user_id(self, username):
        try:
            user_id = self.api.get_user(username)
            return user_id.id_str
        except tweepy.error.TweepError as e:
            return False