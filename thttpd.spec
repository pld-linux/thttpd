Summary:	Throttleable lightweight httpd server
Name:		thttpd
Version:	2.20b
Release:	1
Group:		Networking
Group(de):	Netzwerkwesen
Group(pl):	Sieciowe
URL:		http://www.acme.com/software/thttpd
Source0:	http://www.acme.com/software/thttpd/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-config.h
Source4:	php-4.0.4pl1.tar.gz
Patch0:		%{name}-includes.patch
Patch1:		php-DESTDIR.patch
Copyright:	distributable (BSD)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Thttpd is a very compact no-frills httpd serving daemon that can
handle very high loads. While lacking many of the advanced features of
Apache, thttpd operates without forking and is extremely efficient in
memory use. Basic support for cgi scripts, authentication, and ssi is
provided for. Advanced features include the ability to throttle
traffic.

%description -l pl
Thttpd jest kompaktowym serwerem http zdolnym obs³ugiwaæ bardzo
wysokie obci±¿enia. Mimo i¿ brakuje mu wielu zaawansowanych
mo¿liwo¶ci z Apache to jednak jest niezwykle wydajny je¶li
chodzi o wykorzystywanie pamiêci. Podstawowe wsparcie dla skryptów
cgi, autentyfikacji oraz ssi jest do³±czone.

%prep
%setup -q -a4
%patch0 -p1
cd php-4.0.4pl1
%patch1 -p1
cp -f %{SOURCE3} ../config.h

%configure \
	--with-thttpd=.. \
	--enable-bcmath \
	--with-bz2 \
	--enable-calendar \
	--enable-ctype \
	--with-db3 \
	--enable-ftp \
	--with-gd
	
cd ..
%configure

%build
cd php-*
%{__make}
cd ..
%{__make} \
	WEBDIR=/home/httpd/html \
	BINDIR=%{_sbindir} \
	prefix=%{_prefix} \
	CGIBINDIR=/home/httpd/cgi-bin \
	MANDIR=%{_mandir} \
	WEBGROUP=http

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/home/httpd/cgi-bin
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT%{_mandir}/man{1,8}
install -d $RPM_BUILD_ROOT%{_sbindir}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/thttpd
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/
install thttpd $RPM_BUILD_ROOT/%{_sbindir}
install extras/{htpasswd,makeweb,syslogtocern} $RPM_BUILD_ROOT/%{_sbindir}
install cgi-bin/printenv $RPM_BUILD_ROOT/home/httpd/cgi-bin/
install cgi-src/{phf,redirect,ssi} $RPM_BUILD_ROOT/home/httpd/cgi-bin/
install cgi-src/{redirect.8,ssi.8} $RPM_BUILD_ROOT/%{_mandir}/man8/
install extras/{htpasswd.1,makeweb.1} $RPM_BUILD_ROOT/%{_mandir}/man1/
install extras/syslogtocern.8 $RPM_BUILD_ROOT/%{_mandir}/man8/
install thttpd.8 $RPM_BUILD_ROOT/%{_mandir}/man8/

cd php-4.0.4pl1
%{__make} DESTDIR=$RPM_BUILD_ROOT install

gzip -9nf ../README ../TODO LICENSE NEWS

%pre
grep '^http:' /etc/passwd >/dev/null || \
	/usr/sbin/useradd -r http

grep '^http:' /etc/group >/dev/null || \
	/usr/sbin/groupadd -r http

%post
/sbin/chkconfig --add thttpd

%preun
/sbin/chkconfig --del thttpd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.gz TODO.gz LICENSE.gz NEWS.gz
%attr(2755, http, http) %{_sbindir}/makeweb
%attr(755,root,root) %{_sbindir}/htpasswd
%attr(755,root,root) %{_sbindir}/syslogtocern
%attr(755,root,root) %{_sbindir}/thttpd
%attr(-, http, http) /home/httpd
%attr(0755, root, root) /etc/rc.d/init.d/thttpd
%config %{_sysconfdir}/thttpd.conf
%doc %{_mandir}/man*/*
