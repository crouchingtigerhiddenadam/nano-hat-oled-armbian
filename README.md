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

## Getting Started

#### Install Dependences
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

#### Running
```
python nano_hat_oled.py
```
