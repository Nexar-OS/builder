#!/bin/bash

cd build/staging

for dir in */; do
    [ -d "$dir" ] || continue

    TAR=$(basename "$dir").tar
    echo "$dir => $TAR"

    fakeroot tar -cpf "$TAR" "$dir"
    rm -rf "$dir"
    sudo tar -xpf "$TAR"
    rm "$TAR"
done