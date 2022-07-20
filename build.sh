#!/bin/bash

set -e
shopt -s nocasematch


#
# Setup workspace if it is not set
#
if [ -z "$WORKSPACE" ]
then
  echo Initializing workspace
  if [ ! -e `pwd`/edksetup.sh ]
  then
    cd ..
  fi
# This version is for the tools in the BaseTools project.
# this assumes svn pulls have the same root dir
#  export EDK_TOOLS_PATH=`pwd`/../BaseTools
# This version is for the tools source in edk2
  export EDK_TOOLS_PATH=`pwd`/BaseTools
  echo $EDK_TOOLS_PATH
  source edksetup.sh BaseTools
else
  echo Building from: $WORKSPACE
fi

if  [[ ! -f `which build` || ! -f `which GenFv` ]];
then
  # build the tools if they don't yet exist. Bin scheme
  echo Building tools as they are not in the path
  make -C $WORKSPACE/BaseTools
elif [[ ( -f `which build` ||  -f `which GenFv` )  && ! -d  $EDK_TOOLS_PATH/Source/C/bin ]];
then
  # build the tools if they don't yet exist. BinWrapper scheme
  echo Building tools no $EDK_TOOLS_PATH/Source/C/bin directory
  make -C $WORKSPACE/BaseTools
else
  echo using prebuilt tools
fi

#
# Do the build!
#
build $@
exit $?
