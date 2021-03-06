Name:           cloud-init
Version:        0.7.5
Release:        4.4
License:        GPL-3.0
Summary:        Cloud node initialization tool
Url:            http://launchpad.net/cloud-init/
Group:          System/Management
Source0:        %{name}-%{version}.tar.gz
BuildRequires:  fdupes
BuildRequires:  python-devel
BuildRequires:  python-setuptools
Requires:       bash
Requires:       python-argparse
Requires:       python-boto >= 2.7
Requires:       python-cheetah
Requires:       python-configobj
Requires:       python-jsonpatch
Requires:       python-oauth
Requires:       python-prettytable
Requires:       python-pyserial
Requires:       python-PyYAML
Requires:       python-requests
Requires:       python-setuptools
Requires:       python-xml
Requires:       python-yaml
Requires:       python-six
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%define         docdir %{_defaultdocdir}/%{name}

%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define initsys aix

%description
Cloud-init is an init script that initializes a cloud node (VM)
according to the fetched configuration data from the admin node.

The RPM packages can be obtained from the following website:
ftp://ftp.software.ibm.com/aix/freeSoftware/aixtoolbox/RPMS/ppc/

The package dependencies listed in install order are:
    python-devel-2.7.6-1.aix6.1.ppc.rpm
    python-xml-0.8.4-1.aix6.1.ppc.rpm
    python-boto-2.34.0-1.aix6.1.noarch.rpm
    python-argparse-1.2.1-1.aix6.1.noarch.rpm
    python-cheetah-2.4.4-2.aix6.1.ppc.rpm
    python-configobj-5.0.5-1.aix6.1.noarch.rpm
    python-jsonpointer-1.0.c1ec3df-1.aix6.1.noarch.rpm
    python-jsonpatch-1.8-1.aix6.1.noarch.rpm
    python-oath-1.0.1-1.aix6.1.noarch.rpm
    python-pyserial-2.7-1.aix6.1.ppc.rpm
    python-prettytable-0.7.2-1.aix6.1.noarch.rpm
    python-requests-2.4.3-1.aix6.1.noarch.rpm
    libyaml-0.1.4-1.aix6.1.ppc.rpm
    python-PyYAML-3.11-2.aix6.1.ppc.rpm
    python-six-1.3.0-1.aix6.1.noarch.rpm
    python-setuptools-0.9.8-2.aix6.1.noarch.rpm

%package doc
Summary:        Cloud node initialization tool - Documentation
Group:          System/Management

%description doc
Cloud-init is an init script that initializes a cloud node (VM)
according to the fetched configuration data from the admin node.

Documentation and examples for cloud-init tools

%package test
Summary:        Cloud node initialization tool  - Testsuite
Group:          System/Management
Requires:       cloud-init = %{version}

%description test
Cloud-init is an init script that initializes a cloud node (VM)
according to the fetched configuration data from the admin node.

Unit tests for the cloud-init tools

%prep
%setup -q


%build
python setup.py build

%install
python setup.py install --root=%{buildroot} --prefix=%{_prefix} --install-lib=%{python_sitelib} --init-system=%{initsys}

find %{buildroot} -name ".gitignore" -type f -exec rm -f {} \;
find %{buildroot} -name ".placeholder" -type f -exec rm -f {} \;

# from debian install script
for x in "%{buildroot}%{_bindir}/"*.py; do
   [ -f "${x}" ] && mv "${x}" "${x%.py}"
done
/usr/bin/mkdir -p %{buildroot}%{_localstatedir}/lib/cloud

# move documentation
/usr/bin/mkdir -p %{buildroot}%{_defaultdocdir}
%define aixshare usr/share

rm -rf %{buildroot}%{docdir}
mv -f %{buildroot}/%{aixshare}/doc/%{name} %{buildroot}%{docdir}
/usr/bin/mkdir -p %{buildroot}/%{_sysconfdir}/cloud/

/usr/bin/mkdir -p %{buildroot}/%_prefix/%_lib
cp -r %{buildroot}/usr/lib/cloud-init %{buildroot}/%_prefix/%_lib

# copy the LICENSE
cp LICENSE %{buildroot}%{docdir}


# remove debian/ubuntu specific profile.d file (bnc#779553)
rm -f %{buildroot}%{_sysconfdir}/profile.d/Z99-cloud-locale-test.sh

# Remove non-AIX templates
rm -f %{buildroot}/etc/cloud/templates/*.debian.*
rm -f %{buildroot}/etc/cloud/templates/*.redhat.*
rm -f %{buildroot}/etc/cloud/templates/*.ubuntu.*
rm -f %{buildroot}/etc/cloud/templates/*.suse.*


# Move everything from %{buildroot}/etc/cloud to %{buildroot}/%{_prefix}/etc/cloud
# so we can build it as a package and installed to /opt/freeware
rm -rf %{buildroot}/%{_prefix}/etc/cloud/*
mv -f %{buildroot}/etc/cloud/* %{buildroot}/%{_prefix}/etc/cloud

# move aix sysvinit scripts into the "right" place
%define _initddir /etc/rc.d/init.d
/usr/bin/mkdir -p %{buildroot}/%{_initddir}
/usr/bin/mkdir -p %{buildroot}/%{_sbindir}
OLDPATH="%{buildroot}%{_initddir}"
for iniF in *; do
    ln -sf "%{_initddir}/${iniF}" "%{buildroot}/%{_sbindir}/rc${iniF}"
done
cd $OLDPATH

# remove duplicate files
/opt/freeware/bin/fdupes %{buildroot}%{python_sitelib}

%post
/usr/bin/ln -sf /etc/rc.d/init.d/cloud-init-local /etc/rc.d/rc2.d/S01cloud-init-local
/usr/bin/ln -sf /etc/rc.d/init.d/cloud-init       /etc/rc.d/rc2.d/S02cloud-init
/usr/bin/ln -sf /etc/rc.d/init.d/cloud-config     /etc/rc.d/rc2.d/S03cloud-config
/usr/bin/ln -sf /etc/rc.d/init.d/cloud-final      /etc/rc.d/rc2.d/S04cloud-final
if [[ `/usr/sbin/lsattr -El sys0 -a clouddev >/dev/null 2>&1; echo $?` -eq 0  ]]; then
	/usr/lib/boot/bootutil -c 2>/dev/null
	/usr/sbin/chdev -l sys0 -a clouddev=1 >/dev/null 2>&1
else
	/usr/sbin/chdev -l sys0 -a ghostdev=1 >/dev/null 2>&1
fi

%preun
if [ "$1" = 0 ]; then
    rm -rf /opt/freeware/var/lib/cloud/*
    rm -rf /run/cloud-init
fi

%postun
if [ "$1" = 0 ]; then
    rm /etc/rc.d/rc2.d/S01cloud-init-local
    rm /etc/rc.d/rc2.d/S02cloud-init
    rm /etc/rc.d/rc2.d/S03cloud-config
    rm /etc/rc.d/rc2.d/S04cloud-final
fi

%files
%define py_ver 2.7
%defattr(-,root,root)
# do not mark as doc or we get conflicts with the doc package
%{docdir}/LICENSE
%{_bindir}/cloud-init
%{_bindir}/cloud-init-per
%config(noreplace) %{_prefix}/etc/cloud/
%{python_sitelib}/cloudinit
%{python_sitelib}/cloud_init-%{version}-py%{py_ver}.egg-info
%{_prefix}/lib/cloud-init
%attr(0755, root, root) %{_initddir}/cloud-config
%attr(0755, root, root) %{_initddir}/cloud-init
%attr(0755, root, root) %{_initddir}/cloud-init-local
%attr(0755, root, root) %{_initddir}/cloud-final

%dir %attr(0755, root, root) %{_localstatedir}/lib/cloud
%dir %{docdir}


%files doc
%defattr(-,root,root)
%{docdir}/examples/*
%{docdir}/README
%{docdir}/*.txt
%{docdir}/*.rst
%dir %{docdir}/examples

%files test
%defattr(-,root,root)
%{python_sitelib}/tests

%changelog


