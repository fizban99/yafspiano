#!/usr/bin/env python3

import pexpect

import logging
import sys
import os
import time
from enum import Enum
from pynput import keyboard

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)




class Mode(Enum):
    INSTRUMENT = 0
    BANK = 1
    SOUNDFONT = 2
    REVERB = 3


class Instrument():
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Fluidsynth():
    def __init__(self, autoconnect = 1, shell_name="", sf=""):
        logger.info(f"Starting fluidsynth  {shell_name}")

        self.fluid_proc = pexpect.spawnu(
            f"fluidsynth -C no -R no -g 1 -j " 
            f"-a jack -o midi.autoconnect={autoconnect} "
            f"-o synth.polyphony=64 "
	        f"-o audio.realtime-prio=90 "
	        f"'{sf}'")
        #self.fluid_proc.logfile = sys.stdout    
        logger.info(f"Waiting for fluidsynth shell {shell_name}")
        p = self.fluid_proc.expect('help topics.')
        self.fluid_proc.expect('>')
        logger.info("Fluidsynth started")
    
    def cmd (self, text):
        self.fluid_proc.sendline(text)        
        self.fluid_proc.expect('>')


class FeedbackSound(Fluidsynth):
    def __init__(self):
        sf = os.path.join(
             os.path.dirname(__file__) , "assets", "voices.sf3")
        super().__init__(autoconnect=0, 
            shell_name="for feedback sounds",
            sf=sf)

    def click(self, n=1):
        self.cmd(f"select 0 1 0 0")
        self.cmd(f"noteon 0 {59+n} 127")
        # time.sleep(.1)
       

    def shutdown(self):
        for n in range(5):
            self.cmd(f"select 0 1 0 0")
            self.cmd(f"noteon 0 {60-n} 40")
            time.sleep(.005)
  

class MidiPlayer(Fluidsynth):
    def __init__(self):
        sf_path = os.path.join(os.path.dirname(__file__) ,"soundfonts")
        self.sf_files = [os.path.join(sf_path, f) 
                        for f in os.listdir(sf_path) 
                        if os.path.isfile(os.path.join(sf_path, f))]
        self.sf_files.sort()
        sf_file = self.sf_files[0]
        super().__init__(sf=sf_file, shell_name="main")
        self.sf_id = 1 # this always increases
        self.sf_index = 0
        self.rev_preset = 0 # 0 will mean off
        self.cmd("reverb off")
        self.load_instruments()

    def load_instruments(self):
        self.cmd(f"inst {self.sf_id}")
        
        instruments = self.fluid_proc.before
        logger.info(instruments)
        instruments = instruments.split("\r\n")[1:-1]
        logger.info("Instruments fetched")

        bank=-1
        self.inst_list=[]
        self.bank_list=[]
        for inst in instruments:
            curr_bank = int(inst[0:3])
            if not self.bank_list or curr_bank!=self.bank_list[-1]:
                bank +=1
                self.bank_list.append(curr_bank)
                self.inst_list.append([])
            self.inst_list[bank].append(Instrument(int(inst[4:7]), inst[8:]))
        self.bank = 0
        self.inst_num = 0
        self.select_current()
        

    def cmd (self, text):
        self.fluid_proc.sendline(text)        
        self.fluid_proc.expect('>')


    def play_chord(self):

        notes = [60, 67, 76]
        for note in notes:
            self.cmd(f"noteon 0 {note} 40")
            time.sleep(.05)
        time.sleep(.5)
        for note in notes:
            self.cmd(f"noteoff 0 {note}")
    

    def wait(self):
        self.fluid_proc.wait()
    
    def select_current(self):
        self.cmd(f"select 0 {self.sf_id} " +
                 f"{self.bank_list[self.bank]} " +
                 f"{self.inst_list[self.bank][self.inst_num].id}")
        logger.info(f"{self.bank_list[self.bank]}-" +
                    f"{self.inst_list[self.bank][self.inst_num].id} " +
                    f"{self.inst_list[self.bank][self.inst_num].name}")

    def next_inst(self, inc=1):
        self.inst_num = (self.inst_num + inc) % len(self.inst_list[self.bank])
        self.select_current()
        self.play_chord()

    def next_soundfont(self, inc=1):
        self.sf_index = (self.sf_index + inc) % len(self.sf_files)
        sf_file = self.sf_files[self.sf_index]
        self.cmd(f"unload {self.sf_id}")
        self.sf_id += 1
        self.cmd(f"load {sf_file}")
        self.reset_inst()
        self.load_instruments()
        self.play_chord()

    def reset_soundfont(self, inc=1):
        self.sf_index = 0
        sf_file = self.sf_files[self.sf_index]
        self.cmd(f"unload {self.sf_id}")
        # the id seems to be always one more
        self.sf_id += 1
        self.cmd(f"load {sf_file}")
        self.load_instruments()

    def next_reverb(self, inc=1):
        self.rev_preset = (self.rev_preset + inc) % 2
        if self.rev_preset !=0:
            self.cmd("reverb on")
            self.cmd("rev_setroomsize 0.61")
            self.cmd("rev_setdamp 0.23")
            self.cmd("rev_setwidth 76.0")
            self.cmd("rev_setlevel 0.57") 
        else:
            self.cmd("reverb off")
        self.play_chord()

    def reset_reverb(self):
        self.rev_preset = 0
        self.cmd("reverb off")

    def next_bank(self, inc=1):
        self.bank += inc
        if self.bank == len(self.inst_list):
            self.bank = 0
        elif self.bank == -1:
            self.bank = len(self.inst_list)-1
        self.reset_inst()
        self.select_current()
        logger.info(f"Bank {self.bank_list[self.bank]}")
        self.play_chord()

    def exit(self):
        self.fluid_proc.sendline("quit")  

    def reset_inst(self):
        self.inst_num = 0

    def reset_bank(self):
        self.bank = 0

class Key_status():
    def __init__(self):
        self.media_volume_down=False
        self.media_volume_up=False
        self.media_volume_down_time=0
        self.media_volume_up_time=0
        self.shuttingdown = False
        self.reset = False
        self.busy =False


class Yafspiano():
    def __init__(self):
        self.fs = FeedbackSound()
        self.mp = MidiPlayer()
        self.key_status = Key_status()
        self.current_mode = Mode.INSTRUMENT


    def shutdown(self):
        self.key_status.shuttingdown=True
        self.key_status.reset = False
        logger.info("shutting down!")
        self.fs.shutdown()
        self.mp.exit()
        os.system("systemctl poweroff")


    def on_press(self, key):
        if self.key_status.shuttingdown or self.key_status.reset:
            return

        if key == keyboard.Key.media_volume_down:
            if not self.key_status.media_volume_down:
                # first time pressing the key (it is a repeating event)
                self.key_status.media_volume_down=True
                self.key_status.media_volume_down_time=time.time()
            elif (self.key_status.media_volume_up and 
                # at the same time both buttons for more than 2 seconds
                time.time()- self.key_status.media_volume_up_time > 2 and
                time.time()- self.key_status.media_volume_down_time > 2):
                self.shutdown()
            
        elif key == keyboard.Key.media_volume_up:
            if not self.key_status.media_volume_up:
                self.key_status.media_volume_up = True
                self.key_status.media_volume_up_time = time.time()
            elif (self.key_status.media_volume_down and 
                time.time()- self.key_status.media_volume_up_time > 2 and
                time.time()- self.key_status.media_volume_down_time > 2):
                self.shutdown()
            elif (time.time()- self.key_status.media_volume_up_time > 2):
                # volume up for more than 2 seconds
                self.key_status.reset = True
                if self.current_mode is Mode.BANK:
                    self.mp.reset_bank()
                    self.mp.reset_inst()
                elif self.current_mode is Mode.INSTRUMENT:
                    self.mp.reset_inst()
                elif self.current_mode is Mode.SOUNDFONT:
                    self.mp.reset_soundfont()
                    self.mp.reset_bank()
                    self.mp.reset_inst()
                elif self.current_mode is Mode.REVERB:
                    self.mp.reset_reverb()                
                self.mp.select_current()
                self.mp.play_chord()
                


        # volume mute sends press release together. No support for long clicks
        elif key == keyboard.Key.media_volume_mute:
            self.current_mode = Mode((self.current_mode.value + 1) % len(Mode))
            logger.info(self.current_mode)
            self.fs.click(self.current_mode.value + 1)
                

    def on_release(self, key):
        if self.key_status.shuttingdown or self.key_status.busy:
            return
        elif self.key_status.reset:
            self.key_status.reset = False
            self.key_status.media_volume_down = False
            self.key_status.media_volume_up = False
            return
        
        inc = 0
        if key == keyboard.Key.media_volume_down:
            self.key_status.media_volume_down = False
            self.key_status.media_volume_down_time = 0
            inc = -1

        elif key == keyboard.Key.media_volume_up:
            self.key_status.media_volume_up = False
            self.key_status.media_volume_up_time = 0
            inc = 1

        if inc:
            self.key_status.busy = True
            if self.current_mode is Mode.BANK:
                self.mp.next_bank(inc)
            elif self.current_mode is Mode.INSTRUMENT:
                self.mp.next_inst(inc)
            elif self.current_mode is Mode.SOUNDFONT:
                self.mp.next_soundfont(inc)
            elif self.current_mode is Mode.REVERB:
                self.mp.next_reverb(inc)
            self.key_status.busy = False

    def run(self):
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()
        logger.info("Start playing!")
        self.mp.play_chord()
        ret = self.mp.wait()
        listener.stop()
        sys.exit(ret)


if __name__ == "__main__":
    yafspiano = Yafspiano()
    yafspiano.run()
