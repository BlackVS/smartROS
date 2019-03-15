#!/bin/bash

sudo echo

APPDIR=secROSAPI
APPNAME="Secure ROS API"
INSTALLDIR=/opt/$APPDIR

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

print_h0 "Installing $APPNAME"
print_h0 "Install bot to: $INSTALLDIR"

run "Creating folder $INSTALLDIR" \
sudo mkdir $INSTALLDIR

run "cloning from git" \
#sudo git clone https://github.com/BlackVS/telegram-bot.git $INSTALLDIR

run "Entering $INSTALLDIR" \
cd $INSTALLDIR

#run "switching to dev" \
#sudo git checkout dev

echo ""
print_h1 "installing python3-pip"
echo ""
sudo apt-get -qq install python3-pip -y 1>/dev/null
check

run "installing dependencies" \
sudo pip3 -q install -r requirements.txt

echo ""
print_h0 "Please edit config files:"
echo " $INSTALLDIR/config/settings.py"
echo " "
print_h0 "The END"
