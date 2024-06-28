# script from youtube-dlp gitlab repo : https://github.com/yt-dlp/yt-dlp/blob/master/devscripts/cli_to_api.py

import yt_dlp
import yt_dlp.options
import re

create_parser = yt_dlp.options.create_parser

def parse_patched_options(opts):
    patched_parser = create_parser()
    patched_parser.defaults.update({
        'ignoreerrors': False,
        'retries': 0,
        'fragment_retries': 0,
        'extract_flat': False,
        'concat_playlist': 'never',
    })
    yt_dlp.options.create_parser = lambda: patched_parser
    try:
        return yt_dlp.parse_options(opts)
    finally:
        yt_dlp.options.create_parser = create_parser

default_opts = parse_patched_options([]).ydl_opts

def cli_to_api(opts_string, cli_defaults=False):
    opts = re.split(r'\s+', opts_string)
    opts = (yt_dlp.parse_options if cli_defaults else parse_patched_options)(opts).ydl_opts

    diff = {k: v for k, v in opts.items() if default_opts[k] != v}
    if 'postprocessors' in diff:
        diff['postprocessors'] = [pp for pp in diff['postprocessors']
                                  if pp not in default_opts['postprocessors']]
    return diff

def merge_redis_registries(dest, source):
    for key in source:
        if key in dest:
            dest[key] = dest.get(key) + source.get(key)
        else:
            dest[key] = source[key]

    return dest