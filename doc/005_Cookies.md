# Cookies

For obvious reasons the `yt-dlp` `--cookies-from-browser` is not available but there is still two ways to manage cookies
for `ydl_api_ng`

##  Persistent storage
You can export your cookies from a private session and put them in a file in the `/app/persistant_cookies/`.

Then you can tell `yt-dlp` what cookies file to use

Example :
```
cookiefile = /app/persistant_cookies/youtube
```

## Post requests

For the : `/download` and `/extract_info` : you can provide a cookie directly in the POST body :

Example : 
```
POST {{host}}/extract_info?url=https://www.youtube.com/watch?v=a0sxBO9HZ-M
Content-Type: application/json

{
  "cookies": "URL encoded (RFC3986 format) netscape cookies format"
}
```

The cookies sent this way are deleted at the end of the execution.