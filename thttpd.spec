#
# Conditional build:
%bcond_with php		# with PHP library
#
%define		php_version	4.0.6

Summary:	Throttleable lightweight HTTP server
Summary(pl):	Niedu¿y serwer HTTP do du¿ych obci±¿eñ
Name:		thttpd
Version:	2.25b
Release:	4.2
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
BuildRequires:	rpmbuild(macros) >= 1.159
PreReq:		rc-scripts
Requires(pre):	sh-utils
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	htpasswd
Provides:	group(thttp)
Provides:	httpd
Provides:	user(thttp)
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		extensionsdir	%{_libdir}/php

%description
Thttpd is a very compact no-frills HTTP serving daemon that can
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

%package -n htpasswd-%{name}
Summary:	thttpd htpasswd utility
Summary(pl):	Narzêdzie htpasswd z thttpd
Group:		Networking/Utilities
Provides:	htpasswd
Obsoletes:	htpasswd

%description -n htpasswd-%{name}
htpasswd is used to create and update the flat-files used to store
usernames and password for basic authentication of HTTP users. This
package contains htpasswd from thttpd; it supports only CRYPT
encryption algorithm.

%description -n htpasswd-%{name} -l pl
htpasswd s³u¿y do tworzenia i uaktualniania p³askich plików s³u¿±cych
do przechowywania nazw u¿ytkowników i hase³ do uwierzytelnienia basic
u¿ytkowników HTTP. Ten pakiet zawiera htpasswd z thttpd; ta wersja
obs³uguje wy³±cznie has³a zaszyfrowane przez CRYPT.

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
if [ -n "`/usr/bin/getgid thttp`" ]; then
	if [ "`/usr/bin/getgid thttp`" != "131" ]; then
		echo "Error: group thttp doesn't have gid=131. Correct this before installing %{name}." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 131 -r -f thttp
fi
if [ -n "`/bin/id -u thttp 2>/dev/null`" ]; then
	if [ "`/bin/id -u thttp`" != "117" ]; then
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
