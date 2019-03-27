# Smart ROS API (under development)

ROS API wrapper

The main idea is to make low-level ROS API more human-friendly + make it more secure (due to starting from 6.43 passwords are sent plain i.e. TLS/SSL **must** be used)

## Features
- [x] low level API included but not directly accessible from client side
- [x] SSL/TLS used by default
- [x] server's certificates check supported (client certificates not supported by ROS for now :( )
- [x] router device can be pre-configured - config/credentials stored separately. Via proper Linux permisisons these settings not available for client (due to very often client is web based service)
- [x] supports 'where' conditions in human readable form, for example try in console (included in this project):
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
By default is in */etc/smartros/main.conf*
Usually you needn't edit this settings but in the case if startROS is called from other application changes may be required (for example, to forward logs in proper folder).
* **app_tmp_dir** : by default /tmp/smartros - temp dir, script must have write permissions to this folder
* **app_log_dir** : by default /var/log/smartros" - log dir, script must have write permissions to this folder
* **app_certs_dir** : by default /etc/smartros/certs - certificates dir, script must have read permissions to this folder
* **debug** : set to True if need verbose debug information in the console and logs

#### routers.json
By default is in */etc/smartros/routers.conf*
JSON file contains credentials for all routers to connect to.
   ```
   {  Router1ShortName : {Router1Parameters} [,
      Router2ShortName : {Router2Parameters},
      ...
      ]
   }
   ```
*RouterXShortName* - number or string, used in *smartROS.getRouter()* call as first argument.

*RouterXParameters* - router's properties in JSON format.

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
Here is the first router (shortname 0 or "0") will be connected to using TLS ADH-AES128-SHA256 (without certificates, right now ROS supports only this cipher for SSL without certificates), the second one will be connected to using certificate. Sure both routers must have API SSL enabled, proper users with mentioned passwords created and certificates for the second one generated. CA certificate named *ca1.crt*  of the second router must be placed in the *certs* folder.  In teh case of realtive path of certificate given it will be searched starting from **app_certrs_dir**

#### OpenSSL
If you use secure connection WITHOUT certificates to router you must have ADH support enabled in OpenSSL.
To check if it enabled run in terminal:
   ```bash
   openssl ciphers -s ADH
   ```
For example:
   ```bash
   >openssl ciphers -s ADH
   TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256:ADH-AES256-GCM-SHA384:ADH-AES128-GCM-SHA256:ADH-AES256-SHA256:ADH-CAMELLIA256-SHA256:**ADH-AES128-SHA256**:ADH-CAMELLIA128-SHA256:ADH-AES256-SHA:ADH-CAMELLIA256-SHA:ADH-AES128-SHA:ADH-SEED-SHA:ADH-CAMELLIA128-SHA
   ```
If you don't see ADH-AES128-SHA256 in answer it means you can't connect to router via SSL/TLS without certificate.
You have the next choices in such case:
* enable certificate for Mikrotik API-SSL. Check Mikrotik [docs](https://wiki.mikrotik.com/wiki/Manual:Create_Certificates) or my [script](https://github.com/BlackVS/Mikrotik-scripts/tree/master/scripts/OpenVPN%20-%20certificates) for this. In the last case you need just import scripts and call:
   ```bash
   /system script run certs_createCA   
   /system script run certs_createServer
   ```
   Generated server's certificate should be set in API-SSL properties in router (*ip->services->api-ssl->certificate*), CA certificate - imported to client and set in connection properties ( *api_ca_cert* property in corresponding router's settings in *routers.json* ). Default folder for certificates is _/opt/smartros/src/smartROS/cert/_ )
* enable ADH ciphers for OpenSSL. Checks docs for your system how to do this (it is a good quest).
* use Linux distribution with already enabled ADH. For example, Ubuntu Server 18.04.x has not support for ADH from box (OpenSSL 1.1.0g) but Ubuntu Server 18.10 has (OpenSSL 1.1.1)
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

### Syntax
Each command ("sentence") to router costs of:
**command** iself, it is in form "/menu1/menu2/menu3/command". For example here
   ```bash
      /ip/firewall/address-list/print where="list==Blacklist and address=='8.8.8.8'"
   ```
_ip_, _firewall_, _address_ - menu and submenu of RouterOS, _print_ - command. Usually they are the same as in the WinBox terminal.

### Syntax. WHERE
Some commands may use conditional clause to restrict result i.e. for example to find default gateways you need execute next commands using low-level RouterOS API:

   ```bash
   <--- '/ip/route/print'
   <--- '?=dst-address=0.0.0.0/0'
   <--- EOS
   ```
But if we need to check if some ip containg in Blacklist address list commands will look like:
   ```bash
   <--- '/ip/firewall/address-list/print'
   <--- '?=list=Blacklist'
   <--- '?=address=1.2.3.4'
   <--- '?#&'
   <--- EOS
   ```
i.e. little bit tricky. Espsecially for people who not familiar with Reverse Polish notation (RPN). 
You may learn RouterOS API [here](https://wiki.mikrotik.com/wiki/Manual:API) but SmartROS allows you do not do this and write commands in more convinient form, for above examples to do:
   ```bash
   /ip/route/print where="dst-address=0.0.0.0/0"
   ```
   and
   ```bash
   /ip/firewall/address-list/print where="list=='Blacklist' and address=='1.2.3.4'"
   ```
   or in python:
   ```python
      import smartROS
      router = smartROS.getRouter("Main")
      print( router.do( "/ip/firewall/address-list/print", where = "list=='Blacklist' and address=='1.2.3.4'" ) )
   ```
   
   respectivly.
   Here are some rules for where conditions:
#### 1. Where condition looks like:
   ```bash
   where=condition
   ```
#### 2. Condition may consist of:
   * == equal
   * != not equal
   * <  less
   * \>  greater
   * <= less or equal
   * \>= greater or equal
   * AND - and
   * OR  - or
   * NOT - not 
   * HAS - special operation which allows to check if attribute present in results. For example, dynamic routes have _dynamic=True_, but non-dynamic routes not contains attribute _dynamic_ at all i.e. to get dynamic routes just call:
   ```bash
   /ip/route/print where="dynamic==true"
   ```
   or in python:
   ```python
      import smartROS
      router = smartROS.getRouter("Main")
      print( router.ip.route.print( where = "dynamic==true" ) )
   ```

But if you need non dynamic routes and run
   ```bash
   /ip/route/print where="dynamic==false"
   ```
you will get empty result ALWAYS. Becausae non-dynamic routes haven't _dynamic_ property at all. In this case you can write:
   ```bash
   /ip/route/print where="has not dynamic"
   ```
and this will work. Little bit crazy but it is specific of RouterOS %)

#### 3. You may use parenthesis to create more complex conditions.
#### 4. You may use in conditions next arguments:
_identifiers_ - consist of alhphas, digits and "\_". Also identifiers may start from dot (for example, _.id_)
_numbers_
_ipv4_ - ipv4 addresses and networks can be used without quotes
_\*NNN_ - special values, indexes
_true/false_ or _yes/no_ - boolean. _yes_ equal to _true_, _no_ to _false_.
Rest of values must be used taken in quotes (single or double). I.e., for example, ipv6 addresses or any values which contains other non-alphanum symbols.

### Syntax. Setting values
Some commands may use parameters (set some property somewhere in router).
For example, low-level commands to add ip 1.2.3.4 to blacklist will look like:
   ```bash
   <--- '/ip/firewall/address-list/add'
   <--- '=address=1.2.3.4'
   <--- '=list=Blacklist'
   <--- '=timeout=86400'
   <--- '=comment=Added via ban ip script'
   <--- EOS
   ```
Using SmartROS commands will be:
   console:
   ```bash
   /ip/firewall/address-list/add address='1.2.3.4' list='Blacklist' timeout=86400 comment='Added via ban ip script'
   ```
   python code (use "\_\_" instead "-" in the command if use first style calls)  :
   ```python
      import smartROS
      router = smartROS.getRouter("Main")
      router.ip.firewall.address__list.add (address='1.2.3.4', list='Blacklist', timeout=86400, comment='Added via ban ip script')
   ```
   or
   ```python
      import smartROS
      router = smartROS.getRouter("Main")
      router.do ("/ip/firewall/address-list/add", address='1.2.3.4', list='Blacklist', timeout=86400, comment='Added via ban ip script')
   ```
Numbers/booleans can be used without quotes, all other values (including ipv4 addresses) must be single- or double- quoted.
Sure you must use API user with write permissions for this.
Also preferred order is - name of atribitues in the left, values in the right.

**ATTENTION!** _SmartROS nothing knows about structure of RouterOS commands or which parameters where must be used. SmartROS just converts your human-readable commands to the low-level ones and passes them to RouterOS_

---

### Known issues

1. ADH support is not enabled in all OpenSSL versions by default. You need connect with certificates in such case or setup server with ADH support.

#### 

