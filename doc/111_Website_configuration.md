## Site management

You can define parameters for given websites.

`_playlist_indicators` is used to know if the URL is a playlist : it's useful in case `yt-dlp` fails to detect the url
is a playlist

```
# Every host matching this site
_hosts = www.youtube.com,youtu.be
# How to define the url is a video 
_video_indicators = /watch?
# How to define the url is a playlist
_playlist_indicators = ?list=,&list=,/user/,/playlists
```

You can also add parameters tied to the site like login information