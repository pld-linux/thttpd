Summary:	Throttleable lightweight httpd server
Name:		thttpd
Version:	2.20b
Release:	1
Group:		Networking
Group(de):	Netzwerkwesen
Group(pl):	Sieciowe
URL:		http://www.acme.com/software/thttpd
Source0:	http://www.acme.com/software/thttpd/%{name}-%{version}.tar.gz
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

./configure --prefix=/usr

%build
%{__make} \
	WEBDIR=/home/httpd/html \
BINDIR=%{_sbindir} prefix=%{_prefix} \
	CGIBINDIR=/home/httpd/cgi-bin

%install

rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/home/httpd/{cgi-bin,logs}
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT%{_prefix}/man/man{1,8}
install -d $RPM_BUILD_ROOT%{_sbindir}
install  contrib/redhat-rpm/thttpd.init $RPM_BUILD_ROOT/etc/rc.d/init.d/thttpd
install contrib/redhat-rpm/thttpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/
%{__make} -i prefix=$RPM_BUILD_ROOT%{_prefix} install

%pre

grep '^httpd:' /etc/passwd >/dev/null || \
	/usr/sbin/adduser -r httpd

%post
/sbin/chkconfig --add thttpd

%preun
/sbin/chkconfig --del thttpd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc [A-Z]*
%attr(2755, httpd, httpd) %{_sbindir}/makeweb
%attr(755,root,root) %{_sbindir}/htpasswd
%attr(755,root,root) %{_sbindir}/syslogtocern
%attr(755,root,root) %{_sbindir}/thttpd
%attr(-, httpd, httpd) /home/httpd
%attr(0755, root, root) /etc/rc.d/init.d/thttpd
%config %{_sysconfdir}/thttpd.conf
%doc %{_prefix}/man/man*/*
