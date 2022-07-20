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

$CURDIR/build.sh -a X64 \
-t GCC \
-p OvmfPkg/OvmfPkgX64.dsc \
-b DEBUG \
-DNETWORK_HTTP_BOOT_ENABLE=TRUE \
-DNETWORK_IP6_ENABLE=TRUE \
-DNETWORK_TLS_ENABLE \
-DSECURE_BOOT_ENABLE=TRUE \
-DTPM2_ENABLE=TRUE \
-DFD_SIZE_4MB \
-DSMM_REQUIRE=TRUE \
--pcd gEfiMdeModulePkgTokenSpaceGuid.PcdAcpiDefaultOemId="ALASKA" \
--pcd gEfiMdeModulePkgTokenSpaceGuid.PcdAcpiDefaultOemTableId=0x00002049204D2041 \
--pcd gEfiMdeModulePkgTokenSpaceGuid.PcdFirmwareVendor=L"AMI" \
--pcd gEfiMdeModulePkgTokenSpaceGuid.PcdAcpiDefaultCreatorId=0x20494D41

cp $CURDIR/Build/OvmfX64/DEBUG_GCC/FV/OVMF_CODE.fd $CURDIR/Build/OvmfX64/DEBUG_GCC/OVMF_CODE.secboot.fd

PYTHONPATH=$CURDIR/enroll/python $CURDIR/enroll/edk2-vars-generator.py -d -f OVMF_4M \
-e $CURDIR/Build/OvmfX64/DEBUG_GCC/X64/EnrollDefaultKeys.efi \
-s $CURDIR/Build/OvmfX64/DEBUG_GCC/X64/Shell.efi \
-c $CURDIR/Build/OvmfX64/DEBUG_GCC/OVMF_CODE.secboot.fd \
-V $CURDIR/Build/OvmfX64/DEBUG_GCC/FV/OVMF_VARS.fd \
-C `< $CURDIR/enroll/oem-string-vendor` \
-o $CURDIR/Build/OvmfX64/DEBUG_GCC/OVMF_VARS.secboot.fd

exit $?
