%bcond_with multiuser
%global serverbuild_hardened 1

Summary: A screen manager that supports multiple logins on one terminal
Name: screen
Version: 4.1.0
Release: 0.18.20120314git3c2946%{?dist}
License: GPLv2+

URL: http://www.gnu.org/software/screen
BuildRequires: ncurses-devel pam-devel utempter-devel autoconf texinfo
BuildRequires: automake

#Source0: ftp://ftp.uni-erlangen.de/pub/utilities/screen/screen-%{version}.tar.gz
# snapshot from git://git.savannah.gnu.org/screen.git
Source0: screen-20120314git3c2946.tar.bz2
Source1: screen.pam

Patch1: screen-4.0.3-libs.patch
Patch2: screen-4.0.3-screenrc.patch
Patch3: screen-ipv6.patch
Patch4: screen-cc.patch
Patch5: screen-E3.patch
Patch6: screen-4.1.0-suppress_remap.patch
Patch7: screen-4.1.0-reattach.patch
Patch8: screen-4.1.0-crypt.patch
Patch9: screen-4.1.0-long-term.patch
Patch10: screen-help-update.patch
Patch11: screen-altscreen.patch
Patch12: screen-man-update.patch

%description
The screen utility allows you to have multiple logins on just one
terminal.  Screen is useful for users who telnet into a machine or
are connected via a dumb terminal, but want to use more than just
one login.

Install the screen package if you need a screen manager that can
support multiple logins on one terminal.

%prep
%setup -q -n screen/src
%patch1 -p1 -b .libs
%patch2 -p1 -b .screenrc
%patch3 -p2 -b .ipv6
%patch4 -p2 -b .cc
%patch5 -p2 -b .E3
%patch6 -p1 -b .suppress_remap
%patch7 -p2 -b .reattach
%patch8 -p2 -b .crypto
%patch9 -p2 -b .long-term
%patch10 -p2 -b .help-update
%patch11 -p2 -b .altscreen.patch
%patch12 -p2 -b .man-update.patch


%build
./autogen.sh

%configure2_5x \
	--enable-pam \
	--enable-colors256 \
	--enable-rxvt_osc \
	--enable-use-locale \
	--enable-telnet \
	--with-pty-mode=0620 \
	--with-pty-group=$(getent group tty | cut -d : -f 3) \
	--with-sys-screenrc="%{_sysconfdir}/screenrc" \
	--with-socket-dir="%{_localstatedir}/run/screen"

# We would like to have braille support.
sed -i -e 's/.*#.*undef.*HAVE_BRAILLE.*/#define HAVE_BRAILLE 1/;' config.h

sed -i -e 's/\(\/usr\)\?\/local\/etc/\/etc/g;' doc/screen.{1,texinfo}

for i in doc/screen.texinfo; do
    iconv -f iso8859-1 -t utf-8 < $i > $i.utf8 && mv -f ${i}{.utf8,}
done

rm -f doc/screen.info*

# fails with %{?_smp_mflags}
make

%install
make install DESTDIR=$RPM_BUILD_ROOT
mv -f $RPM_BUILD_ROOT%{_bindir}/screen{-%{version},}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
install -m 0644 etc/etcscreenrc $RPM_BUILD_ROOT%{_sysconfdir}/screenrc
cat etc/screenrc >> $RPM_BUILD_ROOT%{_sysconfdir}/screenrc

# Better not forget to copy the pam file around
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/screen

# Create the socket dir
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/screen

# And tell systemd to recreate it on start with tmpfs
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d
cat <<EOF > $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/screen.conf
# screen needs directory in /var/run
%if %{with multiuser}
d %{_localstatedir}/run/screen 0755 root root
%else
d %{_localstatedir}/run/screen 0775 root screen
%endif
EOF

# Remove files from the buildroot which we don't want packaged
rm -f $RPM_BUILD_ROOT%{_infodir}/dir

%pre
/usr/sbin/groupadd -g 84 -r -f screen
:

%files
%doc NEWS README doc/FAQ doc/README.DOTSCREEN COPYING
%{_mandir}/man1/screen.*
%{_infodir}/screen.info*
%{_datadir}/screen
%config(noreplace) %{_sysconfdir}/screenrc
%config(noreplace) %{_sysconfdir}/pam.d/screen
%{_sysconfdir}/tmpfiles.d/screen.conf
%if %{with multiuser}
%attr(4755,root,root) %{_bindir}/screen
%attr(755,root,root) %{_localstatedir}/run/screen
%else
%attr(2755,root,screen) %{_bindir}/screen
%attr(775,root,screen) %{_localstatedir}/run/screen
%endif
