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
By default is in /opt/smartros/src/smartROS/settings.py
Usually yoy needn't edit this but in the case if startROS is called from otehr application changes may be required (for example, to forward logs in proper folder).
* **app_name**    = "smartros"             # keyword, don't change if not sure
* **app_tmp_dir** = "/tmp/" + app_name     # script must have write permissions to this folder
* **app_log_dir** = "/var/log/" + app_name # script must have write permissions to this folder

#### routers.json
JSON file containg credentials for all routers to connect to.
   ```
   {  Router1ShortName : {Router1Parameters} [,
      Router2ShortName : {Router2Parameters},
      ...
      ]
   }
   ```
*RouterXShortName* - number or string.

*RouterXParameters* - router's properties in JSON fromat

For example:
   ```json
   {
    "0":
     {
      "name" : "Main router",
      "description" : "Main router in office",
      "ip"   : "192.168.1.1",
      "port" : 8729,
      "api_ro_user"    : "api_ro", 
      "api_ro_pass"    : "pa$$w0rd1",
      "api_rw_user"    : "api_rw", 
      "api_rw_pass"    : "pa$$w0rd2",
      "api_ca_cert"    : null
     },
    "1":
     {
      "name" : "Backup router",
      "description" : "Backup router in office",
      "ip"   : "192.168.1.2",
      "port" : 8729,
      "api_ro_user"    : "api_ro", 
      "api_ro_pass"    : "pa$$w0rd3",
      "api_rw_user"    : "api_rw", 
      "api_rw_pass"    : "pa$$w0rd4",
      "api_ca_cert"    : "ca1.crt"
     }
    }
   ```
Here first router (shortname 0 or "0") will be connected using TLS ADH-AES128-SHA256 (without certificates, right now ADH supports only this cipher), the second one will be connected using certificate. Sure both routers must have API SSL enabled, proper users with mentioned passwords created and certificates for the second one generated. CA certificate of the second routers must be placed in the *smartROS/certs* folder.  

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
* enable certificate for Mikrotik API-SSL. Check Mikrotik [docs](https://wiki.mikrotik.com/wiki/Manual:Create_Certificates) or this my [script](https://github.com/BlackVS/Mikrotik-scripts/tree/master/scripts/OpenVPN%20-%20certificates) for this. In the last case you need just import scripts and call:
   ```bash
   /system script run certs_createCA   
   /system script run certs_createServer
   ```
   Generated server's certificate should be set in API-SSL properties in router (ip->services->api-ssl->certificate), CA certificate - imported to client and set in connection properties (routers.json). Default folder for certificates is /opt/smartros/src/cert/ )
* enable ADH ciphers for openSSL. Checks docs for your system.
* use Linux distribution with already enabled ADH. For example, Ubuntu server 18.04.x has not support for ADH from box (OpenSSL 1.1.0g) but Ubuntu server 18.10 has (OpenSSL 1.1.1)
* use non-secure connection (but it is disabled in smartROS due to high security risks). As variant to create VPN connection to router and connect to API via such vpn.

### 4. Test connection via console script
   ```bash
   cd /opt/smartros/src
   ./test_console.py
   ```
If all is ok you will see prompt and will be able run commands for example:
   ```bash
      /ip/route/print where="dst-address=='0.0.0.0/0'"
   ```
to check all default gateways.
Type /quit to exit from console

---

### Known issues

1. ADH support is not enabled in all OpenSSL versions by default. You need connect with certificates in such case or setup server with ADH support.

#### 

