# NanoHAT OLED for Armbian
NanoHAT OLED and GPIO Button Control for Armbian.

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

### Enable i2c0
You can either enable the i2c0 interface using armbian-config or editing `/boot/armbianEnv.txt`.

#### Method 1: Use armbian-config
```
sudo apt install armbian-config
sudo armbian config
```
Then select `System`, `Hardware`, mark `i2c0` and `Save`.  
Reboot the system for the changes to take effect.

#### Method 2: Edit /boot/armbianEnv.txt
```
sudo nano /boot/armbianEnv.txt
```
Then add `i2c0` to the overlays line, for example if the line appears as follows:
```
overlays=usbhost1 usbhost2
```
Then add `i2c0` with a space seperating it from the other values:
```
overlays=i2c0 usbhost1 usbhost2
```
Then to save these changes, press `ctrl+x`, `ctrl+y` and `enter` as prompted at the bottom of the screen.   
Reboot the system for the changes to take effect.
```
sudo reboot now
```

### Getting Started

#### Install Dependences
```
sudo apt update \
sudo apt -y install \
  libjpeg-dev \
  libfreetype6-dev \
  python \
  python-dev \
  python-pip \
  python-setuptools \
  python-smbus \
  ttf-dejavu \
  zlib1g-dev

sudo pip install \
  image \
  pillow
```

#### Clone from GitHub
```
sudo apt -y install git
git clone https://github.com/crouchingtigerhiddenadam/nano-hat-oled-armbian
cd nano-hat-oled-armbian
```

#### Running
```
python nano_hat_oled.py
```

### Installing (Optional)
Move the files to a production directory:
```
sudo mkdir /usr/share/nanohatoled
sudo mv nano_hat_oled.py /usr/share/nanohatoled
sudo mv splash.png /usr/share/nanohatoled
```
Then edit:
```
sudo nano /etc/rc.local
```
Then find the line:
```
exit 0
```
And add `cd /usr/share/nanohatoled` and `/usr/bin/python nano_hat_oled.py &` before `exit 0` so the lines look like this:
```
cd /usr/share/nanohatoled
/usr/bin/python nano_hat_oled.py &
exit 0
```
Then to save these changes, press `ctrl+x`, `ctrl+y` and `enter` as prompted at the bottom of the screen.   
Reboot the system for the changes to take effect.

## Troubleshooting

### Compatibility with BitBake and NanoHatOLED
This does not require the FriendlyARM BitBake or NanoHatOLED software to be installed. If this has already been installed you will need disable it.

```
sudo nano /etc/rc.local
```
Then find the lines:
```
/usr/local/bin/oled-start
exit 0
```
and comment out the `oled-start` line by adding `#` at the start of the line, so the lines look like this:
```
# /usr/local/bin/oled-start
exit 0
```
Then to save these changes, press `ctrl+x`, `ctrl+y` and `enter` as prompted at the bottom of the screen.   
Reboot the system for the changes to take effect.
```
sudo reboot now
```
