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
#### OpenSSL
If you use secure connection WITHOUT certificates to router you should have ADH support enabled in OpenSSL.
To check if it enabled run:
   ```bash
   openssl ciphers -s ADH
   ```
For example:
   ```bash
   >openssl ciphers -s ADH
   TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256:ADH-AES256-GCM-SHA384:ADH-AES128-GCM-SHA256:ADH-AES256-SHA256:ADH-CAMELLIA256-SHA256:**ADH-AES128-SHA256**:ADH-CAMELLIA128-SHA256:ADH-AES256-SHA:ADH-CAMELLIA256-SHA:ADH-AES128-SHA:ADH-SEED-SHA:ADH-CAMELLIA128-SHA
   ```
If you don't see ADH-AES128-SHA256 in answer it means you can't connect to router via SSL/TLS without certificate.
You have the next choices:
* enable certificate for Mikrotik API-SSL. Check Mikrotik docs for this.
* enable ADH ciphers for openSSL. Checks docs for your system.
* use Linux distribution with already enabled ADH. For example, Ubuntu server 18.04.x has not support for ADH from box (OpenSSL 1.1.0g) but Ubuntu server 18.10 has (OpenSSL 1.1.1)
* use non-secure connection (but it is disabled in smartROS due to high security risks). As variant to create VPN connection to router and connect to API via such vpn.

### 4. Test connection via console script

---

### Known issues

#### 

