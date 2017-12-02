sudo apt-get update && apt-get install -y --force-yes docker-ce=17.10.0-ce-0raspbian
sudo usermod -aG docker volumio
sudo systemctl enable docker
sudo systemctl start docker
sudo docker pull dhrone/pydpiper:v0.31-alpha
docker run armhf/hello-world

