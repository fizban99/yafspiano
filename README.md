Yafspiano
=========

_Yet Another FluidSynth Piano. Python3 script to use a TV Box as a headless software midi synthesizer for a USB Midi keyboard_

There are many people that have created scripts to use a Raspberry Pi as a software synth to use it as a standalone device into which connect a midi keyboard. Among others, the [SquishBox](https://geekfunklabs.com/products/squishbox/), [Zynthian](https://zynthian.org/), the [Sampler box](https://www.samplerbox.org/), the [Zbox](https://zircothc.wordpress.com/2017/12/11/zbox-orange-pi-zero-and-fluidsynth-headless/) or [Pipiano](https://github.com/bneijt/pipiano) / [original Pipiano](http://jacquespi.blogspot.com/2013/07/synthesizer.html). Most of them are based on [FluidSynth](https://www.fluidsynth.org/). This is just one more, but with the twist of using the hardware buttons of the USB soundcard for additional control, which is easier than using the edit button of the midi keyboard (if it has one). Besides, it has been actually tested only on a TV Box runing Armbian. This is much less ambitius than the [Sonaremin project](https://github.com/hexdump0815/sonaremin), which is also targeted towards TV Boxes.


Althugh this script has been tested on a QPlus TV Box, it might work with other devices with Armbian (similar ones are the T95 and T95Max, if H6-based).
The QPlus TV Box is based on the Allwinner H6 chipset, which is the same chipset of several Orange Pi models, but at a competitive price since it comes with 2GB-4GB (although only 3GB available) RAM, 32GB/64GB emmc memory, a case, and a power plug. Check Amazon or AliExpress for current prices. Unfortunately, this low price comes with some limitations: the unofficial Armbian version that can be installed on these devices often do not support their WiFi, their GPU, their remote or their internal audio DAC, which might be OK for certain projects such as this one. Once configured, the box takes less than 40 seconds to be ready to play from the moment you plug it in.

The python script might actually work on any linux box, but it has not been tested.

Besides the TV Box, you also need a USB soundcard (preferably with 4 buttons: mute mic, mute volume, volume up and volume down). The buttons allow changing the instrument and the bank. You can use a USB Soundcard without buttons, but you will just be able to play one instrument. Obviously, you should also have a USB Midi keyboard or to connect to the box. The idea of the project is to be headless (without monitor), so you just switch on the box, wait a few seconds to boot, and start playing without the need of a keyboard, mouse or monitor. 

Ir you need more advanced functionality you can try the [HeadlessPi](https://github.com/albedozero/fluidpatcher) from the author of the [SquishBox](https://geekfunklabs.com/products/squishbox/)


There are many places to download soundfonts. For piano soundfonts, try [Soundfonts4U](https://sites.google.com/site/soundfonts4u/) 

The included sounfont contains a piano from [studioax.com](https://www.studioax.com) and other instruments from the NiceKeys soundfont of [Soundfonts4U](https://sites.google.com/site/soundfonts4u/)


A note on USB Soundcards
------------------------

There are many USB Soundcards out there. Cheap ones tend to sound bad. Some inexpensive and compatible chipsets include CM108, HS100B and PCM2704. The quality of the sound will also depend on the additional circuitry surrounding the main chipset, but PCM2704-based cards seem to tend to sound good, although it is difficult to find them with a case. I have used successfully a [LogiLink UA0078](https://images-na.ssl-images-amazon.com/images/I/51HhgVREaQS.__AC_SX300_SY300_QL70_ML2_.jpg) card (CM108 based) and a [generic HS100B card which included some (bad) headphones](https://images-na.ssl-images-amazon.com/images/I/61E5Mqz5caL.__AC_SX300_SY300_QL70_ML2_.jpg), The LogiLink needs a USB extension cable, since it does not fit directly in the USB connector of the QPlus. 


Installation
------------

Installation is not difficult if you follow the steps carefully. You should connect a computer keyboard, mouse, monitor and ethernet cable with internet access to the box in order to configure it. You should also have an empty SD Card (minimum 8GB and Class 1 -'A1' recommended).

### Preparation of the SD Card

This is done on a separate computer. These instructions are for a compatible TV Box (basically a QPlus, a T95 or a T95Max) (see https://forum.armbian.com/topic/16859-allwinner-h6/)

Download the latest armbian buster desktop release for the H6 chipset from https://users.armbian.com/balbes150/aw-h6-tv/ . At the time of writing it is 	
`Armbian_21.08.0-trunk_Aw-h6-tv_buster_current_5.10.47_xfce_desktop.img.xz`

The [official Armbian documentation](https://docs.armbian.com/User-Guide_Getting-Started/) recommends formatting first the card using the [SD Memory Card Formatter](https://www.sdcard.org/downloads/formatter/) and then using [USB Imager](https://gitlab.com/bztsrc/usbimager) to load the image into the SD Card, directly selecting the compressed .xz image. It has worked for me without problems. Be careful to select the drive with the SD Card in the dropdown list. Although the Windows drive cannot be selected, if you have additional disks they will appear in there.

One of the good things of these H6-based TV Boxes is that they can boot from the SD Card directly. Once the image is burned in the SD Card, just insert the card in the TV Box, plug it and Armbian will start loading. The original Android system will stay in the internal storage and will boot normally if the SD Card is not inserted. There is an option to actually replace Android with Armbian, but it is not required, unless you want to forget about Android and just use Armbian. Armbian [comes with a tool](https://docs.armbian.com/User-Guide_Getting-Started/#how-to-install-to-emmc-nand-sata-usb) just to do that.


### Armbian initial configuration

Upon first boot, Armbian will typically ask several questions:

1. Set the root password. Use letters and numbers. You will have to re-enter it for confirmation. If for some strange reason you get the login prompt and not the request to set the root password, just login with user `root` and password `1234`. It will then prompt you to set the root password as well as the following questions.
2. Default command shell. I use bash (press '1')
3. Default user name and password with confirmation
4. Your 'real name'. Just leave the default, which is the user capitalized.
5. If you want to set your user language based on your location. Since I prefer using English for the interface (it is easier to google problems and instructions if the messages are in English), I press 'n'

If all goes well, it should show an x-windows interface. On the top left corner go to Applications-Settings-Armbian config. You will be asked for your password. Enter it. Once in the tool, select Personal. If needed, configure your keyboard layout for your language and then your timezone.

Click on your user name on the top right corner and select Restart.



### Autologin configuration

You will restart to the command line. Enter your user and password. You can go back to the desktop environment using 

```bash
startx
``` 
There you can use the webbrowser to access these instructions and then open a Terminal Emulator and copy and paste in the terminal window (pasting is done with CTRL+SHIFT+V).

To make the system login automatically to the x-windows environment, we need to perform some additional steps. Type the following commands, entering your password when asked and confirming the actions if need to. Note that when entering paths, you can start writing, use TAB to partially autocomplete, keep writing and use TAB again to autocomplete.

Download this repository:

```bash
git clone https://github.com/fizban99/yafspiano.git
``` 
Add your user in the configuration file:

```bash
cd yafspiano
nano install_assets/22-armbian-autologin.conf
```

The second line will present you with an editor. Go to the line with `autologin-user=` and enter your user name in there, replacing the placeholder. Press CTRL+X, confirm with 'y' and ENTER to save.
If you press CTRL+Z by mistake, you can just type `fg` to return back to the editor.

Copy the configuration to the apropriate system path:

```bash
sudo cp install_assets/22-armbian-autologin.conf /etc/lightdm/lightdm.conf.d/
```

Reboot the system to verify that the autologin works with:

```bash
sudo reboot
```

### Installation of pre-requisites


#### Compilation of FluidSynth

The default FluidSynth package is version 1.1.1, but the latest one is 2.2.2. It comes with some useful functionality such as autodetection of a midi-keyboard. So, we will compile the latest version. Open a Terminal emulator and type or copy/paste the following (better line by line):

```bash
wget https://github.com/FluidSynth/fluidsynth/archive/refs/tags/v2.2.2.tar.gz
tar -xvzf v2.2.2.tar.gz
cd fluidsynth-2.2.2
mkdir build
cd build
sudo sed -i~orig -e 's/# deb-src/deb-src/' /etc/apt/sources.list
sudo apt update
sudo apt-get build-dep fluidsynth --no-install-recommends
cmake ..
sudo make install
sudo nano /etc/ld.so.conf.d/libc.conf
```
In the nano editor, add one line with ```/usr/local/lib64```. Press CTRL+X, confirm with 'y' and ENTER to save.

Finally type the following in the terminal for the change to take effect:

```
sudo ldconfig
```

Check that fluidsynth launches: 

```
fluidsynth
```
You should get a `>` prompt. Press CTRL+C to exit fluidsynth.

We will also install a component to reduce the latency of the sound. With jack, the latency can be much lower than any latency you can have in Android. The drawback is that only one application can take a hold of the audio device, which for us is fine (just remember not to have Firefox on when running the headless_synth):
```
sudo apt install jackd2
```
It wil ask you if you want to enable realtime. Select Yes.

Copy the default jack configuration to your home:

```
cp ~/yafspiano/install_assets/.jackdrc ~/
```

Reboot for the changes to take effect with:

```
sudo reboot
```


#### python3 prerequisites

Since the headless_synth script is in python3, we need to install some requirements:

```
sudo apt install python3-pip
pip3 install pexpect setuptools
sudo apt install python3-dev
pip3 install wheel
pip3 install pynput
```

#### The headless_synth script

Close Firefox and test the script (you need at least a usb sound card connected, so either you use a USB hub or disconnect the mouse and connect the usb soundcard before running it):

```
python3 yafspiano/yafspiano.py
```

After a few seconds you should hear a chord, indicating that the synth is ready. If you are not using a USB hub, you can now disconnect your computer keyboard and connect a midi keyboard. Fluidsynth should autodetect it and you should be able to play. You can press CTRL+C to abort (reconnect your computer keyboard if needed).

#### Autostart the headless_synth upon boot

Since this is going to be headless, we want the script to autostart upon boot.

```
cp ~/yafspiano/install_assets/yafspiano.desktop ~/.config/autostart/yafspiano.desktop
```

That's it. Make sure you close Firefox and reboot to see if it works:

```
sudo reboot
```

To powerdown the system, press volume up and down at the same time for a few seconds. You should hear a sound and then the screen should show the armbian logo and the wheel spinning for a few seconds until it stops. If the soundcard has a led, it should also turn off. You can unplug the tvbox now.

#### Additional soundfonts

You can download the GM Soundfont that typically is used with fluidsynth and create a symlink in the soundfonts directory:

```
sudo apt install -y fluid-soundfont-gm
ln -s /usr/share/sounds/sf2/FluidR3_GM.sf2 ~/yafspiano/soundfonts/

Usage
------------

Out of the 4 buttons only 3 are clickable: volume up, volume down and volume mute. The mic mute does not generate any signal.

The volume mute changes the functionality of the volume up and down. By default, volume up and down navigate the instruments from the current bank. By pressing once  on the volume mute, the volume keys navigate through the banks. One more press and you can navigate through the instruments of the current bank.

Additionaly, you can use the default functionality of FluidSynth if you have an Edit button in your Keyboard (e.g. KeyStation49 or KeyRig49):
![Piano settings](http://1.bp.blogspot.com/-HV-r5akM2UA/UfTxJK8mmbI/AAAAAAAABcM/x5FBg9kIBUA/s1600/Untitled-1.png)

To do
------------

* Long click on volume up to reset current mode.