#!/bin/bash

for dir in build/staging/*/; do
    [ -d "$dir" ] || continue

    TAR=build/staging/$(basename "$dir").tar
    echo "$dir => $TAR"

    fakeroot tar -cpf "$TAR" -C "$dir" .
    rm -rf "$dir"
done