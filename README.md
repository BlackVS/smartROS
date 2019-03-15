# secure ROS API (under development)

ROS API wrapper

Main idea to try secure low-level ROS API (due to starting from 6.43 passwords sents plain i.e. TLS/SSL **must** be used) and create more user friendly IP (i.e. without necessity know low level API)

## Features
- [x] low level API included but not directly accessible from client side
- [x] SSL/TLS used by default
- [x] server's certificates check supported (client certificates not supported by ROS for now :( )
- [x] router device can be pre-configured - config/credentials stored separatly. Via proper Linux permisisons these settings not available for client (due to very often cleint is web based service)
- [x] API wrapped in black-box style - i.e. inside client's code you can just receive context of desired router 
      and do only listed for this router actions i.e. no full control on router given. 
      ROS have rediculus persmissions controls for router users.  
    
Good security for ROS API can be achieved only combining all of these:
- secureROS API with SSL+certificates
- proper firewall/permisiions configuration on server side 
- proper firewall/permissions configuration on router side (i.e. at least don't use admin/full access logins for API %)

## Configuration / Installation
1. Router:
- enable _api-ssl_
- enable 8729 (or another) port only for specific peers via firewall
- add _Available From_ in api-ssl config
- use router certificate
- create own _ro_ and _rw_ users for api and restrict access for specific API

###Installation:                                        
   Run:
   ```bash
   cd ~
   ```
   Edit config files and run script (see log of install.sh for details)

 
 
### Settings

### Debug

---

### Known issues

#### 

