Documentation is available at: https://github.com/opinsys/smbkrb5pwd/wiki


OVERVIEW

smbkrb5pwd is an OpenLDAP (slapd) overlay to change LDAP, Samba and MIT 
Kerberos passwords at the same time. It intercepts the LDAP 
PasswordModify Extended Operations and changes all the passwords. It is 
based on the smbk5pwd overlay that provides similar functionality for 
Heimdal kerberos.

The overlay is linked against libkadm5clnt_mit and contacts kadmind to
modify Kerberos principals. It uses a service principal and keytab to
authenticate to the Kerberos administration service.

When LDAP password is changed, the overlay checks whether a principal 
uid@REALM exists and creates it if it does not. If the principal exists, 
only the password is changed.


KNOWN LIMITATIONS

* Because of locking issues, kerberos data cannot be stored in same 
  objects as users
* Principals are always named uid@REALM and cannot be changed
* If uid in LDAP is changed, the old kerberos principal is not deleted 
  automatically
* If LDAP user is deleted, the kerberos principal is not deleted 
  automatically


INSTALLATION

To compile the overlay the easiest way is to get the full source code 
for OpenLDAP and place the smbkrb5pwd directory under 
contrib/slapd-modules directory. After compiling OpenLDAP normally the 
overlay can be compiled simply by running make in the smbkrb5pwd 
directory.


cd contrib/slapd-modules/smbkrb5pwd
make
make install moduledir=/path/to/slapd/modules


SLAPD CONFIGURATION

To configure the overlay, the module needs to be loaded and configured 
for the database.

dn: cn=module{0},cn=config
objectClass: olcModuleList
cn: module
olcModulepath: /path/to/slapd/modules
olcModuleload: smbkrb5pwd

Overlay configuration:

dn: olcOverlay={0}smbkrb5pwd,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSmbKrb5PwdConfig
olcOverlay: {0}smbkrb5pwd
olcSmbKrb5PwdEnable: samba
olcSmbKrb5PwdEnable: krb5
olcSmbKrb5PwdMustChange: 2592012
olcSmbKrb5PwdKrb5Realm: EDU.EXAMPLE.ORG
olcSmbKrb5PwdRequiredClass: posixAccount


For a traditional `slapd.conf`, configure the overlay inside its database
definition:

```conf
database mdb
suffix "dc=edu,dc=example,dc=org"
directory /var/lib/ldap
overlay smbkrb5pwd
smbkrb5pwd-enable krb5
smbkrb5pwd-realm EDU.EXAMPLE.ORG
smbkrb5pwd-required-class posixAccount
```

The legacy `smbkrb5pwd-krb5realm` keyword is also accepted as an alias for
`smbkrb5pwd-realm`. The older `smbkrb5pwd-requiredclass` keyword is also
accepted as an alias for `smbkrb5pwd-required-class`.


The overlay accepts the following configuration attributes:

* olcSmbKrb5PwdEnable - samba / krb5
  - Enable samba/kerberos functionality of the module, same as 
    olcSmbK5PwdEnable in smbk5pwd. If attribute is not set or both are set, 
    both passwords are changed.
* olcSmbKrb5PwdMustChange - e.g. 31536000 (year), 2592000 (30 days)
  - Time in seconds before the password expires (currently affects only Samba)
* olcSmbKrb5PwdKrb5Realm - e.g. EDU.EXAMPLE.ORG
  - Kerberos realm used to create user principals
* olcSmbKrb5PwdRequiredClass - e.g. posixAccount
  - If set, the entry needs to have this object class for the kerberos 
    principal and samba passwords to be modified


KERBEROS PRINCIPAL

smbkrb5pwd connects to kadmind using a principal found in keytab file 
/etc/openldap/smbkrb5pwd.keytab. The keytab is searched for
principal that has name smbkrb5pwd/FQDN@REALM. Note that “hostname -f” 
should return fqdn. One way to achieve this is to put fqdn as the first 
name in /etc/hosts for the server’s ip address (here 10.11.12.13):


10.11.12.13   server.edu.example.org server


Create the service principal and export it to the keytab:


kadmin.local -q "addprinc -randkey smbkrb5pwd/server.edu.example.org@EDU.EXAMPLE.ORG"
kadmin.local -q "ktadd -k /etc/openldap/smbkrb5pwd.keytab \
 smbkrb5pwd/server.edu.example.org@EDU.EXAMPLE.ORG"

chown openldap.openldap /etc/openldap/smbkrb5pwd.keytab


TESTING

The overlay activates itself when an password change exop request is 
made. This can be done for example with ldappasswd command:

ldappasswd -x -D uid=admin,ou=people,dc=edu,dc=example,dc=org -W \
 uid=user1,ou=people,dc=edu,dc=example,dc=org

smbkrb5pwd writes debug information to slapd’s logfile which is normally 
/var/log/syslog in Ubuntu.


LICENSE

smbkrb5pwd is based on smbk5pwd overlay that can be found under 
http://www.openldap.org/devel/cvsweb.cgi/contrib/slapd-modules/smbk5pwd
in OpenLDAP's sources. smbkrb5pwd is licensed under The OpenLDAP Public 
License that is also used for smbk5pwd.


Copyright 2004-2010 The OpenLDAP Foundation.
Portions Copyright 2004-2005 Howard Chu, Symas Corp. All rights reserved.
Portions Copyright 2010-2013 Opinsys Oy.

Redistribution and use in source and binary forms, with or without
modification, are permitted only as authorized by the OpenLDAP
Public License.

A copy of this license is available in the file LICENSE in the
top-level directory of the distribution or, alternatively, at
<http://www.OpenLDAP.org/license.html>.
