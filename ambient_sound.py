import logging
import random
import subprocess
import os
import sys
import psutil
import glob
import threading
from time import sleep
from kalliope.core.Utils import Utils
from kalliope.core.NeuronModule import NeuronModule, InvalidParameterException


logging.basicConfig()
logger = logging.getLogger("kalliope")

pid_file_path = "pid.txt"
fifo_file_path = "music-control"
sound_path = "sounds/"
valid_ext = ['.mp3', '.ogg', '.wav', '.wma', '.amr', '.m3u']

class AmbientSound:
    def __init__(self, name=None, file_extension=None):
        self.name = name
        self.file_extension = file_extension

    def __str__(self):
        return "name: %s, file_extension: %s" % (self.name, self.file_extension)


class SoundDatabase:

    def __init__(self, soundtype = "ambient"):
        self.available_sounds = self.load_available_sounds(soundtype)

    @staticmethod
    def load_available_sounds(soundtype = "ambient"):
        """
        Check all file in the sub folder "sounds" and return a list of AmbientSound object
        :return: list of AmbientSound object
        """
        list_ambient_sounds = list()

        list_sound_name_with_extension = \
            [os.path.basename(x) for x in glob.glob(SoundDatabase.get_sound_folder_path(soundtype) + '/*')]
        logger.debug("[Ambient_sounds] file in sound folder: %s" % list_sound_name_with_extension)

        for sound_with_extension in list_sound_name_with_extension:
            tuple_name_extension = os.path.splitext(sound_with_extension)
            # print tuple_name_extension
            if tuple_name_extension[1] in valid_ext:
                new_ambient_sound = AmbientSound(name=tuple_name_extension[0], file_extension=tuple_name_extension[1])
                list_ambient_sounds.append(new_ambient_sound)

        return list_ambient_sounds

    def get_sound_by_name(self, sound_name_to_find):
        """
        Return an AmbientSound object from a given name if exist in list_ambient_sounds of the sound database
        :param sound_name_to_find: name of the sound to find
        :return:
        """

        for ambient_sound in self.available_sounds:
            if ambient_sound.name == sound_name_to_find:
                return ambient_sound
        return None

    def get_random_ambient_sound(self):
        """
        return an AmbientSound object randomly from available sounds
        :return: AmbientSound object
        """
        return random.choice(self.available_sounds)

    @classmethod
    def get_neuron_path(cls):
        """
        Return the absolute path of the current neuron folder
        :return: absolute path of the current neuron folder
        """
        current_script_path = os.path.abspath(__file__)
        return os.path.normpath(current_script_path + os.sep + os.pardir)

    @classmethod
    def get_sound_folder_path(cls, soundtype = "ambient"):
        """
        Return the absolute path of the current sound folder in the neuron folder
        :return: absolute path of the current sound folder in the neuron folder
        """
        dr = "ambient/"
        if soundtype == "music":
            dr = "music/"
        elif soundtype == "sounds":
            dr = "sounds/"

        absolute_sound_file_path = cls.get_neuron_path() + os.sep + sound_path + dr
        if os.path.exists(absolute_sound_file_path):
            logger.debug("[Ambient_sounds] absolute_sound_folder_path: %s" % absolute_sound_file_path)
            return absolute_sound_file_path
        else:
            raise InvalidParameterException("[Ambient_sounds] Can't open Sound folder %s. Please create it."% absolute_sound_file_path)



class Ambient_sound(NeuronModule):
    """
    Ambient sound neuron
    Play a sound from the list of sound available in the sound folder
    """
    def __init__(self, **kwargs):
        super(Ambient_sound, self).__init__(**kwargs)

        self.state = kwargs.get('state', None)
        self.type = kwargs.get('type', None)
        self.sound_name = kwargs.get('sound_name', None)
        self.mplayer_path = kwargs.get('mplayer_path', "/usr/bin/mplayer")
        self.auto_stop_minutes = kwargs.get('auto_stop_minutes', None)
        
        self.is_playlist = False
        self.extra_cmd = ["play-pause", "restart-song", "next-song", "back-song"]
        # this is the target AmbientSound object if the user gave a sound_name to play.
        # this object will be loaded by the _is_parameters_ok function durring the check if the sound exist
        self.target_ambient_sound = None

        # sound database
        self.sdb = SoundDatabase(self.type)

        # message dict that will be passed to the neuron template
        self.message = dict()
        # add the list of available sounds
        self.message["available_sounds"] = list()
        for sound in self.sdb.available_sounds:
            self.message["available_sounds"].append(sound.name)

        # check if sent parameters are in good state
        if self._is_parameters_ok():
            if self.state == "off":
                self.stop_last_process()
                self.clean_pid_file()
            elif self.state in self.extra_cmd:
                # To Do : 
                #   - block next_song, back_song if no playlist or if no random
                #     or if simple song select other creating other process
                #   - add auto stop in paused mode for close unused process if user only pause and never stop
                self.cmd_to_last_process(self.state)
            else:
                # we stop the last process if exist
                self.stop_last_process()

                # if the user haven't given a sound name
                if self.target_ambient_sound is None:
                    # then we load one randomly
                    self.target_ambient_sound = self.sdb.get_random_ambient_sound()
                    logger.debug("[Ambient_sounds] Random ambient sound selected: %s" % self.target_ambient_sound)

                # then we can start a new process
                if self.target_ambient_sound is not None:
                    self.start_new_process(self.target_ambient_sound)

                    # give the current file name played to the neuron template
                    self.message["playing_sound"] = self.target_ambient_sound.name
                    self.message["is_playlist"] = self.is_playlist
                    # run auto stop thread
                    if self.auto_stop_minutes:
                        thread_auto_stop = threading.Thread(target=self.wait_before_stop)
                        thread_auto_stop.start()

            # give the message dict to the neuron template
            self.say(self.message)

    def wait_before_stop(self):
        logger.debug("[Ambient_sounds] Wait %s minutes before checking if the thread is alive" % self.auto_stop_minutes)
        Utils.print_info("[Ambient_sounds] Wait %s minutes before stopping the ambient sound" % self.auto_stop_minutes)
        sleep(self.auto_stop_minutes*60)  # *60 to convert received minutes into seconds
        logger.debug("[Ambient_sounds] Time is over, Stop player")
        Utils.print_info("[Ambient_sounds] Time is over, stopping the ambient sound")
        self.stop_last_process()
    

    def _is_parameters_ok(self):
        """
        Check that all given parameter are valid
        :return: True if all given parameter are ok
        """

        if self.state not in ["on", "off"] and self.state not in self.extra_cmd: 
            raise InvalidParameterException("[Ambient_sounds] State must be 'on', 'off', 'play-pause', 'restart-song', 'next-song', 'back-song'")

        # check that the given sound name exist
        if self.sound_name is not None:
            self.target_ambient_sound = self.sdb.get_sound_by_name(self.sound_name)
            if self.target_ambient_sound is None:
                raise InvalidParameterException("[Ambient_sounds] Sound name %s does not exist" % self.sound_name)

        
        # if wait auto_stop_minutes is set, mut be an integer or string convertible to integer
        if self.auto_stop_minutes is not None:
            if not isinstance(self.auto_stop_minutes, int):
                try:
                    self.auto_stop_minutes = int(self.auto_stop_minutes)
                except ValueError:
                    raise InvalidParameterException("[Ambient_sounds] auto_stop_minutes must be an integer")
            # check auto_stop_minutes is positive
            if self.auto_stop_minutes < 1:
                raise InvalidParameterException("[Ambient_sounds] auto_stop_minutes must be set at least to 1 minute")
        return True

    @staticmethod
    def get_fifo_file_path():
        """
        Store FIFO into a file
        :param pid: pid number to save
        :return: Music control fifo path or None
        """
        absolute_fifo_file_path = SoundDatabase.get_neuron_path() + os.sep + fifo_file_path
        try:
            if not os.path.exists(absolute_fifo_file_path):
                os.mkfifo(absolute_fifo_file_path)
                logger.debug("[Ambient_sounds] music control fifo created. file path: %s" % absolute_fifo_file_path)    
            return absolute_fifo_file_path
        except IOError as e:
            logger.error("[Ambient_sounds] Get music control fifo I/O error(%s): %s", e.errno, e.strerror)
        
        return None

    @classmethod
    def send_to_fifo_music_control(cls, cmd):
        """
        Send a command to mplayer fifo
        :param pid: pid number to save
        :return: Music control fifo path or None
        """
        absolute_fifo_file_path = cls.get_fifo_file_path()
        try:
            if cmd == "play-pause":
                os.system("echo pause > %s"%absolute_fifo_file_path) 
            elif cmd == "next-song":
                os.system("echo pt_step 1 > %s"%absolute_fifo_file_path) 
            elif cmd == "back-song":
                os.system("echo pt_step -1 > %s"%absolute_fifo_file_path) 
            elif cmd == "restart-song":
                os.system("echo set_property percent_pos 0 > %s"%absolute_fifo_file_path) 
        except Exception as e:
            logger.error("[Ambient_sounds] Unable to send command to mplayer. Exception error(%s): %s", e.errno, e.strerror)
        
        return None

    @staticmethod
    def store_pid(pid):
        """
        Store a PID number into a file
        :param pid: pid number to save
        :return:
        """

        content = str(pid)
        absolute_pid_file_path = SoundDatabase.get_neuron_path() + os.sep + pid_file_path
        try:
            with open(absolute_pid_file_path, "wb") as file_open:
                if sys.version_info[0] == 2:
                    file_open.write(content)
                else:
                    file_open.write(content.encode())
                file_open.close()

        except IOError as e:
            logger.error("[Ambient_sounds] I/O error(%s): %s", e.errno, e.strerror)
            return False

    @staticmethod
    def load_pid():
        """
        Load a PID number from the pid.txt file
        :return:
        """
        absolute_pid_file_path = SoundDatabase.get_neuron_path() + os.sep + pid_file_path

        if os.path.isfile(absolute_pid_file_path):
            try:
                with open(absolute_pid_file_path, "r") as file_open:
                    pid_str = file_open.readline()
                    if pid_str:
                        return int(pid_str)

            except IOError as e:
                logger.debug("[Ambient_sounds] I/O error(%s): %s", e.errno, e.strerror)
                return False
        return False

    def cmd_to_last_process(self, cmd):
        """
        send cmd to the last mplayer process launched by this neuron
        :return:
        """
        pid = self.load_pid()

        if pid is not None:
            logger.debug("[Ambient_sounds] loaded pid: %s" % pid)
            try:
                p = psutil.Process(pid)
                self.send_to_fifo_music_control(cmd)
                logger.debug("[Ambient_sounds] cmd %s send to mplayer process with pid %s" % (cmd, pid))
            except psutil.NoSuchProcess:
                logger.debug("[Ambient_sounds] the process PID %s does not exist" % pid)
            except Exception as e:
                logger.debug("[Ambient_sounds] p type : %s" % str(type(p)))
                logger.error("[Ambient_sounds] Unable to send mplayer cmd. Exception : %s", str(e))
        else:
            logger.debug("[Ambient_sounds] pid is null. Process already stopped")

    def stop_last_process(self):
        """
        stop the last mplayer process launched by this neuron
        :return:
        """
        pid = self.load_pid()

        if pid is not None:
            logger.debug("[Ambient_sounds] loaded pid: %s" % pid)
            try:
                p = psutil.Process(pid)
                p.kill()
                logger.debug("[Ambient_sounds] mplayer process with pid %s killed" % pid)
            except psutil.NoSuchProcess:
                logger.debug("[Ambient_sounds] the process PID %s does not exist" % pid)
        else:
            logger.debug("[Ambient_sounds] pid is null. Process already stopped")

    def start_new_process(self, target_ambient_sound):
        """
        Start mplayer process with the given AmbientSound
        :param target_ambient_sound:
        :type target_ambient_sound: AmbientSound
        :return:
        """
        absolute_fifo_file_path = self.get_fifo_file_path()
        if target_ambient_sound.file_extension in valid_ext:
            mplayer_exec_path = [self.mplayer_path]
            mplayer_options = ['-slave', '-quiet', '-loop', '0']
            if absolute_fifo_file_path is not None:
                mplayer_options.append('-input')
                mplayer_options.append('file=%s'%absolute_fifo_file_path)
            # if is m3u playlist
            if target_ambient_sound.file_extension == '.m3u':
                self.is_playlist = True
                mplayer_options.append('-playlist')
                logger.debug("[Ambient_sounds] playlist detected...")
        
            mplayer_command = list()
            mplayer_command.extend(mplayer_exec_path)
            mplayer_command.extend(mplayer_options)

            mplayer_command.append(SoundDatabase.get_sound_folder_path(self.type) + os.sep +
                                target_ambient_sound.name + target_ambient_sound.file_extension)
            logger.debug("[Ambient_sounds] Mplayer cmd: %s" % str(mplayer_command))
            logger.debug("[Ambient_sounds] file extension : %s" % str(target_ambient_sound.file_extension))
            
            # run mplayer in background inside a new process
            # redirect stdout and stderr to nothing
            # https://stackoverflow.com/questions/6735917/redirecting-stdout-to-nothing-in-python
            fnull = open(os.devnull, 'w') 
            pid = subprocess.Popen(mplayer_command, stdout=fnull, stderr=fnull).pid

            # store the pid in a file to be killed later
            self.store_pid(pid)

            logger.debug("[Ambient_sounds] Mplayer started, pid: %s" % pid)
        else:
            logger.error("[Ambient_sounds] Extension error : when attemping to play %s. Extension accepted are %s", str(target_ambient_sound.name + target_ambient_sound.file_extension), str(valid_ext))

    @staticmethod
    def clean_pid_file():
        """
        Clean up all data stored in the pid.txt file
        """
        try:
            with open(pid_file_path, "w") as file_open:
                file_open.close()
                logger.debug("[Ambient_sounds] pid file cleaned")

        except IOError as e:
            logger.error("I/O error(%s): %s", e.errno, e.strerror)
            return False
