Summary:	A screen manager that supports multiple logins on one terminal
Name:		screen
Version:	4.0.3
Release: 	%mkrel 4
License:	GPL
Group:		Terminals
BuildRequires:	ncurses-devel
BuildRequires:	utempter-devel
BuildRequires:	texinfo
URL:		http://www.gnu.org/software/screen/
Source0:	ftp://ftp.uni-erlangen.de/pub/utilities/screen/%{name}-%{version}.tar.gz
# TODO check if still needed
Patch1: 	screen-ia64.patch
# TODO check if still needed 
Patch3:		screen-makefile-ppc.patch
# correct the location of various files in man page and info page 
Patch4:		screen-3.9.11-fix-utmp.diff
# do not link with libelf, this is not needed
Patch6:		screen-3.9.13-no-libelf.patch
# for portability ? is it needed ? in doubt, let's apply it
Patch7:		screen-3.9.11-biarch-utmp.patch
# add U as default binding to switch to utf8, in /etc/screenrc
Patch8:		screen-4.0.2-screenrc-utf8-switch.patch
# manpage of execl specify that the list should be NULL terminated, so there is a bug
# i however do not know if this fix a crash or anything
Patch9:		screen-4.0.2-varargs.patch
# add ipv6 support to the builtin telnet client
Patch12:	screen-4.0.3-ipv6.patch
Requires(post): info-install
Requires(pre):  info-install
BuildRoot:	%{_tmppath}/%{name}-root

%description
The screen utility allows you to have multiple logins on just one
terminal.  Screen is useful for users who telnet into a machine or
are connected via a dumb terminal, but want to use more than just
one login.

Install the screen package if you need a screen manager that can
support multiple logins on one terminal.

%prep

%setup -q
%patch1 -p1
%ifarch ppc
%patch3 -p1
%endif
%patch4 -p1
%patch6 -p1 -b .no-libelf
%patch7 -p1 -b .biarch-utmp
%patch8 -p0
%patch9 -p1 -b .varargs
%patch12 -p1 -b .ipv6

%build
%configure
perl -pi -e 's|.*#.*PTYMODE.*|#define PTYMODE 0620|' config.h
perl -pi -e 's|.*#.*PTYGROUP.*|#define PTYGROUP 5|' config.h

perl -pi -e 's|.*#undef HAVE_BRAILLE.*|#define HAVE_BRAILLE 1|' config.h
perl -pi -e 's|.*#undef BUILTIN_TELNET.*|#define BUILTIN_TELNET 1|' config.h

perl -pi -e 's|%{_prefix}/etc/screenrc|%{_sysconfdir}/screenrc|' config.h
perl -pi -e 's|/usr/local/etc/screenrc|%{_sysconfdir}/screenrc|' etc/etcscreenrc doc/*
perl -pi -e 's|/local/etc/screenrc|%{_sysconfdir}/screenrc|' doc/*
rm doc/screen.info*

%make CFLAGS="$RPM_OPT_FLAGS -DETCSCREENRC=\\\"%{_sysconfdir}/screenrc\\\""

%install
rm -Rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/skel

%makeinstall SCREENENCODINGS=%buildroot/%{_datadir}/screen/utf8encodings/

( cd $RPM_BUILD_ROOT/%{_bindir} && {
	rm -f screen.old screen
	mv screen-%{version} screen
  }
)

install -c -m 0644 etc/etcscreenrc $RPM_BUILD_ROOT/%{_sysconfdir}/screenrc
install -c -m 0644 etc/screenrc $RPM_BUILD_ROOT/%{_sysconfdir}/skel/.screenrc

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/profile.d

cat > $RPM_BUILD_ROOT/%{_sysconfdir}/profile.d/20screen.sh <<'EOF'
if [ -z "$SCREENDIR" ]; then
    export SCREENDIR=$HOME/tmp
fi
EOF

%clean
rm -fr $RPM_BUILD_ROOT

%post
%_install_info %name.


%preun
%_remove_install_info %name

%files
%defattr(-,root,root)
%doc NEWS README doc/FAQ doc/README.DOTSCREEN ChangeLog
%{_bindir}/screen
%{_mandir}/man1/screen.1*
%{_infodir}/screen.info*
%config(noreplace) %{_sysconfdir}/profile.d/20screen.sh
%config(noreplace) %{_sysconfdir}/screenrc
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/skel/.screenrc
%{_datadir}/screen/


