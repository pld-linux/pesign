# TODO: PLDify init script
Summary:	Signing tool for PE-COFF binaries
Summary(pl.UTF-8):	Narzędzie do podpisywania binariów PE-COFF
Name:		pesign
Version:	0.109
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	https://github.com/vathpela/pesign/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	5214a68896a54775a211f02667fedd7b
Patch0:		%{name}-uninitialized.patch
URL:		https://github.com/vathpela/pesign
BuildRequires:	nspr-devel
BuildRequires:	nss-devel
BuildRequires:	pkgconfig
BuildRequires:	popt-devel
BuildRequires:	rpmbuild(macros) >= 1.644
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	%{name}-libs = %{version}-%{release}
Requires:	rc-scripts
Provides:	group(pesign)
Provides:	user(pesign)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Signing tool for PE-COFF binaries, hopefully at least vaguely
compliant with the PE and Authenticode specifications.

%description -l pl.UTF-8
Narzędzie do podpisywania binariów PE-COFF, mające być przynajmniej
w jakiś sposób zgodne ze specyfikacjami PE oraz Authenticode.

%package libs
Summary:	libdpe shared library
Summary(pl.UTF-8):	Biblioteka współdzielona libdpe
Group:		Libraries

%description libs
libdpe shared library.

%description libs -l pl.UTF-8
Biblioteka współdzielona libdpe.

%package devel
Summary:	Header files for libdpe library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki libdpe
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for libdpe library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libdpe.

%package static
Summary:	Static libdpe library
Summary(pl.UTF-8):	Statyczna biblioteka libdpe
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libdpe library.

%description static -l pl.UTF-8
Statyczna biblioteka libdpe.

%prep
%setup -q
%patch0 -p1

%{__sed} -i -e 's/-g -O0/%{rpmcflags} -Wno-unused-result/' Make.defaults

%{__sed} -i -e 's,/usr/lib/systemd/system,%{systemdunitdir},' src/Makefile

%build
%{__make} \
	CC="%{__cc}" \
	LIBDIR=%{_libdir}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install install_systemd install_sysvinit \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 312 pesign
%useradd -u 312 -d /usr/share/empty -g pesign -c "pesign signing daemon user" pesign

%post
/sbin/chkconfig --add pesign
%service pesign restart

%preun
if [ "$1" = "0" ]; then
	%service -q pesign stop
	/sbin/chkconfig --del pesign
fi

%postun
if [ "$1" = "0" ]; then
	%userremove pesign
	%groupremove pesign
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README TODO
%attr(755,root,root) %{_bindir}/efikeygen
%attr(755,root,root) %{_bindir}/pesign
%attr(755,root,root) %{_bindir}/pesign-client
%attr(775,pesign,pesign) %dir /etc/pki/pesign
# what should be proper owner???
%dir /etc/popt.d
/etc/popt.d/pesign.popt
/etc/rpm/macros.pesign
%attr(754,root,root) /etc/rc.d/init.d/pesign
%{systemdunitdir}/pesign.service
%attr(770,pesign,pesign) %dir /var/run/pesign
%{systemdtmpfilesdir}/pesign.conf
%{_mandir}/man1/efikeygen.1*
%{_mandir}/man1/pesign.1*
%{_mandir}/man1/pesign-client.1*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdpe.so

%files devel
%defattr(644,root,root,755)
%{_includedir}/libdpe

%files static
%defattr(644,root,root,755)
%{_libdir}/libdpe.a
