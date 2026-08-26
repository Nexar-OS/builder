#!/bin/bash

DISK_IMG="build/disk.img"
MOUNT="build/disk"

# Delete mount
sudo umount -R $MOUNT/* &> /dev/null
sudo umount -R $MOUNT &> /dev/null
rm -rf $MOUNT &> /dev/null

# Create disk
echo ">> Creating disk..."
dd if=/dev/zero of=$DISK_IMG bs=1MiB count=3072

echo ">> Mounting disk..."
LOOP="$(sudo losetup --find --show $DISK_IMG)"
echo " | LOOP: $LOOP"

# Create partitions
echo ">> Creating partitions..."
sudo parted "$LOOP" --script \
    mklabel msdos \
    mkpart primary 1MiB 40MiB \
    mkpart primary 41MiB 100% \
    set 1 boot on

echo "  | Formatting partitions..."
sudo mkfs.fat -F 32 "$LOOP"p1
sudo mkfs.ext4 "$LOOP"p2

# Mount partitions
echo " | Mounting partitions..."
mkdir -p $MOUNT
sudo mount "$LOOP"p2 $MOUNT
sudo mkdir -p $MOUNT/boot/efi
sudo mount "$LOOP"p1 $MOUNT/boot/efi

# Compress stages
sh script/compress_stages.sh

echo " | Extracting stages..."
for tar in build/staging/*.tar; do
    sudo tar -xpf "$tar" -C $MOUNT
done