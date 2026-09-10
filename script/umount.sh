#!/bin/bash

MOUNT="build/disk"

echo ">> Deleting mounts..."
sudo umount -R $MOUNT/* &> /dev/null
sudo umount -R $MOUNT &> /dev/null
sudo losetup -D
sudo rm -rf $MOUNT