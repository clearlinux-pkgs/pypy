# Build PyPy without autospec

Name     : pypy
Version  : 5.4.1
Release  : 6
Source0  : https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.4.1-src.zip
Summary  : Python implementation with a tracing JIT compiler
Group    : Development/Tools
License  : MIT Python-2.0 Apache-2.0 TCL
URL      : http://pypy.org

#Additional sources, patches and customiztions
Patch0: add_library_link_logic.patch
Patch1: add_makefile.patch
Patch2: update_python_path.patch
Patch3: add_gupb_spambayes.patch
#turn off brp-python-bytecompile
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')


############## Build Requirements #############
BuildRequires : python-dev
BuildRequires:  libffi-dev
BuildRequires:  tcl-dev
BuildRequires:  tk-dev
BuildRequires:  libX11-dev
BuildRequires:  sqlite-autoconf-dev
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  zlib-dev
BuildRequires:  bzip2-dev
BuildRequires:  ncurses-dev
BuildRequires:  expat-dev
BuildRequires:  openssl-dev
BuildRequires:  gdbm-dev
BuildRequires:  cffi

############# Package definitions #############
%description
PyPy implements a tracing JIT resulting in better performance

#define the packages

%package lib
Summary:        Runtime libs for PyPy
Group:          devel/pypy
Requires:	pypy-core
%description lib
Libraries required for the PyPy impplementation of the  Python Programming Language.

%package core
Summary:        PyPy JIT implementation for the Python Programming Language
Group:          devel/pypy

%description core
The PyPy JIT version of the Python Programming Language.

%package dev
Summary:        The Python Programming Language
Group:          devel
Requires:       pypy-lib
Requires:       pypy-core

%description dev
Header files for building PyPy C extension modules

#################### prep and build  ##########

%prep
%setup -q -n %{name}2-v%{version}-src
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build

#Builds core PyPy
RPM_BUILD_ROOT= \
PYPY_USESSION_DIR=$(pwd) \
PYPY_USESSION_BASENAME=%{name} \
python rpython/bin/rpython -Ojit pypy/goal/targetpypystandalone.py

#Builds cffi modules
PYTHONPATH=. ./pypy-c pypy/tool/build_cffi_imports.py

################### installation phase ########
%install
#rm -rf %{buildroot}
mkdir -p  %{buildroot}/%{_bindir}

#Basically, first install pypy to %{buildroot}/usr/lib64/pypy-version
%global pypy_install_location  %{buildroot}/%{_libdir}
%global pypy_dir %{name}-%{version}
%global pypy_absolute_path %{pypy_install_location}/%{pypy_dir}
%global pypy_relative_path %{_libdir}/%{pypy_dir}

mkdir -p %{pypy_install_location}/%{pypy_dir}

python pypy/tool/release/package.py --override_pypy_c ./pypy-c --archive-name %{pypy_dir} --builddir %{pypy_install_location}

#symlinking pypy binary to %{buildroot}/usr/bin/pypy and moving libpypy to %{buildroot}/usr/lib64/ 
ln -sf  %{pypy_relative_path}/bin/%{name} %{buildroot}/%{_bindir}/%{name}
mv  %{pypy_absolute_path}/bin/libpypy-c.so %{buildroot}/%{_libdir}

#get rid of the "installed but unpackaged files found" error
rm -rf %{pypy_install_location}/%{pypy_dir}.tar.bz2
rm -rf %{pypy_absolute_path}/LICENSE
rm -rf %{pypy_absolute_path}/README.rst
rm -rf %{pypy_absolute_path}/include/README

################ files to be packaged ########

%files lib
%license LICENSE
%doc README.rst
%dir %{pypy_relative_path}
%dir %{pypy_relative_path}/lib-python
%{_libdir}/libpypy-c.so
%{pypy_relative_path}/lib-python/2.7/
%{pypy_relative_path}/lib_pypy/
%{pypy_relative_path}/site-packages/

%files core
%license LICENSE
%doc README.rst
%{_bindir}/%{name}
%{pypy_relative_path}/bin/%{name}

%files dev
%dir %{pypy_relative_path}/include
%{pypy_relative_path}/include/*.h
%{pypy_relative_path}/include/_numpypy/numpy

