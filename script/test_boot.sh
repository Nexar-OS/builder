#!/bin/bash

cd build

# Create disk
dd if=/dev/zero of=disk.img bs=1MiB count=3072

LOOP="$(sudo losetup --find --show disk.img)"
echo "LOOP: $LOOP"

# Create partitions
sudo parted "$LOOP" --script \
    mklabel msdos \
    mkpart primary 1MiB 40MiB \
    mkpart primary 41MiB 100% \
    set 1 boot on

sudo mkfs.fat -F 32 "$LOOP"p1
sudo mkfs.ext4 "$LOOP"p2

# Mount partitions
mkdir -p disk
sudo mount "$LOOP"p2 disk
sudo mkdir -p disk/boot/efi
sudo mount "$LOOP"p1 disk/boot/efi

# Copy root
sudo rsync -aHAX staging/base/ disk/

# Mount sys partitions
sudo mount --rbind /dev disk/dev
sudo mount --make-rslave disk/dev

sudo mount -t proc /proc disk/proc
sudo mount --rbind /sys disk/sys
sudo mount --make-rslave disk/sys

sudo mount --rbind /run disk/run
sudo mount --make-rslave disk/run

# Generate fstab
genfstab -U disk > disk/etc/fstab

# Setup grub
sudo chroot disk sh -c "grub-install --target=x86_64-efi --efi-directory=\"/boot/efi\" --bootloader-id=\"test\" --removable"
sudo chroot disk sh -c "grub-mkconfig -o /boot/grub/grub.cfg"

sudo tee disk/boot/grub/grub.cfg >/dev/null <<'EOF'
set timeout=5
set default=0

menuentry "Linux" {
    linux /boot/vmlinuz-6.18.42 root=/dev/vda2 init=/sbin/init rw console=tty0 console=ttyS0,115200
}
EOF

# Delete mount
sudo umount -R disk/* &> /dev/null
sudo umount -R disk
sudo losetup -d $LOOP
rm -rf disk

# Boot
cp /usr/share/edk2/x64/OVMF_VARS.4m.fd OVMF_VARS.fd
qemu-system-x86_64 \
    -machine q35 \
    -m 8G \
    -drive file=disk.img,format=raw,if=virtio \
    -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
    -drive if=pflash,format=raw,file=OVMF_VARS.fd \
    -serial stdio \
    -display none