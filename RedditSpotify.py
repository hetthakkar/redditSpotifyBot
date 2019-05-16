
# coding: utf-8

# In[2]:


import spotipy
import spotipy.util as util
import praw
import re
import json
import threading
import time
import os


# In[3]:



# Spotify Credentials
username = os.environ['s_username']
scope = os.environ['s_scope']
client_id = os.environ['s_client_id']
client_secret = os.environ['s_client_secret']


reddit = praw.Reddit(client_id=os.environ['r_client_id'],
                     client_secret=os.environ['r_client_secret'],
                     password=os.environ['r_password'],
                     user_agent=os.environ['r_user_agent'],
                     username=os.environ['r_username'])


done_posts = [] # Keep track of submissions processed
curr_playlists  = [] # IDs of the playlists created
playlist_dict = {} # A map from submission ID -> playlist ID
subreddit = reddit.subreddit('EDM')
global playlist_tracks # Store all the tracks present in a playlist to avoid duplicates
playlist_tracks = {}

# Extract track title and search query from comment. Also determine whether it is a single or an album/EP
def determine_type(track):
    match0 = re.findall('[a-zA-Z&()Öö,Ää\'0-9_ ]* - [a-zA-Z&()Öö,Ää\'0-9_ ]*', track) # Check if comment has a valid track
    match1 = re.findall('[a-zA-Z&()Øø,Ää\'0-9_ ]*-[a-zA-Z&()Øø,Ää\'0-9_ ]*', track)
    
    if(match0):
        match = match0
    elif(match1):
        match = match1
    else:
        match = []
    
    if(not match):
        return -1,''
    track = match[0]
    before = track[:]
    track = track.replace('(EP)','')
    track = track.replace('(Album)','')
    track = track.replace('EP','')
    track = track.replace('Album','')
    track = track.replace('album','')
    track = track.replace('(album)','')
    if(track == before and (track.lower().find('remixes') < 0)): # Text does not contain EP/Album/Remixes keyword, then it is not a single
        return 0,track
    else:
        return 1,track


# Add track to its proper playlist from the given comment
def parse_comment(text, sp, playlist_id, username):
    
    global playlist_tracks
    tracks = text.split('\n')
    c = 0
    for track in tracks:

        print('For c = ' + str(c) + ' Processing track ' + track)
        c += 1
        if(track == ''):
            continue
        val, text = determine_type(track)
        
        if(val < 0):
            print('Not a track')
            return -1
        
        if(not text):
            continue
            
        print('Searching for : ' + text)
        if(val == 0): # Track is a single

            print('adding track')
            results = sp.search(q=text, type='track', limit = 10)
            
            if(not results['tracks']['items']):
                print('Could not find track - ' + text)
                return -1
                
            track_uri = results['tracks']['items'][0]['uri'] 
            if(track_uri not in playlist_tracks[playlist_id]):
                sp.user_playlist_add_tracks(user = username, playlist_id = playlist['id'], tracks = [track_uri], position=None)
                playlist_tracks[playlist_id].append(track_uri)
                
            else:
                print('Repeated track - ' + text)
                return -2
            
        else: 
            
            print('adding EP/Album')
            results = sp.search(q=text , type = 'album')
            
            if(not results['albums']['items']):
                print('Could not find album/ep - ' + text)
                return -1
            
            n_album_tracks = -1
            it = 0

            # Sometimes spotify returns title track single as an album. Iterate through the results until an album with more than 1 track is found
            while(n_album_tracks < 2):
                album_uri = results['albums']['items'][it]['uri']
                album_tracks = sp.album_tracks(album_uri, limit=50, offset=0)
                n_album_tracks = len(album_tracks['items'])
                it += 1
            
            for i in range(n_album_tracks):
                        
                track_uri = album_tracks['items'][i]['uri']
                if(track_uri not in playlist_tracks[playlist_id]):
                    sp.user_playlist_add_tracks(user = username, playlist_id = playlist_id, tracks = [track_uri], position=None)
                    playlist_tracks[playlist_id].append(track_uri)


        
if __name__ == "__main__":
    
    global sp

    token = util.prompt_for_user_token(username = username, scope = scope, client_id=client_id, client_secret=client_secret, redirect_uri = 'http://localhost:8888')
    sp = spotipy.Spotify(auth = token)
    
    print('Started Streaming')
    for comment in subreddit.stream.comments(skip_existing=True):


        print('Caught comment' + comment.body)
        # Check for expired token by a test search
        try:
            
            results = sp.search(q='Sp - test', type='track', limit = 10)
            
        except:
            
            token = util.prompt_for_user_token(username = username, scope = scope, client_id=client_id, client_secret=client_secret, redirect_uri = 'http://localhost:8888')
            sp = spotipy.Spotify(auth = token)
            
        if((comment.body == '!createSpotifyPlaylist') and (comment.link_id[3:] not in done_posts)):

            done_posts.append(comment.link_id[3:])
            submission = comment.submission

            playlist = sp.user_playlist_create(user=username, name = submission.title)
            print('created playlist with title ' + submission.title)

            curr_playlists.append(playlist['id'])

            playlist_dict[comment.link_id[3:]] = playlist['id']
            playlist_tracks[playlist['id']] = []

            for top_level_comment in submission.comments:

                parse_comment(top_level_comment.body, sp, playlist['id'], username)
                time.sleep(1)


            comment.reply('Created Playlist. URL : ' + playlist['external_urls']['spotify'])

        elif( (comment.link_id[3:] in done_posts) and (comment.link_id == comment.parent_id)):

            print('Processing c')
            parse_comment(comment.body, sp, playlist_dict[comment.link_id[3:]], username)

