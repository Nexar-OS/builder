#!/bin/bash
# Mount sys partitions
sudo mount --rbind /dev build/disk/dev
sudo mount --make-rslave build/disk/dev

sudo mount -t proc /proc build/disk/proc
sudo mount --rbind /sys build/disk/sys
sudo mount --make-rslave build/disk/sys

sudo mount --rbind /run build/disk/run
sudo mount --make-rslave build/disk/run

chroot build/disk