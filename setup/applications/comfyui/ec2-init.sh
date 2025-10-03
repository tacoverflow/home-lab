sudo yum install -y amazon-efs-utils
sudo mkdir efs
sudo mount -t efs $EFS_ID efs/
