%define	module	kronolith
%define	name	horde-%{module}
%define version 2.2
%define release %mkrel 2

%define _requires_exceptions pear(Horde.*)

Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
Summary:	The Horde calendar application
License:	LGPL
Group:		System/Servers
Source0:	ftp://ftp.horde.org/pub/%{module}/%{module}-h3-%{version}.tar.bz2
URL:		http://www.horde.org/%{module}
Requires(post):	rpm-helper
Requires:	horde-imp >= 4.0
Requires:	php-mcal
Requires:	php-pear-Date
Requires:	php-pear-HTML_Common
Requires:	php-pear-HTML_Select
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
Kronolith is the Horde calendar application. It provides a stable and
featureful individual calendar system for every Horde user, and
collaboration/scheduling features are starting to take shape. It makes
extensive use of the Horde Framework to provide integration with other
applications.

%prep
%setup -q -n %{module}-h3-%{version}

%build

%install
rm -rf %{buildroot}

# horde configuration
install -d -m 755 %{buildroot}%{_sysconfdir}/horde/registry.d
cat > %{buildroot}%{_sysconfdir}/horde/registry.d/%{module}.php <<'EOF'
<?php
//
// Kronolith Horde configuration file
//
 
$this->applications['kronolith'] = array(
    'fileroot'    => $this->applications['horde']['fileroot'] . '/kronolith',
    'webroot'     => $this->applications['horde']['webroot'] . '/kronolith',
    'name'        => _("Calendar"),
    'status'      => 'active',
    'provides'    => 'calendar',
    'menu_parent' => 'organizing'
);

$this->applications['kronolith-menu'] = array(
    'status'      => 'block',
    'app'         => 'kronolith',
    'blockname'   => 'tree_menu',
    'menu_parent' => 'kronolith',
);
EOF

# remove .htaccess files
find . -name .htaccess -exec rm -f {} \;

# install files
install -d -m 755 %{buildroot}%{_var}/www/horde/%{module}
install -d -m 755 %{buildroot}%{_datadir}/horde/%{module}
install -d -m 755 %{buildroot}%{_sysconfdir}/horde
cp -pR *.php %{buildroot}%{_var}/www/horde/%{module}
cp -pR themes %{buildroot}%{_var}/www/horde/%{module}
cp -pR lib %{buildroot}%{_datadir}/horde/%{module}
cp -pR locale %{buildroot}%{_datadir}/horde/%{module}
cp -pR scripts %{buildroot}%{_datadir}/horde/%{module}
cp -pR templates %{buildroot}%{_datadir}/horde/%{module}
cp -pR config %{buildroot}%{_sysconfdir}/horde/%{module}

# use symlinks to recreate original structure
pushd %{buildroot}%{_var}/www/horde/%{module}
ln -s ../../../..%{_sysconfdir}/horde/%{module} config
ln -s ../../../..%{_datadir}/horde/%{module}/lib .
ln -s ../../../..%{_datadir}/horde/%{module}/locale .
ln -s ../../../..%{_datadir}/horde/%{module}/templates .
popd
pushd %{buildroot}%{_datadir}/horde/%{module}
ln -s ../../../..%{_sysconfdir}/horde/%{module} config
popd

# activate configuration files
for file in %{buildroot}%{_sysconfdir}/horde/%{module}/*.dist; do
	mv $file ${file%.dist}
done

# fix script shellbang
for file in `find %{buildroot}%{_datadir}/horde/%{module}/scripts`; do
	perl -pi -e 's|/usr/local/bin/php|/usr/bin/php|' $file
done

%clean
rm -rf %{buildroot}

%post
if [ $1 = 1 ]; then
	# calendar access
	mcalpass=`perl -le'print map { (a..z,A..Z,0..9)[rand 62] } 0..pop' 12`
	htpasswd -b /etc/mpasswd kronolith "$mcalpass"
	perl -pi -e 's|\*\*\*\*|'$mcalpass'|' %{_sysconfdir}/horde/%{module}/conf.xml

	# configuration
	%create_ghostfile %{_sysconfdir}/horde/%{module}/conf.php apache apache 644
	%create_ghostfile %{_sysconfdir}/horde/%{module}/conf.php.bak apache apache 644

fi

%postun
if [ $1 = 0 ]; then
	htpasswd -bD /etc/mpasswd kronolith ""
fi

%files
%defattr(-,root,root)
%doc README COPYING docs
%config(noreplace) %{_sysconfdir}/horde/registry.d/%{module}.php
%config(noreplace) %{_sysconfdir}/horde/%{module}
%{_datadir}/horde/%{module}
%{_var}/www/horde/%{module}


