#!/bin/bash

cd build

# Create disk
dd if=/dev/zero of=disk.img bs=1MiB count=1024

LOOP="$(sudo losetup --find --show disk.img)"

sudo parted "$LOOP" --script \
    mklabel msdos \
    mkpart primary 1MiB 100% \
    set 1 boot on

sudo mkfs.ext4 "$LOOP"p1

mkdir disk
sudo mount "$LOOP"p1 disk


# Copy root
sudo rsync -aHAX staging/base/ disk/


# Setup grub
sudo grub-install --target=i386-pc --boot-directory=$(realpath disk/boot/) $LOOP

sudo tee disk/boot/grub/grub.cfg >/dev/null <<'EOF'
set timeout=5
set default=0

menuentry "Linux" {
    linux /boot/vmlinuz root=/dev/sda1 rw init=/sbin/init
}
EOF

sudo umount -R disk
sudo losetup -d $LOOP
rm -rf disk

qemu-system-x86_64 -drive file=disk.img,format=raw