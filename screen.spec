%bcond_without	uclibc
%bcond_with	multiuser

%global serverbuild_hardened 1

Summary:	A manager that supports multiple logins on one terminal
Name:		screen
Version:	4.3.0
Release:	1
License:	GPLv2+
Group:		Terminals
URL:		http://www.gnu.org/software/screen/
Source0:	ftp://ftp.gnu.org/gnu/screen/%{name}-%{version}.tar.gz
Source1:	screen.pam
Patch1:		screen-4.0.3-libs.patch
Patch2:		screen-4.0.3-screenrc.patch
Patch3:		screen-ipv6.patch
Patch4:		screen-E3.patch
Patch5:		screen-4.1.0-suppress_remap.patch
Patch6:		screen-4.2.1-crypt.patch
Patch7:		screen-altscreen.patch
Patch15:	screen-4.2.1-uclibc-compile-fixes.patch

BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	pam-devel
BuildRequires:	utempter-devel
BuildRequires:	texinfo
%if %{with uclibc}
BuildRequires:	uClibc-devel
%endif
Requires(pre):	shadow-utils

%description
The screen utility allows you to have multiple logins on just one
terminal.  Screen is useful for users who telnet into a machine or
are connected via a dumb terminal, but want to use more than just
one login.

Install the screen package if you need a screen manager that can
support multiple logins on one terminal.

%package -n	uclibc-%{name}
Summary:	A manager that supports multiple logins on one terminal (uClibc build)
Group:		Terminals
Requires:	%{name} = %{EVRD}

%description -n	uclibc-%{name}
The screen utility allows you to have multiple logins on just one
terminal.  Screen is useful for users who telnet into a machine or
are connected via a dumb terminal, but want to use more than just
one login.

Install the screen package if you need a screen manager that can
support multiple logins on one terminal.

%prep
%setup -q
%patch1 -p1 -b .libs~
%patch2 -p1 -b .screenrc~
%patch3 -p1 -b .ipv6~
%patch4 -p1 -b .E3~
%patch5 -p1 -b .suppress_remap~
%patch6 -p1 -b .crypto~
%patch7 -p1 -b .altscreen.patch~
%patch15 -p1 -b .uclibc~
autoreconf -fiv

for i in doc/screen.texinfo; do
    iconv -f iso8859-1 -t utf-8 < $i > $i.utf8 && mv -f ${i}{.utf8,}
done

sed -e 's|/usr/local/etc/screenrc|%{_sysconfdir}/screenrc|' -i etc/etcscreenrc doc/*
sed -e 's|/local/etc/screenrc|%{_sysconfdir}/screenrc|' -i doc/*
rm config.h

%build
# 5 is tty group
CONFIGURE_TOP="$PWD"
%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
%uclibc_configure \
		--enable-colors256 \
		--with-pty-mode=0620 \
		--with-pty-group=$(getent group tty | cut -d : -f 3) \
		--disable-telnet \
		--disable-pam \
		--with-sys-screenrc=%{_sysconfdir}/screenrc \
		--with-socket-dir=%{_localstatedir}/run/screen

sed -e 's|.*#undef HAVE_BRAILLE.*|#define HAVE_BRAILLE 1|' -i config.h
%make
popd
%endif

mkdir -p glibc
pushd glibc
%configure \
		--enable-colors256 \
		--with-pty-mode=0620 \
		--with-pty-group=$(getent group tty | cut -d : -f 3) \
		--enable-telnet \
		--enable-pam \
		--enable-rxvt_osc \
		--enable-use-locale \
		--with-sys-screenrc=%{_sysconfdir}/screenrc \
		--with-socket-dir=%{_localstatedir}/run/screen

sed -e 's|.*#undef HAVE_BRAILLE.*|#define HAVE_BRAILLE 1|' -i config.h
%make
popd

%install
%if %{with uclibc}
%makeinstall_std -C uclibc
mv -f %{buildroot}%{uclibc_root}%{_bindir}/screen{-*,}
%endif
%makeinstall_std -C glibc
mv -f %{buildroot}%{_bindir}/screen{-%{version},}


install -m644 etc/etcscreenrc -D %{buildroot}%{_sysconfdir}/screenrc
install -m644 etc/screenrc -D %{buildroot}%{_sysconfdir}/skel/.screenrc
install -p -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/pam.d/screen

mkdir -p %{buildroot}%{_sysconfdir}/profile.d

cat > %{buildroot}%{_sysconfdir}/profile.d/20screen.sh <<'EOF'
if [ -z "$SCREENDIR" ]; then
	export SCREENDIR=$HOME/tmp
fi
EOF

# Create the socket dir
mkdir -p %{buildroot}%{_localstatedir}/run/screen

# And tell systemd to recreate it on start with tmpfs
mkdir -p %{buildroot}%{_tmpfilesdir}
cat <<EOF > %{buildroot}%{_tmpfilesdir}/screen.conf
# screen needs directory in /var/run
%if %{with multiuser}
d %{_localstatedir}/run/screen 0755 root root
%else
d %{_localstatedir}/run/screen 0775 root screen
%endif
EOF

%pre
/usr/sbin/groupadd -g 84 -r -f screen

%files
%doc NEWS README doc/FAQ doc/README.DOTSCREEN COPYING
%{_mandir}/man1/screen.*
%{_infodir}/screen.info*
%{_datadir}/screen
%config(noreplace) %{_sysconfdir}/profile.d/20screen.sh
%config(noreplace) %{_sysconfdir}/screenrc
%config(noreplace) %{_sysconfdir}/skel/.screenrc
%config(noreplace) %{_sysconfdir}/pam.d/screen
%{_tmpfilesdir}/screen.conf
%if %{with multiuser}
%attr(4755,root,root) %{_bindir}/screen
%ghost %attr(755,root,root) %{_localstatedir}/run/screen
%else
%attr(2755,root,screen) %{_bindir}/screen
%ghost %attr(775,root,screen) %{_localstatedir}/run/screen
%endif

%if %{with uclibc}
%files -n uclibc-%{name}
%{uclibc_root}%{_bindir}/screen
%endif
