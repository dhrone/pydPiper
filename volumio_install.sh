git clone https://github.com/dhrone/pydPiper
curl -sSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker volumio
sudo docker pull dhrone/pydpiper:raspdacv3
sudo cp pydPiper/pydpipervolumio.service /etc/systemd/system
sudo systemctl enable pydpipervolumio
sudo systemctl start pydpipervolumio
