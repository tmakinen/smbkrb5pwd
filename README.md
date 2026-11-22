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
its password is changed. Samba password attributes are updated only for entries
with the `sambaSamAccount` object class.

## Known limitations

- Kerberos principal data is managed in the separate MIT Kerberos database;
  this overlay does not store Kerberos keys in LDAP user entries.
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

Before enabling Samba support, load a schema that defines `sambaSamAccount`,
`sambaNTPassword`, `sambaPwdLastSet`, `sambaPwdMustChange`, and
`sambaPwdCanChange`. With traditional `slapd.conf`, load the schema before
starting `slapd`. The overlay fails to initialize Samba support if these schema
elements are unavailable.

With OpenSSL 3, Samba NT hash generation uses MD4 from the legacy provider.
Ensure the OpenSSL legacy provider is installed and loadable by `slapd`.

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
olcSmbKrb5PwdCanChange: 60
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
smbkrb5pwd-enable krb5 samba
smbkrb5pwd-must-change 2592012
smbkrb5pwd-can-change 60
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
| `olcSmbKrb5PwdMustChange` | Samba password expiry interval in seconds, added to the time of the password change. |
| `olcSmbKrb5PwdCanChange` | Samba minimum password age in seconds; the resulting `sambaPwdCanChange` value is the time of the password change plus this interval. |
| `olcSmbKrb5PwdKrb5Realm` | Kerberos realm used to create user principals, for example `EDU.EXAMPLE.ORG`. |
| `olcSmbKrb5PwdRequiredClass` | If set, the entry must have this object class for Kerberos and Samba passwords to be modified, for example `posixAccount`. |

The `MustChange` and `CanChange` intervals default to zero; deleting either
configuration value resets that interval to zero. Kerberos mode requires a
`uid` value on each user entry and uses it to form the `uid@REALM` principal.

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

chown ldap:ldap /etc/openldap/smbkrb5pwd.keytab
```

Grant this service principal the required add-principal and change-password
permissions in the KDC's `kadm5.acl` file, and ensure the LDAP server can reach
`kadmind` for the configured realm. If `slapd` runs under a different
account/group, replace `ldap:ldap` with that account and group.

## Testing

The overlay activates when a password modify extended operation is requested.
For example:

```sh
ldappasswd -x -D uid=admin,ou=people,dc=edu,dc=example,dc=org -W \
  uid=user1,ou=people,dc=edu,dc=example,dc=org
```

The overlay writes diagnostic messages to `slapd`'s configured logging
destination. Depending on the system, this may be a log file, syslog, or the
system journal.

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
