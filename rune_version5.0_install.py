# Retrieve pydPiper
git clone https://github.com/dhrone/pydPiper
#
# Get pip installer
wget https://bootstrap.pypa.io/get-pip.py
#
# Install pip for python2
sudo python2 get-pip.py
#
# Use pip2 to install pipenv
pip2 install --user pipenv
#
# Use pipenv to install pydPiper dependencies
~/.local/bin/pipenv install moment python-mpd2 pyLMS redis pyOWM luma.oled socketIO-client Pillow
#
# Enter pipenv shell for pydPiper
~/.local/bin/pipenv shell
#
# Run pydPiper configure script
python2 configure.py
#
# Place pydpiper.service file into systemd directory
cp pydpiper.service /usr/lib/systemd/system/
#
# Enable and start the pydpiper service
systemctl daemon-reload
systemctl enable pydpiper.service
systemctl start pydpiper.service
