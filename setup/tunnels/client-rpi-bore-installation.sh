# get latest version url of bore from the main repo  (https://github.com/ekzhang/bore)
BORE_URL=$(curl -s https://api.github.com/repos/ekzhang/bore/releases/latest | jq '.assets[] | select(.name | contains("linux"|"arm-"|"musleabi.")).browser_download_url')
# install latest version 
wget $BORE_URL
# move the bin to /usr/local/bin
mv ./bore /usr/local/bin/bore
