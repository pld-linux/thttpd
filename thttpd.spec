#
# Conditional build:
%bcond_with	php		# with PHP library
#
%define		php_version	4.0.6

Summary:	Throttleable lightweight HTTP server
Summary(pl.UTF-8):	Nieduży serwer HTTP do dużych obciążeń
Name:		thttpd
Version:	2.25b
Release:	8
License:	BSD
Group:		Networking/Daemons/HTTP
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
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(pre):	sh-utils
Requires:	htpasswd
Requires:	rc-scripts
Provides:	group(thttp)
Provides:	user(thttp)
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		extensionsdir	%{_libdir}/php

%description
Thttpd is a very compact no-frills HTTP serving daemon that can handle
very high loads. While lacking many of the advanced features of
Apache, thttpd operates without forking and is extremely efficient in
memory use. Basic support for CGI scripts, authentication and SSI is
provided. Advanced features include the ability to throttle traffic.

%description -l pl.UTF-8
Thttpd jest kompaktowym serwerem HTTP, zdolnym obsługiwać bardzo
wysokie obciążenia. Mimo iż brakuje mu wielu zaawansowanych możliwości
Apache, jest niezwykle wydajny jeśli chodzi o wykorzystywanie pamięci.
Dostarczane jest podstawowe wsparcie dla skryptów CGI,
uwierzytelniania, oraz SSI.

%package -n htpasswd-%{name}
Summary:	thttpd htpasswd utility
Summary(pl.UTF-8):	Narzędzie htpasswd z thttpd
Group:		Networking/Utilities
Provides:	htpasswd
Obsoletes:	htpasswd

%description -n htpasswd-%{name}
htpasswd is used to create and update the flat-files used to store
usernames and password for basic authentication of HTTP users. This
package contains htpasswd from thttpd; it supports only CRYPT
encryption algorithm.

%description -n htpasswd-%{name} -l pl.UTF-8
htpasswd służy do tworzenia i uaktualniania płaskich plików służących
do przechowywania nazw użytkowników i haseł do uwierzytelnienia basic
użytkowników HTTP. Ten pakiet zawiera htpasswd z thttpd; ta wersja
obsługuje wyłącznie hasła zaszyfrowane przez CRYPT.

%prep
%setup -q
%patch -P0 -p1

%if %{with php}
%patch -P1 -p1
tar xzf %{SOURCE4}
cd php-%{php_version}
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1
%patch -P7 -p1
%patch -P8 -p1
%patch -P9 -p1
%patch -P10 -p1
%patch -P11 -p1
#%%patch10 -p1
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
install -d $RPM_BUILD_ROOT{/home/services/%{name}/{cgi-bin,html},%{_sbindir},%{_bindir}} \
	$RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir},%{_mandir}/man{1,8}}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}
install thttpd $RPM_BUILD_ROOT%{_sbindir}
install extras/{makeweb,syslogtocern} $RPM_BUILD_ROOT%{_sbindir}
install cgi-bin/printenv $RPM_BUILD_ROOT/home/services/%{name}/cgi-bin
install cgi-src/{phf,redirect,ssi} $RPM_BUILD_ROOT/home/services/%{name}/cgi-bin
install cgi-src/{redirect.8,ssi.8} $RPM_BUILD_ROOT%{_mandir}/man8
install extras/makeweb.1 $RPM_BUILD_ROOT%{_mandir}/man1
install extras/syslogtocern.8 $RPM_BUILD_ROOT%{_mandir}/man8
install thttpd.8 $RPM_BUILD_ROOT%{_mandir}/man8

# htpasswd
install extras/htpasswd $RPM_BUILD_ROOT%{_bindir}
ln -sf %{_bindir}/htpasswd $RPM_BUILD_ROOT%{_sbindir}
install extras/htpasswd.1 $RPM_BUILD_ROOT%{_mandir}/man1

%if %{with php}
cd php-%{php_version}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
cd ..
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 131 -r -f thttp
%useradd -u 117 -r -d /home/services/%{name} -s /bin/false -c "tHTTP User" -g thttp thttp

%post
/sbin/chkconfig --add %{name}
%service thttpd restart "%{name} daemon"

%preun
if [ "$1" = "0" ]; then
	%service thttpd stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove thttp
	%groupremove thttp
fi

%files
%defattr(644,root,root,755)
%doc README TODO
%if %{with php}
%doc php-%{php_version}/{LICENSE,NEWS}
%endif
%attr(2755,thttp,thttp) %{_sbindir}/makeweb
%attr(755,root,root) %{_sbindir}/syslogtocern
%attr(755,root,root) %{_sbindir}/%{name}
%attr(-,root,root) /home/services/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%{_mandir}/man*/m*
%{_mandir}/man*/r*
%{_mandir}/man*/s*
%{_mandir}/man*/t*

%files -n htpasswd-%{name}
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/htpasswd
%{_sbindir}/htpasswd
%{_mandir}/man1/htpasswd.1*
