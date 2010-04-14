Name:		ganglia-plugin-iptables
Version:	20100413.1
Release:	1%{?dist}
Summary:	iptables plugin for ganglia.

Group:		SEAS
License:	SEAS
Source0:	ganglia_iptables-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	python
BuildRequires:	python-setuptools
Requires:	python
Requires:	ganglia-gmond

%description
iptables plugin for ganglia.

%prep
%setup -q -n ganglia_iptables-%{version}

%build
python setup.py build


%install
rm -rf $RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/ganglia/python_modules
python setup.py install --root=$RPM_BUILD_ROOT \
	--install-scripts=%{_libdir}/ganglia/python_modules

install -d -m 755 $RPM_BUILD_ROOT/etc/ganglia/conf.d
install -m 644 iptables.pyconf.sample $RPM_BUILD_ROOT/etc/ganglia/conf.d/iptables.pyconf

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)

%{_libdir}/ganglia/python_modules/*
/usr/lib/*/site-packages/*

%config /etc/ganglia/conf.d/iptables.pyconf

%changelog

