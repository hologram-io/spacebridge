#!/bin/bash

set -e

SIGNBIN=0

while getopts "s" opt; do
    case $opt in
        s)
            SIGNBIN=1
            ;;
    esac
done

OS="`uname`"
PLATFORM='unknown'
VE="ve/bin/"
MAKEZIP=0
PIFLAGS=""
case $OS in
  'Linux')
      PLATFORM="$(uname -m)-pc-linux-gnu"
    ;;
  MINGW32*)
      PLATFORM="i686-windows"
      VE="ve/Scripts/"
      MAKEZIP=1
      PIFLAGS+="--icon icons/hologram.ico --hiddenimport SocketServer"
      export TCL_LIBRARY=/c/Python27/tcl/tcl8.5
    ;;
  'Darwin')
      PLATFORM="x86_64-apple-darwin"
      PIFLAGS+="--icon icons/hologram.icns"
    ;;
  *)
    echo 'Invalid OS'
    exit
esac

version=$(cat version.txt)
buildname="spacebridge-$version-$PLATFORM"

if [ VE -a ! -d ./ve ] ; then
    virtualenv ve
fi

PIP=$VE
PIP+=pip
$PIP install --upgrade pip
$PIP install -r requirements.txt

PM=$VE
PM+=pyi-makespec
$PM $PIFLAGS -F -n spacebridge spacebridge.py

#This .bak and then deletion is to maintain compatibility with BSD sed
sed -i.bak "s/datas=\[\]/datas=\[\('version.txt', '.'\)\]/" spacebridge.spec
rm spacebridge.spec.bak

PI=$VE
PI+=pyinstaller
$PI spacebridge.spec

if [ "$SIGNBIN" -eq "1" ]; then
    cmd /c runsigntool.bat
fi

cd dist
mkdir -p $buildname/bin/
cp spacebridge $buildname/bin/
tar -jcvf $buildname.tar.bz2 $buildname

if [ "$MAKEZIP" -eq "1" ] ; then
    zip -r $buildname.zip $buildname
fi
