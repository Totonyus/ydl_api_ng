# Params metadata

As the `params.ini` is a plain text file, we need to cast to the correct type to address `yt-dlp` python API.

For this purpose, there is the [params_metadata.ini](../params/params_metadata.ini) file that tells what type is each
field.

Every field not in this file is a `str`.

## Override

There are two cases you could want to override the file :

- You may want to add your own fields
- One of the fields has the wrong type (please open an issue)

To override this file, simply copy the [params_metadata.ini](../params/params_metadata.ini) alongside your `params.ini`
file

Note this file does not apply to `POST` requests (there is simply no need) : the type of the attribute will be decided by the `JSON`.

## Hidden attributes

There is a special section : all the fields in this one will be removed from all api responses (only for presets !!!)
but will be useable in [hooks](300_Hooks.md).

```
_hidden = _token
          _unit_test
          logger
          password
          postprocessor_hooks
          progress_hooks
          username
```