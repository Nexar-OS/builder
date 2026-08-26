#!/bin/bash
sh script/stages_to_disk.sh

MOUNT="build/disk"

# Generate fstab
echo ">> Generating fstab..."
genfstab -U $MOUNT | sudo tee $MOUNT/etc/fstab

# Mount sys partitions
echo ">> Mounting system partitions..."
sudo mount --rbind /dev build/disk/dev
sudo mount --make-rslave build/disk/dev

sudo mount -t proc /proc build/disk/proc
sudo mount --rbind /sys build/disk/sys
sudo mount --make-rslave build/disk/sys

sudo mount --rbind /run build/disk/run
sudo mount --make-rslave build/disk/run

# Setup grub
echo ">> Setting up grub..."
sudo chroot $MOUNT sh -c "grub-install --target=x86_64-efi --efi-directory=\"/boot/efi\" --bootloader-id=\"test\" --removable" &> /dev/null
echo " | Generating grub.cfg."
sudo chroot $MOUNT sh -c "grub-mkconfig -o /boot/grub/grub.cfg" &> /dev/null

echo " | Overwriting grub.cfg."
sudo tee $MOUNT/boot/grub/grub.cfg >/dev/null <<'EOF'
set timeout=5
set default=0

menuentry "Linux" {
    linux /boot/vmlinuz-6.18.42 root=/dev/vda2 rw console=ttyS0,115200
}
EOF

# Delete mount
echo ">> Deleting mounts..."
sudo umount -R $MOUNT/* &> /dev/null
sudo umount -R $MOUNT &> /dev/null
sudo losetup -D
rm -rf $MOUNT

# Boot
echo ">> Booting..."
cp /usr/share/edk2/x64/OVMF_VARS.4m.fd build/OVMF_VARS.fd
qemu-system-x86_64 \
    -machine q35 \
    -m 8G \
    -drive file=build/disk.img,format=raw,if=virtio \
    -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
    -drive if=pflash,format=raw,file=build/OVMF_VARS.fd \
    -serial stdio \
    -display none