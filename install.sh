#!/bin/bash

sudo echo

APPDIR=smartros
APPNAME="SmartROS API"
INSTALLDIR=/opt/$APPDIR
LOGDIR=/var/log/$APPDIR
TEMPDIR=/tmp/$APPDIR
ETCDIR=/etc/$APPDIR
GITURL=https://github.com/BlackVS/smartROS.git

WHITE='\033[1;37m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m'
BOLD="\e[1m"
NOBOLD="\e[21m"

onerror() {
    echo " FAILED, aborting script"
    exit 1
}

trap 'onerror' ERR

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAIL${NC}, aborting script"
        exit 1
    fi
}

function print_h0(){
    echo -e "${WHITE}${BOLD}$@${NOBOLD}${NC}"
}

function print_h1(){
    echo -e " * ${YELLOW}$@${NC} : "
}

function print_h1n(){
    echo ""
    echo -n -e " * ${YELLOW}$@${NC} : "
}

function run() { 
    print_h1n $1
    #echo -n \
    ${@:2}
    check
}

print_h0 "Installing: $APPNAME"
print_h0 "Install to: $INSTALLDIR"

run "Creating folder $INSTALLDIR" \
sudo mkdir $INSTALLDIR

run "cloning from git" \
sudo git clone $GITURL $INSTALLDIR

run "Entering $INSTALLDIR" \
cd $INSTALLDIR

#run "switching to dev" \
#sudo git checkout dev

echo ""
print_h1 "installing python3-pip"
echo ""
sudo apt update
sudo apt-get -qq install python3-pip -y 1>/dev/null
check

run "installing dependencies" \
sudo pip3 -q install -r requirements.txt

print_h1 "Creating default log dir: $LOGDIR"
sudo mkdir $LOGDIR
sudo chmod a+w $LOGDIR
check

print_h1 "Creating default temp dir: $TEMPDIR"
sudo mkdir $TEMPDIR
sudo chmod a+w $TEMPDIR
check

print_h1 "Creating config dir: $ETCDIR"
sudo mkdir $ETCDIR
check

print_h1 "Creating certificates' dir: $ETCDIR/certs"
sudo mkdir $ETCDIR/certs
check

print_h1 "Creating default settings:"
sudo cp $INSTALLDIR/src/smartROS/main.conf.template $ETC/main.conf
check

print_h1 "Creating routers.json config file:"
sudo cp $INSTALLDIR/src/smartROS/routers.json.template $ETC/routers.json
check

print_h1 "WARNING: please manually check and update permission for temp/log folders, by default ALL have write permissions to these folder"

echo ""
print_h0 "Please update config files:"
echo " $ETCDIR/main.conf"
echo " $ETCDIR/routers.json"
print_h0 "Add if required certificates to certs folder:"
echo " $ETCDIR/certs/"
echo " "
print_h0 "and test connection running test console (by default to router 0):"
echo " $INSTALLDIR/src/test_console.py"
echo " "
print_h0 "In console try commands:"
echo "   /ip/route/print"
echo "   /quit"


print_h0 "The END"
