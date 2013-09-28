%bcond_without	uclibc

Summary:	A manager that supports multiple logins on one terminal
Name:		screen
Version:	4.0.3
Release:	14
License:	GPLv2+
Group:		Terminals
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	utempter-devel
BuildRequires:	texinfo
%if %{with uclibc}
BuildRequires:	uClibc-devel
%endif
URL:		http://www.gnu.org/software/screen/
Source0:	ftp://ftp.uni-erlangen.de/pub/utilities/screen/%{name}-%{version}.tar.gz

# correct the location of various files in man page and info page 
# not sent upstream
Patch4:		screen-3.9.11-fix-utmp.diff
# do not link with libelf, this is not needed
Patch6:		screen-3.9.13-no-libelf.patch
# for portability ? is it needed ? in doubt, let's apply it
# fixed upstream git on b4aa8750 , but that's a different fix
Patch7:		screen-3.9.11-biarch-utmp.patch
# add U as default binding to switch to utf8, in /etc/screenrc
# not to send upstream
Patch8:		screen-4.0.2-screenrc-utf8-switch.patch
# manpage of execl specify that the list should be NULL terminated, so there is a bug
# i however do not know if this fix a crash or anything
# already fixed upstream, different fix
Patch9:		screen-4.0.2-varargs.patch
# add ipv6 support to the builtin telnet client
Patch12:	screen-4.0.3-ipv6.patch
# from git, workaround vte's autodetect DEL
Patch13:	screen-4.0.3-vte-autodetect-workaround.patch
# Prevent format-string errors
# sent upstream : https://savannah.gnu.org/bugs/index.php?29024
Patch14:	screen-4.0.3-format-string.patch
Patch15:	screen-4.0.3-uclibc-compile-fixes.patch

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
%patch4 -p1
%patch6 -p1 -b .no-libelf
%patch7 -p1 -b .biarch-utmp
%patch8 -p0
%patch9 -p1 -b .varargs
%patch12 -p1 -b .ipv6
%patch13 -p2 -b .vte
%patch14 -p1 -b .format-string
%patch15 -p1 -b .uclibc~
autoconf -f

%build
# 5 is tty group
CONFIGURE_TOP="$PWD"
%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
%uclibc_configure \
		--enable-colors256 \
		--with-pty-mode=0620 \
		--with-pty-group=5 \
		--disable-telnet \
		--disable-pam \
		--with-sys-screenrc=%{_sysconfdir}/screenrc
sed -e 's|.*#undef HAVE_BRAILLE.*|#define HAVE_BRAILLE 1|' -i config.h
%make
popd

mkdir -p glibc
pushd glibc
%configure2_5x	--enable-colors256 \
		--with-pty-mode=0620 \
		--with-pty-group=5 \
		--enable-telnet \
		--enable-pam \
		--with-sys-screenrc=%{_sysconfdir}/screenrc
sed -e 's|.*#undef HAVE_BRAILLE.*|#define HAVE_BRAILLE 1|' -i config.h
%make
popd
%endif

perl -pi -e 's|.*#undef HAVE_BRAILLE.*|#define HAVE_BRAILLE 1|' config.h

sed -e 's|/usr/local/etc/screenrc|%{_sysconfdir}/screenrc|' -i etc/etcscreenrc doc/*
sed -e 's|/local/etc/screenrc|%{_sysconfdir}/screenrc|' -i doc/*

%install
%if %{with uclibc}
%makeinstall_std -C uclibc
mv -f %{buildroot}%{uclibc_root}%{_bindir}/screen{-*,}
%endif
%makeinstall_std -C glibc

( cd %{buildroot}/%{_bindir} && {
	rm -f screen.old screen
	mv screen-%{version} screen
  }
)

install -m644 etc/etcscreenrc -D %{buildroot}%{_sysconfdir}/screenrc
install -m644 etc/screenrc -D %{buildroot}%{_sysconfdir}/skel/.screenrc

mkdir -p %{buildroot}%{_sysconfdir}/profile.d

cat > %{buildroot}%{_sysconfdir}/profile.d/20screen.sh <<'EOF'
if [ -z "$SCREENDIR" ]; then
	export SCREENDIR=$HOME/tmp
fi
EOF

%files
%doc NEWS README doc/FAQ doc/README.DOTSCREEN ChangeLog
%{_bindir}/screen
%{_mandir}/man1/screen.1*
%{_infodir}/screen.info*
%config(noreplace) %{_sysconfdir}/profile.d/20screen.sh
%config(noreplace) %{_sysconfdir}/screenrc
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/skel/.screenrc
%{_datadir}/screen/

%if %{with uclibc}
%files -n uclibc-%{name}
%{uclibc_root}%{_bindir}/screen
%endif

%changelog
* Mon Jun 04 2012 Andrey Bondrov <abondrov@mandriva.org> 4.0.3-12
+ Revision: 802224
- Drop some legacy junk

* Tue Mar 06 2012 Sergio Rafael Lemke <sergio@mandriva.com> 4.0.3-11
+ Revision: 782522
- Rebuild and fix rpmlint complains

* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 4.0.3-10
+ Revision: 669965
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 4.0.3-9mdv2011.0
+ Revision: 607529
- rebuild

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 4.0.3-8mdv2010.1
+ Revision: 519070
- rebuild

  + Michael Scherer <misc@mandriva.org>
    - remove old ppc patch as we have no ppc port, and as the patch seems to be a
      work around for some awk bug
    - remove unneeded patch coming from rh for old ia64 problem

* Mon Jun 22 2009 Lev Givon <lev@mandriva.org> 4.0.3-7mdv2010.0
+ Revision: 388108
- Refactor ia64 patch.
  Add patch to fix format-string errors.
  Enable 256 color support.

* Mon Oct 13 2008 Funda Wang <fwang@mandriva.org> 4.0.3-6mdv2009.1
+ Revision: 293321
- add patch from git to wor around vte's del key autodetect feature
  https://savannah.gnu.org/bugs/index.php?23868
- clearify the license

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 4.0.3-5mdv2009.0
+ Revision: 225411
- rebuild

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Sat Dec 22 2007 Guillaume Rousse <guillomovitch@mandriva.org> 4.0.3-4mdv2008.1
+ Revision: 137010
- no executable bit on profile scriptlet
  order prefix on profile scriptlet

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Sep 24 2007 Thierry Vignaud <tv@mandriva.org> 4.0.3-3mdv2008.0
+ Revision: 92613
- fix man pages extension


* Wed Mar 14 2007 Michael Scherer <misc@mandriva.org> 4.0.3-2mdv2007.1
+ Revision: 143661
- remove patch11, was unclear and caused problem ( #29468 )

* Thu Jan 25 2007 Per Øyvind Karlsen <pkarlsen@mandriva.com> 4.0.3-1mdv2007.1
+ Revision: 113524
- new release: 4.0.5
- bump MAXSTR (string buffer size) to 4k (from 256 bytes), fixes
  status line issues with window list in status line and too many
  windows (and possibly other issues with long strings) (P11 from fedora)
- ipv6 patch (RHBZ #198410)

* Tue Oct 31 2006 Michael Scherer <misc@mandriva.org> 4.0.2-10mdv2007.1
+ Revision: 74233
- Bump release
- document the remaining patchs
-remove patch 5, screen-3.9.11-max-window-size.diff, as it does nothing except setting a constant,
  that is used nowhere in the source ( and nowhere on the internet, according to google code search and
  koders.com )
- remove Patch0, it is applied to a code snippet enclosed in a #if !defined(linux), so it doesn't
  apply to this package, unless we start to port mandriva to bsd.
- bunzip patch
- add fix for CVE-2006-4573
- Import screen

* Tue Sep 19 2006 Gwenole Beauchesne <gbeauchesne@mandriva.com> 4.0.2-9mdv2007.0
- Rebuild

* Fri Jul 21 2006 Michael Scherer <misc@mandriva.org> 4.0.2-8mdv2007.0
- use mkrel
- clean buildRoot

* Mon May 08 2006 Stefan van der Eijk <stefan@eijk.nu> 4.0.2-7mdk
- rebuild for sparc

* Wed Aug 24 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 4.0.2-6mdk
- varargs fixes

* Tue Apr 26 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.0.2-5mdk
- Patch 8: add 'C-a U' binding to /etc/skel/.screenrc

* Tue Nov 09 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.0.2-4mdk
- The screen profile.d script (and hence $SCREENDIR) was broken

* Thu Oct 14 2004 Olivier Thauvin <thauvin@aerov.jussieu.fr> 4.0.2-3mdk
- don't use a bash fonction to start screen profile.d, exporting SCREENDIR instead

* Wed Apr 21 2004 Olivier Blin <blino@mandrake.org> 4.0.2-2mdk
- rebuild for new libncurses

