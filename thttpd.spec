#
# Conditional build:
%bcond_with php		# with PHP library
#
%define		php_version	4.0.6

Summary:	Throttleable lightweight httpd server
Summary(pl):	Niedu¿y serwer httpd do du¿ych obci±¿eñ
Name:		thttpd
Version:	2.25b
Release:	3
Group:		Networking
License:	BSD
Source0:	http://www.acme.com/software/thttpd/%{name}-%{version}.tar.gz
# Source0-md5:	a0e9cd87455d3a0ea11e5ea7e947adf6
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-config.h
Patch0:		%{name}-includes.patch
%if %{with php}
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
%if %{with php}
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

%define		extensionsdir	%{_libdir}/php

%description
Thttpd is a very compact no-frills httpd serving daemon that can
handle very high loads. While lacking many of the advanced features of
Apache, thttpd operates without forking and is extremely efficient in
memory use. Basic support for CGI scripts, authentication and SSI is
provided. Advanced features include the ability to throttle traffic.

%description -l pl
Thttpd jest kompaktowym serwerem HTTP, zdolnym obs³ugiwaæ bardzo
wysokie obci±¿enia. Mimo i¿ brakuje mu wielu zaawansowanych mo¿liwo¶ci
Apache, jest niezwykle wydajny je¶li chodzi o wykorzystywanie pamiêci.
Dostarczane jest podstawowe wsparcie dla skryptów CGI,
uwierzytelniania, oraz SSI.

%prep
%setup -q
%patch0 -p1

%if %{with php}
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
install %{_datadir}/automake/config.* .
CFLAGS="%{rpmcflags}"; export CFLAGS
%if %{with php}
cd php-%{php_version}
EXTENSION_DIR="%{extensionsdir}"; export EXTENSION_DIR
./buildconf
%{__libtoolize}
%{__aclocal}
%{__autoconf}

%configure \
	--with-thttpd=.. \
	--%{!?debug:dis}%{?debug:en}able-debug \
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
	--with-zlib \
	--with-gd \
	--with-bz2 \
	--with-mysql=%{_prefix} \
	--with-mysql-sock=/var/lib/mysql/mysql.sock
#	--with-pear=%{peardir} \

%{__make}
# this install adds special options to thttpd Makefile.in
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
cd ..
%endif
# unfortunately this configure _must_ be here
%configure2_13
%{__make} \
	CCOPT="%{rpmcflags}" \
	prefix=%{_prefix} \
	BINDIR=%{_sbindir} \
	MANDIR=%{_mandir} \
	WEBDIR=/home/services/%{name}/html \
	CGIBINDIR=/home/services/%{name}/cgi-bin \
	WEBGROUP=%{name}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/home/services/%{name}/{cgi-bin,html},%{_sbindir}} \
	$RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir},%{_mandir}/man{1,8}}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}
install thttpd $RPM_BUILD_ROOT%{_sbindir}
install extras/{htpasswd,makeweb,syslogtocern} $RPM_BUILD_ROOT%{_sbindir}
install cgi-bin/printenv $RPM_BUILD_ROOT/home/services/%{name}/cgi-bin
install cgi-src/{phf,redirect,ssi} $RPM_BUILD_ROOT/home/services/%{name}/cgi-bin
install cgi-src/{redirect.8,ssi.8} $RPM_BUILD_ROOT%{_mandir}/man8
# htpasswd.1 confilcts with apache, so temporary commented
#install extras/{htpasswd.1,makeweb.1} $RPM_BUILD_ROOT%{_mandir}/man1
install extras/makeweb.1 $RPM_BUILD_ROOT%{_mandir}/man1
install extras/syslogtocern.8 $RPM_BUILD_ROOT%{_mandir}/man8
install thttpd.8 $RPM_BUILD_ROOT%{_mandir}/man8

%if %{with php}
cd php-%{php_version}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
cd ..
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid thttp`" ]; then
	if [ "`getgid thttp`" != "131" ]; then
		echo "Error: group thttp doesn't have gid=131. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 131 -r -f thttp
fi
if [ -n "`id -u thttp 2>/dev/null`" ]; then
	if [ "`id -u thttp`" != "117" ]; then
		echo "Error: user thttp doesn't have uid=117. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 117 -r -d /home/services/%{name} -s /bin/false -c "tHTTP User" -g thttp thttp 1>&2
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
	/usr/sbin/userdel thttp
	/usr/sbin/groupdel thttp
fi

%files
%defattr(644,root,root,755)
%doc README TODO
%if %{with php}
%doc php-%{php_version}/{LICENSE,NEWS}
%endif
%attr(2755,thttp,thttp) %{_sbindir}/makeweb
%attr(755,root,root) %{_sbindir}/htpasswd
%attr(755,root,root) %{_sbindir}/syslogtocern
%attr(755,root,root) %{_sbindir}/%{name}
%attr(-,root,root) /home/services/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config %{_sysconfdir}/%{name}.conf
%{_mandir}/man*/*
