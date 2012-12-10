%define	module	kronolith
%define	name	horde-%{module}
%define version 2.3.5
%define release %mkrel 2

%define _requires_exceptions pear(Horde.*)

Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
Summary:	The Horde calendar application
License:	LGPL
Group:		System/Servers
URL:		http://www.horde.org/%{module}
Source0:	ftp://ftp.horde.org/pub/%{module}/%{module}-h3-%{version}.tar.gz
Requires(post):	rpm-helper
Requires:	horde >= 3.3.5
Requires:	horde-imp >= 4.0
Requires:	php-mcal
Requires:	php-pear-Date
Suggests:	php-pear-Date_Holidays
Suggests:	php-pear-XML_Serializer
BuildArch:	noarch

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

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
# %{name} Apache configuration file

<Directory %{_datadir}/horde/%{module}/lib>
    Order allow,deny
    Deny from all
</Directory>

<Directory %{_datadir}/horde/%{module}/locale>
    Order allow,deny
    Deny from all
</Directory>

<Directory %{_datadir}/horde/%{module}/scripts>
    Order allow,deny
    Deny from all
</Directory>

<Directory %{_datadir}/horde/%{module}/templates>
    Order allow,deny
    Deny from all
</Directory>
EOF

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
install -d -m 755 %{buildroot}%{_datadir}/horde/%{module}
cp -pR *.php %{buildroot}%{_datadir}/horde/%{module}
cp -pR themes %{buildroot}%{_datadir}/horde/%{module}
cp -pR js %{buildroot}%{_datadir}/horde/%{module}
cp -pR calendars %{buildroot}%{_datadir}/horde/%{module}
cp -pR lib %{buildroot}%{_datadir}/horde/%{module}
cp -pR locale %{buildroot}%{_datadir}/horde/%{module}
cp -pR scripts %{buildroot}%{_datadir}/horde/%{module}
cp -pR templates %{buildroot}%{_datadir}/horde/%{module}
cp -pR config %{buildroot}%{_sysconfdir}/horde/%{module}

install -d -m 755 %{buildroot}%{_sysconfdir}/horde
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
%if %mdkversion < 201010
%_post_webapp
%endif

%postun
if [ $1 = 0 ]; then
	htpasswd -bD /etc/mpasswd kronolith ""
fi
%if %mdkversion < 201010
%_postun_webapp
%endif

%files
%defattr(-,root,root)
%doc README COPYING docs
%config(noreplace) %{_webappconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/horde/registry.d/%{module}.php
%config(noreplace) %{_sysconfdir}/horde/%{module}
%{_datadir}/horde/%{module}


%changelog
* Wed Mar 30 2011 Adam Williamson <awilliamson@mandriva.org> 2.3.5-2mdv2011.0
+ Revision: 648819
- add some newer optional deps
- drop a couple of now obsolete pear deps
- new release 2.3.5

* Sun Aug 08 2010 Thomas Spuhler <tspuhler@mandriva.org> 2.3.4-1mdv2011.0
+ Revision: 567502
- Updated to version 2.3.4
- added version 2.3.4 source file

* Sun Aug 01 2010 Thomas Spuhler <tspuhler@mandriva.org> 2.3.2-4mdv2011.0
+ Revision: 564167
- Increased release for rebuild

* Mon Jan 18 2010 Guillaume Rousse <guillomovitch@mandriva.org> 2.3.2-3mdv2010.1
+ Revision: 493348
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise
- restrict default access permissions to localhost only, as per new policy

* Sun Sep 20 2009 Guillaume Rousse <guillomovitch@mandriva.org> 2.3.2-1mdv2010.0
+ Revision: 445929
- new version
- new setup (simpler is better)

* Fri Sep 11 2009 Thierry Vignaud <tv@mandriva.org> 2.3-2mdv2010.0
+ Revision: 437883
- rebuild

* Sun Oct 19 2008 Guillaume Rousse <guillomovitch@mandriva.org> 2.3-1mdv2009.1
+ Revision: 295282
- update to new version 2.3

* Tue Jun 17 2008 Guillaume Rousse <guillomovitch@mandriva.org> 2.2-3mdv2009.0
+ Revision: 223438
- add missing js and calendars directories (fix #41510)

* Fri May 30 2008 Guillaume Rousse <guillomovitch@mandriva.org> 2.2-2mdv2009.0
+ Revision: 213372
- don't duplicate spec-helper work

* Fri May 30 2008 Guillaume Rousse <guillomovitch@mandriva.org> 2.2-1mdv2009.0
+ Revision: 213371
- update to new version 2.2

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Wed Dec 19 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.1.6-1mdv2008.1
+ Revision: 133769
- update to new version 2.1.6

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Mon Dec 18 2006 Guillaume Rousse <guillomovitch@mandriva.org> 2.1.4-1mdv2007.0
+ Revision: 98407
- new version
- protect registry file from shell expansion

  + Andreas Hasenack <andreas@mandriva.com>
    - Import horde-kronolith

* Tue Jun 27 2006 Guillaume Rousse <guillomovitch@mandriva.org> 2.1.2-1mdv2007.0
- New version 2.1.2
- use herein document for horde configuration

* Tue Mar 07 2006 Guillaume Rousse <guillomovitch@mandriva.org> 2.1-1mdk
- new version
- drop patch

* Wed Jan 11 2006 Guillaume Rousse <guillomovitch@mandriva.org> 2.0.6-2mdk
- fix automatic dependencies

* Tue Dec 27 2005 Guillaume Rousse <guillomovitch@mandriva.org> 2.0.6-1mdk
- New release 2.0.6
- %%mkrel

* Thu Jun 30 2005 Guillaume Rousse <guillomovitch@mandriva.org> 2.0.3-1mdk 
- new version
- better fix encoding
- fix requires

* Sun Apr 17 2005 Guillaume Rousse <guillomovitch@mandrake.org> 2.0.2-1mdk
- New release 2.0.2

* Fri Feb 18 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.1-5mdk
- spec file cleanups, remove the ADVX-build stuff
- strip away annoying ^M

* Thu Jan 27 2005 Guillaume Rousse <guillomovitch@mandrake.org> 2.0.1-4mdk 
- no automatic config generation, incorrect default values
- horde isn't a prereq
- spec cleanup

* Mon Jan 17 2005 Guillaume Rousse <guillomovitch@mandrake.org> 2.0.1-3mdk 
- fix inclusion path
- fix configuration perms
- generate configuration at postinstall
- horde and rpm-helper are now a prereq
- only manage calendar access for installation and deinstallation, not upgrade

* Sat Jan 15 2005 Guillaume Rousse <guillomovitch@mandrake.org> 2.0.1-2mdk 
- fix symlink
- fix scripts shellbang

* Fri Jan 14 2005 Guillaume Rousse <guillomovitch@mandrake.org> 2.0.1-1mdk 
- new version
- top-level is now /var/www/horde/kronolith
- config is now in /etc/horde/kronolith
- other non-accessible files are now in /usr/share/horde/kronolith
- drop old obsoletes
- rediff patch0
- no more apache configuration
- rpmbuildupdate aware
- spec cleanup

* Mon Jul 19 2004 Guillaume Rousse <guillomovitch@mandrake.org> 1.1.2-3mdk 
- apache config file in /etc/httpd/webapps.d

* Sun May 02 2004 Guillaume Rousse <guillomovitch@mandrake.org> 1.1.2-2mdk
- renamed to horde-kronolith
- pluggable horde configuration
- standard perms for /etc/httpd/conf.d/%%{order}_horde-kronolith.conf
- don't provide useless ADVXpackage virtual package

* Tue Apr 06 2004 Guillaume Rousse <guillomovitch@mandrake.org> 1.1.2-1mdk
- new version
- dropped patch 1 (no more useful)

* Sun Feb 15 2004 Pascal Terjan <pterjan@mandrake.org> 1.1-10mdk
- require imp not only in changelog...

* Sun Feb 15 2004 Pascal Terjan <pterjan@mandrake.org> 1.1-9mdk
- Requires imp
- fix bad redirect after login (Patch1)

* Sun Feb 15 2004 Pascal Terjan <pterjan@mandrake.org> 1.1-8mdk
- oops remove useless Requires

* Sun Feb 15 2004 Pascal Terjan <pterjan@mandrake.org> 1.1-7mdk
- make kronolith work out-of-the-box using mcal

* Sun Dec 28 2003 Pascal Terjan <pterjan@mandrake.org> 1.1-6mdk
- requires php-pear-HTML_Common and php-pear-HTML_Select

* Sun Dec 28 2003 Pascal Terjan <pterjan@mandrake.org> 1.1-5mdk
- requires php-pear-Date

* Sat Dec 20 2003 Guillaume Rousse <guillomovitch@mandrake.org> 1.1-4mdk
- untagged localisation files
- no more .htaccess files, use /etc/httpd/conf.d/%%{order}_kronolith.conf instead
- scripts now in  /usr/share/{name}

