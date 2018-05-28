echo 'Installing Docker from the convenience script\n'
curl -sSL https://get.docker.com | sh

echo 'Enabling docker\n'
sudo systemctl enable docker
sudo systemctl start docker
sudo docker pull dhrone/pydpiper:v0.31-alpha

echo 'Testing docker\n'
sudo docker run hello-world
