echo 'Installing Docker from the convenience script'
curl -sSL https://get.docker.com | sh

echo 'Now removing the engine so we can downgrade to one that currently works on Raspberry Pis' 
sudo apt-get purge -y docker-ce
sudo apt-get autoremove -y 
sudo rm -rf /var/lib/docker # This deletes all images, containers, and volumes

echo 'Reinstalling an older version'
sudo apt-get install -y --force-yes docker-ce=17.09.0ce-0raspbian

echo 'Enabling docker'
sudo usermod -aG docker volumio
sudo systemctl enable docker
sudo systemctl start docker
sudo docker pull dhrone/pydpiper:v0.31-alpha

echo 'Testing docker'
docker run armhf/hello-world
