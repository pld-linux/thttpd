
# Conditional build:
# _with_php - with PHP library

%define		php_version	4.0.6

Summary:	Throttleable lightweight httpd server
Summary(pl):	Niedu�y serwer httpd do du�ych obci��e�
Name:		thttpd
Version:	2.20c
Release:	4
Group:		Networking
License:	BSD
Source0:	http://www.acme.com/software/thttpd/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-config.h
Patch0:		%{name}-includes.patch
%if %{?_with_php:1}%{!?_with_php:0}
Source4:	http://www.php.net/distributions/php-%{php_version}.tar.gz
Patch1:		%{name}-php.patch
Patch2:		php-mysql-socket.patch
Patch3:		php-mail.patch
Patch4:		php-link-libs.patch
Patch5:		php-session-path.patch
Patch6:		php-am_ac_lt.patch
Patch7:		php-shared.patch
Patch8:		php-pldlogo.patch
Patch9:		php-ac250.patch
Patch10:	php-pearinstall.patch
Patch11:	%{name}-remove-php-patch.patch
%endif
URL:		http://www.acme.com/software/thttpd/
%if %{?_with_php:1}%{!?_with_php:0}
BuildRequires:	autoconf >= 1.4
BuildRequires:	automake >= 1.4d
BuildRequires:	bzip2-devel
BuildRequires:	db3-devel
BuildRequires:	gd-devel
BuildRequires:	libtool >= 1.4
BuildRequires:	mysql-devel
%endif
Provides:	httpd
Provides:	webserver
PreReq:		rc-scripts
Requires(pre):	sh-utils
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         extensionsdir	%{_libdir}/php

%description
Thttpd is a very compact no-frills httpd serving daemon that can
handle very high loads. While lacking many of the advanced features of
Apache, thttpd operates without forking and is extremely efficient in
memory use. Basic support for cgi scripts, authentication, and ssi is
provided for. Advanced features include the ability to throttle
traffic.

%description -l pl
Thttpd jest kompaktowym serwerem http zdolnym obs�ugiwa� bardzo
wysokie obci��enia. Mimo i� brakuje mu wielu zaawansowanych mo�liwo�ci
z Apache to jednak jest niezwykle wydajny je�li chodzi o
wykorzystywanie pami�ci. Podstawowe wsparcie dla skrypt�w cgi,
autentyfikacji oraz ssi jest do��czone.

%prep
%setup -q
%patch0 -p1

%if %{?_with_php:1}%{!?_with_php:0}
%patch1 -p1
tar xzf %{SOURCE4}
cd php-%{php_version}
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
#%patch10 -p1
cp -f %{SOURCE3} ../config.h
%endif

%build
CFLAGS="%{rpmcflags}"; export CFLAGS
%if %{?_with_php:1}%{!?_with_php:0}
cd php-%{php_version}
EXTENSION_DIR="%{extensionsdir}"; export EXTENSION_DIR
./buildconf
%{__libtoolize}
%{__aclocal}
%{__autoconf}

%configure \
	--with-thttpd=.. \
	--disable-debug \
	--enable-bcmath \
	--enable-calendar \
	--enable-ctype \
	--enable-ftp \
	--enable-magic-quotes \
	--enable-shared \
	--enable-track-vars \
	--enable-safe-mode \
	--enable-trans-sid \
	--enable-sysvsem \
	--enable-sysvshm \
	--enable-shmop \
	--enable-session \
	--enable-exif \
	--with-db3 \
	--with-regex=php \
	--with-gettext \
	--without-mysql \
	--with-zlib \
	--with-gd \
	--with-bz2 \
	--with-mysql=/usr \
	--with-mysql-sock=/var/lib/mysql/mysql.sock
#	--with-pear=%{peardir} \

%{__make}
# this install adds special options to thttpd Makefile.in
%{__make} DESTDIR=$RPM_BUILD_ROOT install
cd ..
%endif
# unfortunately this configure _must_ be here
%configure2_13
%{__make} \
	WEBDIR=/home/httpd/html \
	BINDIR=%{_sbindir} \
	prefix=%{_prefix} \
	CGIBINDIR=/home/httpd/cgi-bin \
	MANDIR=%{_mandir} \
	WEBGROUP=http

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/home/httpd/cgi-bin,/etc/rc.d/init.d} \
	$RPM_BUILD_ROOT{%{_mandir}/man{1,8},%{_sbindir}}

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

%if %{?_with_php:1}%{!?_with_php:0}
cd php-%{php_version}
%{__make} DESTDIR=$RPM_BUILD_ROOT install
cd ..
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid http`" ]; then
	if [ "`getgid http`" != "51" ]; then
		echo "Error: group http doesn't have gid=51. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 51 -r -f http
fi
if [ -n "`id -u http 2>/dev/null`" ]; then
	if [ "`id -u http`" != "51" ]; then
		echo "Error: user http doesn't have uid=51. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 51 -r -d /home/httpd -s /bin/false -c "HTTP User" -g http http 1>&2
fi

%post
/sbin/chkconfig --add %{name}
if [ -f /var/lock/subsys/thttpd ]; then
	/etc/rc.d/init.d/thttpd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/thttpd start\" to start %{name} daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/thttpd ]; then
		/etc/rc.d/init.d/thttpd stop 1>&2
	fi
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
        /usr/sbin/userdel http
        /usr/sbin/groupdel http
fi

%files
%defattr(644,root,root,755)
%doc README TODO
%if %{?_with_php:1}%{!?_with_php:0}
%doc php-%{php_version}/{LICENSE,NEWS}
%endif
%attr(2755,http,http) %{_sbindir}/makeweb
%attr(755,root,root) %{_sbindir}/htpasswd
%attr(755,root,root) %{_sbindir}/syslogtocern
%attr(755,root,root) %{_sbindir}/thttpd
%attr(-, http, http) /home/httpd
%attr(754,root,root) /etc/rc.d/init.d/thttpd
%config %{_sysconfdir}/thttpd.conf
%{_mandir}/man*/*
