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
You can either enable the i2c0 interface using armbian-config or editing `/boot/armbianEnv.txt`

#### Either using armbian-config
```
sudo apt install armbian-config
sudo armbian config
```
Then select 'System', 'Hardware', mark 'i2c0' and 'Save'.  
Reboot the system for the changes to take effect.

#### Or by editing /boot/armbianEnv.txt
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
Then to save press `ctrl+x`, `ctrl+y` and `enter`.  
Reboot the system for the changes to take effect.
```
sudo reboot now
```

### Install Dependences
```
sudo apt install \
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

### Running
```
python nano_hat_oled.py
```

## Troubleshooting

### Compatibility with BitBake and NanoHatOLED
This does not require the FriendlyARM BitBake or NanoHatOLED software to be installed. If this has already been installed you will need disable it `/etc/rc.local` and reboot.

```
sudo nano /etc/rc.local
```
Then find line the line:
```
/usr/local/bin/oled-start
exit 0
```
and comment out the `oled-start` line by adding `#` at the start of the line, so the line looks like this:
```
# /usr/local/bin/oled-start
exit 0
```
Then to save press `ctrl+x`, `ctrl+y` and `enter`.  
Reboot the system for the changes to take effect.
```
sudo reboot now
```
