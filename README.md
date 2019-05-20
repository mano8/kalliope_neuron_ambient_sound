# Ambient sound

## Synopsis

Background sounds for focusing or create a relaxing ambiance.

## Installation

Install the neuron into your resource directory
```bash
kalliope install --git-url https://github.com/mano8/kalliope_neuron_ambient_sound.git
```

## Options

| parameter         | required | type   | default          | choices             | comment                                                                     |
|-------------------|----------|--------|------------------|---------------------|-----------------------------------------------------------------------------|
| state             | YES      | string |                  | "on", "off", "play-pause", "restart-song", "next-song", "back-song"         | Target state of the ambient sound. |
| type              | NO       | string | ambient          | "ambient", "music", "sounds"   | If not set, ambient directory selected 
| sound_name        | NO       | string |                  | See the list bellow | If not set, a sound will be selectedrandomly                                |
| mplayer_path      | NO       | string | /usr/bin/mplayer |                     | Path to mplayer binary. By default /usr/bin/mplayer on Debian family system |
| auto_stop_minutes | NO       | int    |                  | Integer > 1         | Number of minutes before Kalliope stop automatically the background sound   |

List of available sound:
- birds
- fireplace
- forest
- forest-rain
- forest-stream
- heavy-rain
- mountain-steam
- ocean-waves
- seaside
- stream
- summer-rain
- thunderstorm
- tropical-beach
- tropical-thunderstorm
- urban-thunderstorm
- wind
- wood-sailboat


## Return Values

| Name             | Description                             | Type   | sample                                                   |
|------------------|-----------------------------------------|--------|----------------------------------------------------------|
| playing_sound    | The current sound played                | string | fireplace                                                |
| is_playlist      | if current sound played is playlist     | bool   | False                                                
| available_sounds | List of available sound in the database | list   | ['fireplace', 'heavy-rain', 'tropical-beach', 'seaside'] |

## Synapses example

Start an ambient sound randomly
```yml
- name: "ambient-random"
  signals:
    - order: "ambient sound"
  neurons:
    - ambient_sound:
        state: "on"
```

Start a song on music directory randomly
```yml
- name: "music-random"
  signals:
    - order: "play a song"
  neurons:
    - ambient_sound:
        state: "on"
        type: "music"
```


Start a sound on sounds directory randomly
```yml
- name: "sound-random"
  signals:
    - order: "play a song"
  neurons:
    - ambient_sound:
        state: "on"
        type: "sounds"
```

Stop played song, music or sound
```yml
- name: "ambient-stop"
  signals:
    - order: "stop ambient sound"
    - order: "stop music"
  neurons:
    - ambient_sound:
        state: "off"
```

Pause played song, music or sound
```yml
- name: "ambient-pause"
  signals:
    - order: "pause ambient sound"
    - order: "pause music"
    - order: "pause sound"
  neurons:
    - ambient_sound:
        state: "play-pause"
```

Play played song, music or sound
```yml
- name: "ambient-play"
  signals:
    - order: "play ambient sound"
    - order: "play music"
    - order: "play sound"
  neurons:
    - ambient_sound:
        state: "play-pause"
```

Restart played song, music or sound
```yml
- name: "ambient-restart"
  signals:
    - order: "restart ambient sound"
    - order: "restart song"
    - order: "restart sound"
  neurons:
    - ambient_sound:
        state: "restart-song"
```

Play selected ambient sound
```yml
- name: "ambient-selected"
  signals:
    - order: "ambient sound"
  neurons:
    - ambient_sound:
        state: "on"
        sound_name: "forest-rain"
```

Play selected song on music folder
```yml
- name: "ambient-selected"
  signals:
    - order: "ambient sound"
  neurons:
    - ambient_sound:
        state: "on"
        type: "music"
        sound_name: "name-of-your-song"
```

Play selected sound on sounds folder
```yml
- name: "ambient-selected"
  signals:
    - order: "ambient sound"
  neurons:
    - ambient_sound:
        state: "on"
        type: "sounds"
        sound_name: "name-of-your-sound"
```

Auto stop after 20 minutes
```yml
- name: "ambient-sleep"
  signals:
    - order: "ambient sound before sleeping"
  neurons:
    - ambient_sound:
        state: "on"
        auto_stop_minutes: 20
        say_template:
            - "I've selected {{ playing_sound }}"
```
## Extra
You can pause music when you need to call kalliope, 
adding play-pause state to your on-triggered-synapse.
And then play, when you finish calling your ambient-play synapse.
```yml
- name: "on-triggered-synapse"
    signals: []
    neurons:
      - ambient_sound:
          state: "play-pause"
      - say:
          message:
            - "yes?"
```            
## Notes
The folder 'player_content/' contains 3 folders:
  - ambient/ : contain all ambients sounds
  - music/   : you can add here all your music
  - sound/   : you can add here all your sounds

You can create a link to your home directory to add music more easly.
But don't erase or rename this folders.

These folders can only contains music files, no folders.

You can add winamp playlists to any folder, and play them.

For now only '.mp3', '.ogg', '.wav', '.wma', '.amr', '.m3u' extensions can be played and can be stored on SoundDatabase.
You can add your owns moddifing 'valid_ext' list on ambiant_sound.py
In case of playlist, no control for extension is executed.


## Licence

MIT
