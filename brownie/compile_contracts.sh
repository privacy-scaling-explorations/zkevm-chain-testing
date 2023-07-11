#!/bin/sh

ROOT="$(dirname $0)/.."

for file in $(find "$ROOT"/contracts/templates/ -iname '*.sol'); do
  name=$(basename $file)
  generated="$ROOT"/contracts/generated/$name
  cp "$file" "$generated"
  for inc in $(cat "$file" | grep "//@INCLUDE:"); do
    template=$(echo "$inc" | awk -F":" '{print $NF}')
    sed -i -e "\#$inc#r $ROOT/contracts/templates/$template" "$generated"
  done
done

OUTPUT_PATH="$ROOT/build/contracts"
mkdir -p "$OUTPUT_PATH"

solc-select install 0.8.13
solc-select use 0.8.13 

#SOLC=$(which solc || printf '%s' "docker run --rm -w /app -v $(pwd):/app ethereum/solc:0.8.16")
SOLC=/home/ubuntu/.local/bin/solc
$SOLC \
--metadata-hash none \
  --combined-json bin,bin-runtime,srcmap,srcmap-runtime,storage-layout \
  --optimize \
  --optimize-runs 4294967295 \
  --overwrite \
  --abi \
  -o "$OUTPUT_PATH" \
  $(find "$ROOT"/contracts/ -iname '*.sol' | grep -v templates/)
