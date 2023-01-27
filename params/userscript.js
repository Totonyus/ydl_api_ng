// ==UserScript==
// @name        ydl_api_ng
// @match       http*://*/*
// @grant       GM_registerMenuCommand
// @grant       GM_xmlhttpRequest
// @grant       GM_notification
// ==/UserScript==

(function () {
    'use strict';
    const key_mapping = "0123456789abcdefghijklmnopqrstuvwxyz";

    // CUSTOMIZE HERE
    const default_host = 'http://localhost:5011';
    const notificationTimeout = 5000;
    const userToken = null;
    // STOP COSTUMIZE HERE

    const format_date = function (date) {
        const year = date.getFullYear();
        const month = `${date.getMonth() + 1}`.padStart(2, "0");
        const day = `${date.getDate()}`.padStart(2, "0");
        const hours = `${date.getHours()}`.padStart(2, "0");
        const minutes = `${date.getMinutes()}`.padStart(2, "0");

        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }

    const find_url_in_mapping = function (site_mapping) {
        const current_url = window.location.href;

        for (let site of site_mapping) {
            for (let url of site.url) {
                if (current_url.includes(url)) {
                    return site.presets;
                }
            }
        }
        return null;
    }

    const build_url = function (preset) {
        const url = new URL(preset.route.route);

        url.searchParams.append('url', window.location.href);

        if (userToken !== null) {
            url.searchParams.append('token', userToken);
        }

        if (preset.query_params !== undefined) {
            Object.entries(preset.query_params).forEach(([key, value]) => {
                url.searchParams.append(key, value);
            });
        }

        return url.href;
    };

    const launch_request = function (preset) {
        const notificationOptions = {};

        const effective_method = preset.method !== undefined ? preset.method : preset.route.method;

        let data = {};
        let headers = {};

        if (preset.body !== undefined) {
            data = JSON.stringify(preset.body());
            headers = {
                "Content-Type": "application/json",
            };
        }

        GM_xmlhttpRequest({
            method: effective_method,
            headers: headers,
            data: data,
            url: build_url(preset),
            onerror: function () {
                notificationOptions.title = `Download failed`;
                notificationOptions.text = `Host seams unreachable, is the server up ?`;
                GM_notification(notificationOptions);
            },
            onload: function (response) {
                notificationOptions.title = `Unknown error`;
                notificationOptions.text = `An unknown response code has been found`;
                notificationOptions.timeout = null;

                const status_code = preset.route.return_code[response.status]
                if (status_code !== undefined) {
                    notificationOptions.title = status_code.title;
                    notificationOptions.text = status_code.text;
                    notificationOptions.timeout = status_code.timeout;
                }

                GM_notification(notificationOptions);
            }
        });
    };

    // CUSTOMIZE HERE
    const routes = {
        download: {
            route: default_host + '/download',
            method: 'GET',
            return_code: {
                200: {
                    title: 'Download launched',
                    text: 'Downloading',
                    timeout: notificationTimeout
                },
                202: {
                    title: 'Download launched',
                    text: 'Download not checked. Some files may not be downloaded',
                    timeout: notificationTimeout
                },
                206: {
                    title: 'Download launched',
                    text: 'Some presets failed download check',
                    timeout: notificationTimeout
                },
                400: {
                    title: 'Bad request',
                    text: 'An error append during parameters validation',
                    timeout: null
                },
                401: {
                    title: 'Authentication failed',
                    text: 'The server requires an user token or the provided token is wrong',
                    timeout: null
                },
                403: {
                    title: 'Unauthorized',
                    text: 'You are not allowed to use this api',
                    timeout: null
                }
            }
        },
        programmation: {
            route: default_host + '/programmation',
            method: 'POST',
            return_code: {
                200: {
                    title: 'Programmation added',
                    text: '',
                    timeout: notificationTimeout
                },
                400: {
                    title: 'Invalid programmation',
                    text: 'Some parameters are wrong',
                    timeout: null
                },
                401: {
                    title: 'Authentication failed',
                    text: 'The server requires an user token or the provided token is wrong',
                    timeout: null
                },
                403: {
                    title: 'Unauthorized',
                    text: 'You are not allowed to use this api',
                    timeout: null
                },
                409: {
                    title: 'Non supported',
                    text: 'This feature require redis enabled on the server',
                    timeout: null
                }
            }
        }
    }

    const programmation_id = new URL(document.URL).pathname.replaceAll('/', '')
    const presets_mapping = {
        'default': {name: 'Default', route: routes.download},
        'best': {name: 'Best', route: routes.download, query_params: {presets: 'BEST'}},
        '720p': {name: '720p', route: routes.download, query_params: {presets: 'HD'}},
        'audio': {name: 'Audio', route: routes.download, query_params: {presets: 'AUDIO'}},
        'best+audio': {name: 'Best + Audio', route: routes.download, query_params: {presets: 'BEST,AUDIO'}},
        'samples': (days = 15, presets = null) => {
            let preset_name = 'Samples'
            let recurrence_end_date = null

            if (days !== null) {
                const end_date = new Date();
                end_date.setDate(end_date.getDate() + days)
                recurrence_end_date = format_date(end_date)
                preset_name = `Samples (${days} days)`
            }

            return {
                name: preset_name, route: routes.programmation, body: () => {
                    const end_date = new Date();
                    end_date.setDate(end_date.getDate() + days)

                    return {
                        id: new URL(document.URL).pathname.replaceAll('/', ''),
                        planning: {
                            recurrence_cron: `${Math.floor(Math.random() * 15)}/15 * * * *`,
                            recording_duration: 2,
                            recording_stops_at_end: true,
                            recording_restarts_during_duration: false,
                            recurrence_end_date: recurrence_end_date
                        },
                        presets: presets
                    }
                }
            }
        },
        'spy': (days = null, presets = null) => {
            let planning = {}
            let preset_name = 'Spy'

            if (days !== null) {
                const end_date = new Date();
                end_date.setDate(end_date.getDate() + days)
                planning = {
                    recurrence_end_date: format_date(end_date)
                }

                preset_name = `Spy (${days} days)`
            }

            return {
                name: preset_name, route: routes.programmation, body: () => {
                    return {
                        id: programmation_id,
                        presets: presets,
                        planning: planning
                    }
                }
            }
        },
        'prog_id': (name = 'DEFAULT', preset = null) => {
            return {
                name: name, route: routes.download, method: 'POST', body: () => {
                    return {
                        programmation: {
                            id: programmation_id
                        },
                        presets: [{
                            "_preset": preset
                        }]
                    }
                }
            }
        },
        'time_limit': (minutes = 60, preset = 'DEFAULT') => {
            return {
                name: `${minutes} minutes`, route: routes.download, method: 'POST', body: () => {
                    return {
                        programmation: {
                            id: programmation_id,
                            planning: {
                                recording_duration: minutes,
                            },
                        },
                        presets: [{
                            "_preset": preset
                        }]
                    }
                }
            }
        },
        'delete_prog': (id) => {
            return {
                name: 'Delete programmation', route: routes.programmation, method: 'DELETE', route_path: `/${id}`
            }
        },
    };

    const site_mapping = [
        {
            url: ['youtube.com', 'youtu.be'],
            presets: ['best', '720p', 'audio', 'best+audio'],
        },
        {
            url: ['twitch.tv'],
            presets: [
                presets_mapping['prog_id']('Best', 'BEST'),
                presets_mapping['prog_id']('720p', 'HD'),
                presets_mapping['time_limit'](60),
                presets_mapping['time_limit'](30),
                presets_mapping['time_limit'](15),
                'spy', 'samples'],
        },
    ];
    // STOP COSTUMIZE HERE

    let effective_presets = find_url_in_mapping(site_mapping);
    if (effective_presets == null) {
        effective_presets = Object.keys(presets_mapping);
    }

    effective_presets.forEach((preset, index) => {
        let preset_object = null;

        if (typeof preset == 'object') {
            preset_object = preset;
        } else if (typeof preset == 'string') {
            if (typeof presets_mapping[preset] == 'function') {
                preset_object = presets_mapping[preset]();
            } else {
                preset_object = presets_mapping[preset];
            }

        } else if (typeof preset == 'function') {
            preset_object = preset();
        }

        if (preset_object !== undefined && preset_object !== null) {
            let key = null;

            if (index < key_mapping.length) {
                key = key_mapping[index];
            }

            GM_registerMenuCommand(preset_object.name, () => {
                launch_request(preset_object);
            }, key);
        }
    });
})();
