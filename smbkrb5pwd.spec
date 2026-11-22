%global openldap_version 2.6.13

Name:           openldap-smbkrb5pwd
Version:        %{openldap_version}
Release:        1%{?dist}
Summary:        Samba and MIT Kerberos password overlay for OpenLDAP
License:        OLDAP-2.8
URL:            https://github.com/tmakinen/smbkrb5pwd

# The EPEL OpenLDAP server package does not ship the internal slapd headers.
# Build against the matching upstream server sources instead.
Source0:        https://openldap.org/software/download/OpenLDAP/openldap-release/openldap-%{openldap_version}.tgz
# A clean source archive of this module directory (Makefile, LICENSE, README.md,
# and smbkrb5pwd.c), named smbkrb5pwd-<version>.tar.gz.
Source1:        smbkrb5pwd-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  krb5-devel
BuildRequires:  libtool-ltdl-devel
BuildRequires:  make
BuildRequires:  openldap-servers = %{openldap_version}
BuildRequires:  openssl-devel

Requires:       openldap-servers%{?_isa} = %{openldap_version}

%description
The smbkrb5pwd slapd overlay updates LDAP user passwords, Samba password
attributes, and MIT Kerberos principals when an LDAP Password Modify Extended
Operation is performed.

%prep
%setup -q -c -T
mkdir openldap
tar -xzf %{SOURCE0} --strip-components=1 -C openldap
mkdir -p openldap/contrib/slapd-modules/smbkrb5pwd
tar -xzf %{SOURCE1} --strip-components=1 \
    -C openldap/contrib/slapd-modules/smbkrb5pwd

%build
cd openldap
%configure \
    --enable-dynamic \
    --enable-modules \
    --enable-backends=no \
    --enable-overlays=no \
    --disable-static \
    --with-pic \
    --libexecdir=%{_libdir}

%make_build -C include
%make_build -C contrib/slapd-modules/smbkrb5pwd \
    CC="%{__cc}" OPT="%{optflags}" moduledir="%{_libdir}/openldap"

%install
%make_install -C openldap/contrib/slapd-modules/smbkrb5pwd \
    moduledir="%{_libdir}/openldap"
rm -f %{buildroot}%{_libdir}/openldap/smbkrb5pwd.la

install -Dpm 0644 openldap/contrib/slapd-modules/smbkrb5pwd/LICENSE \
    %{buildroot}%{_licensedir}/%{name}/LICENSE
install -Dpm 0644 openldap/contrib/slapd-modules/smbkrb5pwd/README.md \
    %{buildroot}%{_docdir}/%{name}/README.md

%files
%license %{_licensedir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README.md
%{_libdir}/openldap/smbkrb5pwd.so*
