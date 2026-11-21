# smbkrb5pwd

Documentation is available on the [project wiki](https://github.com/opinsys/smbkrb5pwd/wiki).

## Overview

`smbkrb5pwd` is an OpenLDAP (`slapd`) overlay that changes LDAP, Samba, and MIT
Kerberos passwords together. It intercepts LDAP Password Modify Extended
Operations and updates the related passwords. It is based on the `smbk5pwd`
overlay, which provides similar functionality for Heimdal Kerberos.

The overlay links against `libkadm5clnt_mit` and contacts `kadmind` to modify
Kerberos principals. It authenticates to the Kerberos administration service
using a service principal and keytab.

When an LDAP password is changed, the overlay checks whether a principal named
`uid@REALM` exists and creates it if it does not. If the principal exists, only
its password is changed.

## Known limitations

- Kerberos data cannot be stored in the same objects as users because of
  locking issues.
- Principals are always named `uid@REALM`; their names cannot be customized.
- Changing an LDAP user's `uid` does not automatically delete the old Kerberos
  principal.
- Deleting an LDAP user does not automatically delete the Kerberos principal.

## Installation

Place the `smbkrb5pwd` directory under `contrib/slapd-modules` in a full
OpenLDAP source tree. After building OpenLDAP, build and install the overlay:

```sh
cd contrib/slapd-modules/smbkrb5pwd
make
make install moduledir=/path/to/slapd/modules
```

## Configuration

Load the module and configure it for the database.

### `cn=config`

Load the module:

```ldif
dn: cn=module{0},cn=config
objectClass: olcModuleList
cn: module
olcModulepath: /path/to/slapd/modules
olcModuleload: smbkrb5pwd
```

Configure the overlay:

```ldif
dn: olcOverlay={0}smbkrb5pwd,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSmbKrb5PwdConfig
olcOverlay: {0}smbkrb5pwd
olcSmbKrb5PwdEnable: samba
olcSmbKrb5PwdEnable: krb5
olcSmbKrb5PwdMustChange: 2592012
olcSmbKrb5PwdKrb5Realm: EDU.EXAMPLE.ORG
olcSmbKrb5PwdRequiredClass: posixAccount
```

### Traditional `slapd.conf`

Configure the overlay inside its database definition:

```conf
database mdb
suffix "dc=edu,dc=example,dc=org"
directory /var/lib/ldap
overlay smbkrb5pwd
smbkrb5pwd-enable krb5
smbkrb5pwd-realm EDU.EXAMPLE.ORG
smbkrb5pwd-required-class posixAccount
```

The legacy `smbkrb5pwd-krb5realm` keyword is accepted as an alias for
`smbkrb5pwd-realm`. The older `smbkrb5pwd-requiredclass` keyword is accepted as
an alias for `smbkrb5pwd-required-class`.

### Configuration options

| `cn=config` attribute | Description |
| --- | --- |
| `olcSmbKrb5PwdEnable` | Enables `samba` and/or `krb5`. If omitted, or if both values are specified, both are enabled. |
| `olcSmbKrb5PwdMustChange` | Password expiry interval in seconds; currently applies only to Samba. |
| `olcSmbKrb5PwdKrb5Realm` | Kerberos realm used to create user principals, for example `EDU.EXAMPLE.ORG`. |
| `olcSmbKrb5PwdRequiredClass` | If set, the entry must have this object class for Kerberos and Samba passwords to be modified, for example `posixAccount`. |

## Kerberos principal

The overlay reads its keytab from `/etc/openldap/smbkrb5pwd.keytab`. It looks
for a principal named `smbkrb5pwd/FQDN@REALM`. Ensure the server's fully
qualified domain name resolves correctly; for example, `/etc/hosts` could
contain:

```text
10.11.12.13 server.edu.example.org server
```

Create the service principal and export it to the keytab:

```sh
kadmin.local -q "addprinc -randkey smbkrb5pwd/server.edu.example.org@EDU.EXAMPLE.ORG"
kadmin.local -q "ktadd -k /etc/openldap/smbkrb5pwd.keytab \
 smbkrb5pwd/server.edu.example.org@EDU.EXAMPLE.ORG"

chown openldap.openldap /etc/openldap/smbkrb5pwd.keytab
```

## Testing

The overlay activates when a password modify extended operation is requested.
For example:

```sh
ldappasswd -x -D uid=admin,ou=people,dc=edu,dc=example,dc=org -W \
  uid=user1,ou=people,dc=edu,dc=example,dc=org
```

The overlay writes debug information to `slapd`'s log, which is commonly
`/var/log/syslog` on Ubuntu.

## License

`smbkrb5pwd` is based on the `smbk5pwd` overlay in the OpenLDAP source tree and
is licensed under the OpenLDAP Public License.

Copyright 2004-2010 The OpenLDAP Foundation.  
Portions Copyright 2004-2005 Howard Chu, Symas Corp. All rights reserved.  
Portions Copyright 2010-2013 Opinsys Oy.  
Portions Copyright 2026 Timo Mäkinen.

Redistribution and use in source and binary forms, with or without
modification, are permitted only as authorized by the OpenLDAP Public License.

A copy of the license is available in the `LICENSE` file in the top-level
directory of the distribution, or at
[openldap.org/license.html](https://www.openldap.org/license.html).
