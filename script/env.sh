#!/bin/sh

export SYSROOT="$(realpath build/toolchain/sysroot)"
export CC="$(realpath build/toolchain/binaries/bin/x86_64-placeholder-linux-gnu-gcc)"
export PKG_CONFIG_SYSROOT_DIR="$SYSROOT"
export PKG_CONFIG_LIBDIR="$SYSROOT/usr/lib/pkgconfig:$SYSROOT/usr/lib64/pkgconfig:$SYSROOT/usr/share/pkgconfig"