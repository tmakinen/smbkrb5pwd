# $OpenLDAP$
# This work is part of OpenLDAP Software <http://www.openldap.org/>.
#
# Copyright 1998-2009 The OpenLDAP Foundation.
# Copyright 2004 Howard Chu, Symas Corp. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted only as authorized by the OpenLDAP
# Public License.
#
# A copy of this license is available in the file LICENSE in the
# top-level directory of the distribution or, alternatively, at
# <http://www.OpenLDAP.org/license.html>.

LDAP_SRC=../../..
LDAP_BUILD=$(LDAP_SRC)
LDAP_INC=-I$(LDAP_BUILD)/include -I$(LDAP_SRC)/include -I$(LDAP_SRC)/servers/slapd

SSL_INC=
SSL_LIB=-lcrypto

LIBTOOL=$(LDAP_BUILD)/libtool
CC=gcc
OPT=-g -O2

MIT_KRB5_INC=-I/usr/include
MIT_KRB5_LIB=-lkrb5

DEFS=
INCS=$(LDAP_INC) $(MIT_KRB5_INC) $(SSL_INC)
LIBS=$(MIT_KRB5_LIB) $(SSL_LIB)

MIT_KRB5_CLNT_LIB=-lkadm5clnt_mit

prefix=/usr/local
ldap_subdir=/openldap

libdir=$(prefix)/lib
libexecdir=$(prefix)/libexec
moduledir=$(libexecdir)$(ldap_subdir)

.PHONY: all
all:	smbkrb5pwd.la

smbkrb5pwd.lo:	smbkrb5pwd.c
	$(LIBTOOL) --mode=compile $(CC) $(OPT) $(DEFS) $(INCS) -c $?

smbkrb5pwd.la:	smbkrb5pwd.lo
	$(LIBTOOL) --mode=link $(CC) $(OPT) -version-info 0:1:0 \
	-rpath $(moduledir) -module -o $@ $? $(LIBS) $(MIT_KRB5_CLNT_LIB)

.PHONY: clean
clean:
	rm -f smbkrb5pwd.lo smbkrb5pwd.o smbkrb5pwd.la .libs/smbkrb5pwd.*

.PHONY: install
install: smbkrb5pwd.la
	mkdir -p $(DESTDIR)$(moduledir)
	$(LIBTOOL) --mode=install cp smbkrb5pwd.la $(DESTDIR)$(moduledir)
