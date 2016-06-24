Summary:	Signing tool for PE-COFF binaries
Summary(pl.UTF-8):	Narzędzie do podpisywania binariów PE-COFF
Name:		pesign
Version:	0.112
Release:	2
License:	GPL v2
Group:		Applications/System
#Source0Download: https://github.com/rhinstaller/pesign/releases
Source0:	https://github.com/rhinstaller/pesign/releases/download/%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	eae1d66e160be744ff310ad7592ae31e
Patch0:		%{name}-pld.patch
Patch1:		%{name}-build.patch
URL:		https://github.com/rhinstaller/pesign
BuildRequires:	efivar-devel
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
%patch1 -p1

%{__sed} -i -e 's/-g -O0/%{rpmcflags} -Wno-unused-result/' Make.defaults

%{__sed} -i -e 's,\$(libdatadir)systemd/system,%{systemdunitdir},' src/Makefile

%build
%{__make} \
	CC="%{__cc}" \
	LIBDIR=%{_libdir} \
	libexecdir=%{_libdir}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install install_systemd install_sysvinit \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir} \
	libexecdir=%{_libdir}

# omitted from install (as of 0.112)
install libdpe/libdpe.so $RPM_BUILD_ROOT%{_libdir}/libdpe.so.%{version}
ln -sf libdpe.so.%{version} $RPM_BUILD_ROOT%{_libdir}/libdpe.so.0
ln -sf libdpe.so.%{version} $RPM_BUILD_ROOT%{_libdir}/libdpe.so
cp -p libdpe/libdpe.a $RPM_BUILD_ROOT%{_libdir}
install -d $RPM_BUILD_ROOT%{_includedir}/libdpe
cp -p include/libdpe/*.h $RPM_BUILD_ROOT%{_includedir}/libdpe

# just unwanted COPYING file; make space for %doc
%{__rm} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/COPYING

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
%attr(755,root,root) %{_bindir}/authvar
%attr(755,root,root) %{_bindir}/efikeygen
%attr(755,root,root) %{_bindir}/efisiglist
%attr(755,root,root) %{_bindir}/pesigcheck
%attr(755,root,root) %{_bindir}/pesign
%attr(755,root,root) %{_bindir}/pesign-client
%dir %{_libdir}/pesign
%attr(755,root,root) %{_libdir}/pesign/pesign-authorize-groups
%attr(755,root,root) %{_libdir}/pesign/pesign-authorize-users
%dir %{_sysconfdir}/pesign
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pesign/groups
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pesign/users
%attr(775,pesign,pesign) %dir /etc/pki/pesign
# what should be proper owner???
%dir /etc/popt.d
/etc/popt.d/pesign.popt
/etc/rpm/macros.pesign
%attr(754,root,root) /etc/rc.d/init.d/pesign
%{systemdunitdir}/pesign.service
%attr(770,pesign,pesign) %dir /var/run/pesign
%{systemdtmpfilesdir}/pesign.conf
%{_mandir}/man1/authvar.1*
%{_mandir}/man1/efikeygen.1*
%{_mandir}/man1/efisiglist.1*
%{_mandir}/man1/pesigcheck.1*
%{_mandir}/man1/pesign.1*
%{_mandir}/man1/pesign-client.1*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdpe.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libdpe.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdpe.so
%{_includedir}/libdpe

%files static
%defattr(644,root,root,755)
%{_libdir}/libdpe.a
