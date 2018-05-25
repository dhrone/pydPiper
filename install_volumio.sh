sudo python configure.py
sudo cp pydpiper.service /etc/systemd/system/pydpiper.service
sudo systemctl enable pydpiper
sudo systemctl start pydpiper
