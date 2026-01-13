#!/bin/bash
image_tag=mcp-server:latest
volume_mount=""
if [ $# -eq 1 ]; then
   mount_dir="$1"
   if [[ -d $mount_dir ]]; then
      volume_mount="--mount \"type=bind,src=$mount_dir,dst=/workspace\""
   fi
fi
tool=$(command -v docker 2>/dev/null || command -v podman 2>/dev/null)
here=$(dirname "$0")
env | sort | sed -E -e 's/(SECRET_KEY)=.*/\1*****/' > $HOME/.continue/env.log
$tool build -t $image_tag "$here" 2>/dev/null
$tool run --rm -i --network none $volume_mount $image_tag
