#!/bin/bash

set -e

# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  CURDIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
CURDIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

LOG=debug.log
OVMFBASE=$CURDIR/Build/OvmfX64/DEBUG_GCC/
OVMFCODE=$OVMFBASE/FV/OVMF_CODE.fd
OVMFVARS=$OVMFBASE/FV/OVMF_VARS.fd

qemu-system-x86_64 \
-name guest=win10-debug,debug-threads=on \
-drive if=pflash,format=raw,readonly=on,file=$OVMFCODE \
-drive if=pflash,format=raw,file=$OVMFVARS \
-m 8192 \
-boot menu=on,strict=on \
-device '{"driver":"pcie-root-port","port":0,"chassis":1,"id":"pci.1","bus":"pcie.0","multifunction":true,"addr":"0x1","x-pci-vendor-id":32902,"x-pci-device-id":6401,"x-pci-sub-vendor-id":5218,"x-pci-sub-device-id":31560}' \
-blockdev '{"driver":"host_device","filename":"/dev/disk/by-id/ata-Samsung_SSD_870_QVO_4TB_S5VYNG0NB00360W","aio":"native","node-name":"libvirt-1-storage","cache":{"direct":true,"no-flush":false},"auto-read-only":true,"discard":"unmap"}' \
-blockdev '{"node-name":"libvirt-1-format","read-only":false,"discard":"unmap","cache":{"direct":true,"no-flush":false},"driver":"raw","file":"libvirt-1-storage"}' \
-device '{"driver":"virtio-blk-pci","bus":"pci.1","addr":"0x0","drive":"libvirt-1-format","id":"virtio-disk0","write-cache":"on"}' \
-debugcon file:$LOG -global isa-debugcon.iobase=0x402 \
-serial stdio \
-nographic \
-nodefaults \
-s -S

exit $?
