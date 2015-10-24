%define _optdir	/opt/usr

Name:       media-data-sdk
Summary:    Media data for SDK. Image/Sounds/Videos and Others.
Version: 0.1.45
Release:    1
Group:      TO_BE/FILLED_IN
License:    CC-BY-ND-3.0
Source0:    %{name}-%{version}.tar.gz
Requires: coreutils
Requires: media-server
BuildRequires: cmake
BuildRequires: sqlite

%description
Description: Media data for SDK. Image/Sounds/Videos and Others.

%prep
%setup -q
LDFLAGS+="-Wl,--rpath=%{PREFIX}/lib -Wl,--as-needed -Wl,--hash-style=both"; export LDFLAGS

%build
cmake . -DCMAKE_INSTALL_PREFIX=%{_optdir}

make %{?jobs:-j%jobs}

%install
%make_install

#remove unusing files
rm %{buildroot}/opt/usr/media/Downloads/DOWNLOADS
rm %{buildroot}/opt/usr/media/Videos/VIDEOS
rm %{buildroot}/opt/usr/media/Images/IMAGES
rm %{buildroot}/opt/usr/share/media/.thumb/phone/*
rm %{buildroot}/opt/usr/share/media/.thumb/mmc/*
rm %{buildroot}/opt/usr/media/Sounds/Voice\ Recorder/VOICE
rm %{buildroot}/opt/usr/media/Sounds/SOUNDS
rm %{buildroot}/opt/usr/media/Music/MUSIC
rm %{buildroot}/opt/usr/media/Documents/DOCUMENTS
rm %{buildroot}/opt/usr/media/Others/OTHERS
rm %{buildroot}/opt/usr/media/DCIM/DCIM

#Create DB
mkdir -p %{buildroot}/opt/usr/dbspace
sqlite3 %{buildroot}/opt/usr/dbspace/.media.db 'PRAGMA journal_mode = PERSIST; PRAGMA user_version=4;'

#License
mkdir -p %{buildroot}/%{_datadir}/license
cp -rf %{_builddir}/%{name}-%{version}/LICENSE.CCPLv3.0 %{buildroot}/%{_datadir}/license/%{name}

%post
#make directory
mkdir -p /opt/usr/apps/media-server/data
chsmack -a 'media-server' /opt/usr/apps/media-server/data

#change permission
chmod 664 /opt/usr/dbspace/.media.db*
chmod 775 /opt/usr/apps/media-server/data
chmod 775 /opt/usr/share/media/.thumb
chmod 775 /opt/usr/share/media/.thumb/phone
chmod 775 /opt/usr/share/media/.thumb/mmc

#change owner
chown -R 5000:5000 /opt/usr/media/*
chown 200:5000 /opt/usr/dbspace/.media.db*
chown 200:5000 /opt/usr/apps/media-server/data
chown -R 200:5000 /opt/usr/share/media/.thumb

#change group (6017: db_filemanager 5000: app)
chgrp 5000 /opt/usr/dbspace

#SMACK for DB
if [ -f /opt/usr/dbspace/.media.db ]
then
	chsmack -a 'media-data::db' /opt/usr/dbspace/.media.db*
fi

chsmack -a 'system::media' /opt/usr/share/media
chsmack -a 'system::media' /opt/usr/share/media/.thumb
chsmack -a 'system::media' /opt/usr/share/media/.thumb/phone
chsmack -a 'system::media' /opt/usr/share/media/.thumb/mmc
chsmack -a 'system::media' /opt/usr/share/media/.thumb/thumb_default.png

chsmack -t /opt/usr/share/media
chsmack -t /opt/usr/share/media/.thumb
chsmack -t /opt/usr/share/media/.thumb/phone
chsmack -t /opt/usr/share/media/.thumb/mmc

%files
%manifest media-data-sdk.manifest
%defattr(-,root,root,-)
%{_optdir}/share/media/.thumb/*
%{_optdir}/media/*
%attr(660,system,app) /opt/usr/dbspace/.media.db*
%config(noreplace) /opt/usr/dbspace/.media.db*

#License
%{_datadir}/license/%{name}

