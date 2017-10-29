curl -sSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker
sudo docker pull dhrone/pydpiper:v0.31-alpha
sudo cp pydpiper.service /etc/systemd/system
sudo systemctl enable pydpiper
sudo systemctl start pydpiper
