# Smart ROS API (under development)

ROS API wrapper

The main idea is to make low-level ROS API more human-friendly + make it more secure (due to starting from 6.43 passwords sents plain i.e. TLS/SSL **must** be used)

## Features
- [x] low level API included but not directly accessible from client side
- [x] SSL/TLS used by default
- [x] server's certificates check supported (client certificates not supported by ROS for now :( )
- [x] router device can be pre-configured - config/credentials stored separetly. Via proper Linux permisisons these settings not available for client (due to very often cleint is web based service)
- [x] supports 'where' conditions in human readable form, for example try in console (included in project):
   ```bash
      /ip/route/print where="dst-address=='0.0.0.0/0'"
   ```
   or
   ```bash
      /ip/firewall/address-list/print where="list==Blacklist and address=='8.8.8.8'"
   ```
- [x] two styles API calls supported i.e.:
   ```python
      import smartROS
      router = smartROS.getRouter("Main")
      print( router.ip.route.print (where="dst-address=='0.0.0.0/0'") )
   ```
   and
   ```python
      import smartROS
      router = smartROS.getRouter("Main")
      print( router.do ("/ip/route/print", where="dst-address=='0.0.0.0/0'") )
   ```
both do the same - get list of default gateways

Good security for ROS API can be achieved only combining at least:
- secureROS API with SSL+certificates
- proper firewall/permisiions configuration on server side 
- proper firewall/permissions configuration on router side (i.e. at least don't use admin/full access logins for API %)

## Configuration / Installation
### 1. Router:
- enable _api-ssl_
- enable 8729 (or another) port only for specific peers via firewall
- add _Available From_ in api-ssl config
- use router certificate
- create own _ro_ and _rw_ users for api and restrict access for specific API

### 2. Linux/ubuntu server:

   Run:
   ```bash
   cd ~
   wget https://raw.githubusercontent.com/BlackVS/smartROS/master/install.sh -O - | bash
   ```
 
### 3. Settings
#### settings.py
#### routers.json

### 4. Test connection via console script

---

### Known issues

#### 

