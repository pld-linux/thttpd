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
Patch0:		%{name}-includes.patch
Copyright:	distributable (BSD)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Thttpd is a very compact no-frills httpd serving daemon that can
handle very high loads. While lacking many of the advanced features of
Apachee, thttpd operates without forking and is extremely efficient in
memory use. Basic support for cgi scripts, authentication, and ssi is
provided for. Advanced features include the ability to throttle
traffic.

%prep
%setup -q
%patch0 -p1

%configure

%build
%{__make} \
	WEBDIR=/home/httpd/html \
	BINDIR=%{_sbindir} prefix=%{_prefix} \
	CGIBINDIR=/home/httpd/cgi-bin \
	MANDIR=%{_mandir}

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

gzip -9nf README TODO

%pre

grep '^httpd:' /etc/passwd >/dev/null || \
	/usr/sbin/useradd -r httpd

grep '^httpd:' /etc/group >/dev/null || \
	/usr/sbin/groupadd -r httpd

%post
/sbin/chkconfig --add thttpd

%preun
/sbin/chkconfig --del thttpd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.gz TODO.gz
%attr(2755, http, http) %{_sbindir}/makeweb
%attr(755,root,root) %{_sbindir}/htpasswd
%attr(755,root,root) %{_sbindir}/syslogtocern
%attr(755,root,root) %{_sbindir}/thttpd
%attr(-, http, http) /home/httpd
%attr(0755, root, root) /etc/rc.d/init.d/thttpd
%config %{_sysconfdir}/thttpd.conf
%doc %{_mandir}/man*/*
