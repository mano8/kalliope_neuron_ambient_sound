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
| state             | YES      | string |                  | "on", "off", "play", "pause", "restart-song", "next", "back", <br :>"next-on-playlist", <br :>"back-on-playlist"         | Target state of the ambient sound. |
| type              | NO       | string | ambient          | "ambient", "music", "sound"   | If not set, ambient directory selected 
| sound_name        | NO       | string |                  | See the list bellow | If not set, a sound will be selectedrandomly                                |
| mplayer_path      | NO       | string | /usr/bin/mplayer |                     | Path to mplayer binary. By default /usr/bin/mplayer on Debian family system |
| auto_stop_minutes | NO       | int    |                  | Integer > 1         | Number of minutes before Kalliope stop automatically the background sound   |

List of available ambient sound: (player_content/ambient/)
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
| playing_type      | Folder type selected     | string   | ambient         |
| is_playlist      | if current sound played is playlist     | bool   | False          |                                      
| available_sounds | List of available sound in the database | list   | ['fireplace', 'heavy-rain', 'tropical-beach', 'seaside'] |


## Kalliope memory

This neuron save on kalliope memory 'state', 'type', and 'sound_name' options with keys :
  - 'kalliope_ambient_sound_state'  -> can be 'on' or 'off' (other states not be registered)
  - 'kalliope_ambient_sound_type'   -> can be 'ambient', 'music' or 'sound'
  - 'kalliope_ambient_sound_name'  -> the current sound played name

Who add capatibility to retrive returned values when state is already 'on', 
and sending new valid state (pause, play... ), with other synapse.

You can use them, but do not overwrite any of those data (can stop actual sound played, or disable capatibility to retrive returned values).


## Synapses example


### Basic fetures

Start an ambient sound randomly (No need to set type here, default is ambient)
```yml
- name: "ambient-random"
  signals:
    - order: "ambient sound"
  neurons:
    - ambient_sound:
        state: "on"
```

Start a song on music directory randomly (change type to select other folder)
```yml
- name: "music-random"
  signals:
    - order: "play a song"
  neurons:
    - ambient_sound:
        state: "on"
        type: "music"
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
        state: "pause"
```

Play paused song, music or sound
```yml
- name: "ambient-play"
  signals:
    - order: "play ambient sound"
    - order: "play music"
    - order: "play sound"
  neurons:
    - ambient_sound:
        state: "play"
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

### Using next and back states

For use this states you need to use kalliope_memory to send actual sound played at next or back synapse.
(Using thoses states, not using kalliope_memory, result with no changes)

Example you select to play music randomly setting returned values to kalliope_memory:
```yml
- name: "music-random"
  signals:
    - order: "play a song"
  neurons:
    - ambient_sound:
        state: "on"
        type: "music"
        kalliope_memory:
          kalliope_ambient_sound_name: "{{ playing_sound }}"
          kalliope_ambient_sound_type: "{{ playing_type }}"
```

Then you can use 'next' or 'back' states. (registering new returned values on kalliope_memory)

```yml
- name: "ambient-next-song"
  signals:
    - order: "play next song on list"
  neurons:
    - ambient_sound:
        state: "next"
        type: "{{ kalliope_memory['kalliope_ambient_sound_type'] }}"
        sound_name: "{{ kalliope_memory['kalliope_ambient_sound_name'] }}"
        kalliope_memory:
          kalliope_ambient_sound_name: "{{ playing_sound }}"
          kalliope_ambient_sound_type: "{{ playing_type }}"
```

```yml
- name: "ambient-back-song"
  signals:
    - order: "play back song on list"
  neurons:
    - ambient_sound:
        state: "back"
        type: "{{ kalliope_memory['kalliope_ambient_sound_type'] }}"
        sound_name: "{{ kalliope_memory['kalliope_ambient_sound_name'] }}"
        kalliope_memory:
          kalliope_ambient_sound_name: "{{ playing_sound }}"
          kalliope_ambient_sound_type: "{{ playing_type }}"
```
And Using your stop state synapse to initialyse kalliope_memory


```yml
- name: "ambient-stop"
  signals:
    - order: "stop ambient sound"
    - order: "stop music"
  neurons:
    - ambient_sound:
        state: "off"
        kalliope_memory:
          kalliope_ambient_sound_name: ""
          kalliope_ambient_sound_type: ""
```

### Using next-on-playlist and back-on-playlist states

For use this states you need to play a m3u playlist first. (if not a playlist only restart the song)

And then add thoses synapses to your brain file:

```yml
- name: "ambient-next-song-on-playlist"
  signals:
    - order: "play next song on playlist"
  neurons:
    - ambient_sound:
        state: "next-on-playlist"
```

```yml
- name: "ambient-back-song-on-playlist"
  signals:
    - order: "play back song on playlist"
  neurons:
    - ambient_sound:
        state: "back-on-playlist"
```        
## Extra
You can pause music when you need to call kalliope, 
adding pause state to your on-triggered-synapse.

And then play, when you finish calling your ambient-play synapse.
```yml
- name: "on-triggered-synapse"
    signals: []
    neurons:
      - ambient_sound:
          state: "pause"
      - say:
          message:
            - "yes?"
```

## Folder structure
The folder 'player_content/' contains 3 folders:
  - ambient/ : contain all ambients sounds
  - music/   : you can add here all your music
  - sound/   : you can add here all your sounds

You can create a link to your home directory to add music more easly.
But don't erase or rename this folders.

These folders can only contains files, no directories.

You can add winamp playlists to any folder, and play them.

For now only '.mp3', '.ogg', '.wav', '.wma', '.amr', '.m3u' extensions can be played and can be stored on SoundDatabase.
In case of playlist, no control for extension, is executed.

## Fifo
Fifo file is used here, to control mplayer.

By default it created in this neuron path depending where you have installed. -> neuron_path/fifo_file_path

If you have anothers fifo files, to control mplayer, you can change default directory, 
by changing, fifo_file_path variable with your absolute path.

Only if you want, all fifo's on same directory.

This Fifo's don't be used by another mplayer process.


## Licence

MIT