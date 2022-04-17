// ==UserScript==
// @name        ydl_api_ng
// @match       http*://*/*
// @grant       GM_registerMenuCommand
// @grant       GM_xmlhttpRequest
// @grant       GM_notification
// ==/UserScript==

(function () {
    'use strict';

    // ---%--- REPLACE ---%--- your host and token here
    const default_host = 'http://localhost:5011/download';
    const userToken = null;
    const notificationTimeout = 5000;

    const preset_list = [
        {name: 'Default', key: '1', host: default_host, params: {}},
        {name: 'Best', key: '2', host: default_host, params: {presets: 'BEST'}},
        {name: '720p', key: '3', host: default_host, params: {presets: 'HD'}},
        {name: 'Audio', key: '4', host: default_host, params: {presets: 'AUDIO'}},
        {name: 'Best + Audio', key: '5', host: default_host, params: {presets: 'BEST,AUDIO'}},
    ];

    const buildURL = function (preset) {
        const url = new URL(preset.host);

        url.searchParams.append('url', window.location.href);

        if (userToken !== null) {
            url.searchParams.append('token', userToken);
        }

        Object.entries(preset.params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });

        return url.href;
    };

    const launchRequest = function (preset) {
        const notificationOptions = {};

        GM_xmlhttpRequest({
            method: 'GET',
            url: buildURL(preset),
            onerror: function () {
                notificationOptions.title = `Download failed`;
                notificationOptions.text = `Host seams unreachable, is the server up ?`;
                GM_notification(notificationOptions);
            },
            onload: function (response) {
                if (response.status === 200) {
                    notificationOptions.title = `Download launched`;
                    notificationOptions.text = `Downloading`;
                    notificationOptions.timeout = notificationTimeout;
                } else if (response.status === 202) {
                    notificationOptions.title = `Download launched`;
                    notificationOptions.text = `Download not checked. Some files may not be downloaded`;
                    notificationOptions.timeout = notificationTimeout;
                } else if (response.status === 206) {
                    notificationOptions.title = `Download launched`;
                    notificationOptions.text = `Some presets failed download check`;
                    notificationOptions.timeout = notificationTimeout;
                } else if (response.status === 401) {
                    notificationOptions.title = `Authentication failed`;
                    notificationOptions.text = `The server requires an user token or the provided token is wrong`;
                } else {
                    notificationOptions.title = `Download failed`;
                    notificationOptions.text = `The format may be wrong or not available or there is no video to download`;
                }

                GM_notification(notificationOptions);
            }
        });
    };

    preset_list.forEach((preset) => {
        GM_registerMenuCommand(preset.name, () => {
            launchRequest(preset)
        }, preset.key);
    })
})();
