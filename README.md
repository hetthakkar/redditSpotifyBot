# redditSpotifyBot
Bot that creates spotify playlists from the comments in a reddit thread

Call the bot using "!createSpotifyPlaylist"

When called, the bot first scans all the top level comments in the thread.
For each line in the comment, 
  <ol>
  <li> Create a Spotify playlist with the name of the post. The playlist ID is stored and indexed on the submission ID of the post.</li>
  <li> Check if the text was meant to be a track by matching it with the regular expression defined. Basically checks for "artist/track - artist/track" </li>
  <li> The search query in Spotify must be made with a track/album parameter. To determine whether the given text is for a track or an album, check for "EP", "Album", "Remixes" in the text. </li>
  <li> When searching for albums, Spotify sometimes returns the title track as a single. To avoid this, the query results are iterated until album with more than 1 track is found. </li>
  <li> The track IDs are stored in a list indexed by the playlist ID to avoid duplicate tracks. </li>
  
  </ol>
All the comments in the subreddit are streamed. When a comment matching a requested post is found, the track is added to its appropriate playlist
  
 <hr>
 To be done:  
 <ol>
 <li> Work for multiple threads simultaneously </li>
 <li> <TT>subreddit.stream</TT> and <TT>submission.comments</TT> straight up don't work sometimes when all the comments are by one user. (Hard to replicate) </li>
 <li> Improve the regular expression to add more special charaters and symbols </li>
 <li> Error checking on API calls to avoid code termination</li>
 </ol>
  

