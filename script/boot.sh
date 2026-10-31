#!/bin/bash
MOUNT="build/disk"

if [ ! -d "$MOUNT" ] || ! mountpoint -q "$MOUNT"; then
    source script/stages_to_disk.sh
fi

# Generate fstab
ROOT_PART="$(findmnt -n -o SOURCE $MOUNT)"
EFI_PART="$(findmnt -n -o SOURCE $MOUNT/boot/efi)"
EFI_UUID="$(sudo blkid -s UUID -o value $EFI_PART)"
ROOT_UUID="$(sudo blkid -s UUID -o value $ROOT_PART)"

echo ">> Generating fstab..."
cat <<EOF | sudo tee "$MOUNT/etc/fstab"
UUID=$ROOT_UUID            /               ext4            rw,relatime     0 1
UUID=$EFI_UUID            /boot/efi       vfat            rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro   0 2
EOF

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
sudo sed -i "s|$EFI_PART|/dev/vda1|g" "$MOUNT/boot/grub/grub.cfg"
sudo sed -i "s|$ROOT_PART|/dev/vda2|g" "$MOUNT/boot/grub/grub.cfg"

# Delete mount
sh script/umount.sh

# Boot
echo ">> Booting..."
cp /usr/share/edk2/x64/OVMF_VARS.4m.fd build/OVMF_VARS.fd
qemu-system-x86_64 \
    -machine q35 \
    -m 8G \
    -drive file=build/disk.img,format=raw,if=virtio \
    -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
    -drive if=pflash,format=raw,file=build/OVMF_VARS.fd \
    -device virtio-vga \
    -display gtk