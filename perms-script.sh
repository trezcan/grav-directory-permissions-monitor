#!/bin/bash

# Customize these
WEB_DIR="/var/www/"
OWNER="www-data"
GROUP="www-data"
DIR_PERMS="775"
FILE_PERMS="664"

# Change ownership for both files and directories
sudo chown -R $OWNER:$GROUP $WEB_DIR

# Update directory permissions to 775
find $WEB_DIR -type d -print0 | sudo xargs -0 chmod $DIR_PERMS

# Update file permissions to 664
find $WEB_DIR -type f -print0 | sudo xargs -0 chmod $FILE_PERMS



# Add custom file permissions below. Example:

# find $WEB_DIR -type f -name 'wp-config.php' -print0 | sudo xargs -0 chmod 640
