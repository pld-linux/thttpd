
# Conditional build:
# _with_php - without PHP library

%define php_version 4.1.0

Summary:	Throttleable lightweight httpd server
Summary(pl):	Niedu¿y serwer httpd do du¿ych obci±¿eñ
Name:		thttpd
Version:	2.20c
Release:	2
Group:		Networking
Group(de):	Netzwerkwesen
Group(es):	Red
Group(pl):	Sieciowe
Group(pt_BR):	Rede
License:	BSD
Source0:	http://www.acme.com/software/thttpd/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}-config.h
Patch0:		%{name}-includes.patch
%if %{?_with_php:1}%{!?_with_php:0}
Source4:	http://www.php.net/distributions/php-%{php_version}.tar.gz
Patch1:		php-mysql-socket.patch
Patch2:		php-mail.patch
Patch3:		php-link-libs.patch
Patch4:		php-session-path.patch
Patch5:		php-am_ac_lt.patch
Patch6:		php-shared.patch
Patch7:		php-pldlogo.patch
Patch8:		php-ac250.patch
Patch9:		php-dbplus.patch
BuildRequires: gd-devel
BuildRequires: db3-devel
BuildRequires:  autoconf >= 1.4
BuildRequires:  automake >= 1.4d
BuildRequires:  libtool >= 1.4
BuildRequires: bzip2-devel
BuildRequires: mysql-devel
%endif
Provides:       httpd
Provides:       webserver
Prereq:         /sbin/chkconfig
Prereq:         /usr/sbin/useradd
Prereq:         /usr/bin/getgid
Prereq:         /bin/id
Prereq:         sh-utils
Prereq:         rc-scripts
URL:		http://www.acme.com/software/thttpd/
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
wysokie obci±¿enia. Mimo i¿ brakuje mu wielu zaawansowanych mo¿liwo¶ci
z Apache to jednak jest niezwykle wydajny je¶li chodzi o
wykorzystywanie pamiêci. Podstawowe wsparcie dla skryptów cgi,
autentyfikacji oraz ssi jest do³±czone.

%prep
%setup -q %{?_with_php:-a4}
%patch0 -p1

%if %{?_with_php:1}%{!?_with_php:0}
cd php-%{php_version}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
cp -f %{SOURCE3} ../config.h
%endif

%build
CFLAGS="%{rpmcflags}"; export CFLAGS
%if %{?_with_php:1}%{!?_with_php:0}
./buildconf
libtoolize --copy --force
aclocal
autoconf

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
	--with-gd
	--with-bz2 \
	--with-mysql=/usr \
	--with-mysql-sock=/var/lib/mysql/mysql.sock
	
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

%if %{?_with_php:1}%{!?_with_php:0}
cd php-%{php_version}
%{__make} DESTDIR=$RPM_BUILD_ROOT install
gzip -9nf LICENSE NEWS
cd ..
%endif

gzip -9nf README TODO 

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid http`" ]; then
        if [ "`getgid http`" != "51" ]; then
                echo "Warning: group http haven't gid=51. Correct this before install %{name}" 1>&2
                exit 1
        fi
else
        /usr/sbin/groupadd -g 51 -r -f http
fi
if [ -n "`id -u http 2>/dev/null`" ]; then
        if [ "`id -u http`" != "51" ]; then
                echo "Warning: user http haven't uid=51. Correct this before install %{name}" 1>&2
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
fi
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
        /usr/sbin/userdel http
        /usr/sbin/groupdel http
fi

%files
%defattr(644,root,root,755)
%doc *.gz 
%if %{?_with_php:1}%{!?_with_php:0}
%doc php-%{php_version}/*.gz
%endif
%attr(2755, http, http) %{_sbindir}/makeweb
%attr(755,root,root) %{_sbindir}/htpasswd
%attr(755,root,root) %{_sbindir}/syslogtocern
%attr(755,root,root) %{_sbindir}/thttpd
%attr(-, http, http) /home/httpd
%attr(0755, root, root) /etc/rc.d/init.d/thttpd
%config %{_sysconfdir}/thttpd.conf
%doc %{_mandir}/man*/*
