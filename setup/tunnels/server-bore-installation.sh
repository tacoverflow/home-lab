# install dependencies 
sudo DEBIAN_FRONTEND=noninteractive apt install jq -y
# get latest version url of bore from the main repo  (https://github.com/ekzhang/bore)
BORE_URL=$(curl -s https://api.github.com/repos/ekzhang/bore/releases/latest | jq -r '.assets[] | select(.name | contains("linux") and contains("i686") and contains("musl.")).browser_download_url')
# install latest version 
wget $BORE_URL
# untar archive
tar -xvf $(basename $BORE_URL)
# move the bin to /usr/local/bin
mv ./bore /usr/local/bin/bore
# delete old tar archive
rm $(basename $BORE_URL)
