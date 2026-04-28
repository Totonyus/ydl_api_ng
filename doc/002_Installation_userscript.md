# Userscript installation

## Plugin installation
Install [Greasemonkey (firefox)](https://addons.mozilla.org/fr/firefox/addon/greasemonkey/)
or [Tampermonkey (chrome)](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=fr)
 
## Add script
In the plugin dashboard, create a new userscript and copy the content of [userscript.js](../params/userscript.js).

## Configuration
### Mandatory configuration
You need to specify the url of your `ydl_api_ng` and your User token (if [user management](103_Users_management.md) is enabled)

```javascript
// CUSTOMIZE HERE
const default_host = 'http://localhost:5011';
const userToken = null;
// STOP CUSTOMIZE HERE
```

### Matching websites
By default, the userscript is only enabled on youtube.

```javascript
// @match       http*://www.youtube.com*/*
```

You can enable the userscript everywhere but it may create conflicts in some cases
```javascript
// @match       http*://*/*
```

Instead you can add your most common websites one by one : see [tampermonkey documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=include#meta:match)

### Presets

There is a few default presets present in the default userscript and you can modify anything you want !

```javascript
// CUSTOMIZE HERE
const routes = {};
const programmation_id = new URL(document.URL).pathname.replaceAll('/', '');
const presets_mapping = {};
const site_mapping = [];
// STOP CUSTOMIZE HERE
```

![Userscript in action](002_installation_userscript.jpg)
