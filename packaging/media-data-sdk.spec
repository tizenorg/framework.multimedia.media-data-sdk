%define _optdir	/opt

Name:       media-data-sdk
Summary:    Media data for SDK. Image/Sounds/Videos and Others.
Version: 0.1.31
Release:    1
Group:      TO_BE/FILLED_IN
License:    TO_BE/FILLED_IN
Source0:    %{name}-%{version}.tar.gz
BuildRequires: cmake

%description
Description: Media data for SDK. Image/Sounds/Videos and Others.

%prep
%setup -q
LDFLAGS+="-Wl,--rpath=%{PREFIX}/lib -Wl,--as-needed -Wl,--hash-style=both"; export LDFLAGS

cmake . -DCMAKE_INSTALL_PREFIX=%{_optdir}

%build
make %{?jobs:-j%jobs}

%install
%make_install

%post
if [ ! -d /opt/dbspace ]; then
	mkdir -p /opt/dbspace
fi

if  [ ! -f /opt/dbspace/.media.db ]
then
	sqlite3 /opt/dbspace/.media.db 'PRAGMA journal_mode = PERSIST;

	CREATE TABLE IF NOT EXISTS album (album_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, artist TEXT, album_art TEXT, unique(name, artist));
	CREATE TABLE IF NOT EXISTS bookmark (bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT, media_uuid TEXT NOT NULL, marked_time INTEGER DEFAULT 0, thumbnail_path  TEXT, unique(media_uuid, marked_time));
	CREATE TABLE IF NOT EXISTS folder (folder_uuid TEXT PRIMARY KEY, path TEXT NOT NULL UNIQUE, name TEXT NOT NULL, modified_time INTEGER DEFAULT 0, storage_type INTEGER, unique(path, name, storage_type));
	CREATE TABLE IF NOT EXISTS media (media_uuid TEXT PRIMARY KEY, path TEXT NOT NULL UNIQUE, file_name TEXT NOT NULL, media_type INTEGER, mime_type TEXT, size INTEGER DEFAULT 0, added_time INTEGER DEFAULT 0, modified_time INTEGER DEFAULT 0, folder_uuid TEXT NOT NULL, thumbnail_path TEXT, title TEXT, album_id INTEGER DEFAULT 0, album TEXT, artist TEXT, genre TEXT, composer TEXT, year TEXT, recorded_date TEXT, copyright TEXT, track_num TEXT, description TEXT, bitrate INTEGER DEFAULT -1, samplerate INTEGER DEFAULT -1, channel INTEGER DEFAULT -1, duration INTEGER DEFAULT -1, longitude DOUBLE DEFAULT 0, latitude DOUBLE DEFAULT 0, altitude DOUBLE DEFAULT 0, width INTEGER DEFAULT -1, height INTEGER DEFAULT -1, datetaken TEXT, orientation INTEGER DEFAULT -1, played_count INTEGER DEFAULT 0, last_played_time INTEGER DEFAULT 0, last_played_position INTEGER DEFAULT 0, rating INTEGER DEFAULT 0, favourite INTEGER DEFAULT 0, author TEXT, provider TEXT, content_name TEXT, category TEXT, location_tag TEXT, age_rating TEXT, keyword TEXT, is_drm INTEGER DEFAULT 0, storage_type INTEGER, validity INTEGER DEFAULT 1, unique(path, file_name) );
	CREATE TABLE IF NOT EXISTS playlist ( playlist_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE );
	CREATE TABLE IF NOT EXISTS playlist_map ( _id INTEGER PRIMARY KEY AUTOINCREMENT, playlist_id INTEGER NOT NULL, media_uuid TEXT NOT NULL, play_order INTEGER NOT NULL );
	CREATE TABLE IF NOT EXISTS tag ( tag_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE );
	CREATE TABLE IF NOT EXISTS tag_map ( _id INTEGER PRIMARY KEY AUTOINCREMENT, tag_id INTEGER NOT NULL, media_uuid TEXT NOT NULL, unique(tag_id, media_uuid) );
	CREATE INDEX folder_folder_uuid_idx on folder (folder_uuid);
	CREATE INDEX folder_uuid_idx on media (folder_uuid);
	CREATE INDEX media_album_idx on media (album);
	CREATE INDEX media_artist_idx on media (artist);
	CREATE INDEX media_author_idx on media (author);
	CREATE INDEX media_category_idx on media (category);
	CREATE INDEX media_composer_idx on media (composer);
	CREATE INDEX media_content_name_idx on media (content_name);
	CREATE INDEX media_file_name_idx on media (file_name);
	CREATE INDEX media_genre_idx on media (genre);
	CREATE INDEX media_location_tag_idx on media (location_tag);
	CREATE INDEX media_media_type_idx on media (media_type);
	CREATE INDEX media_media_uuid_idx on media (media_uuid);
	CREATE INDEX media_modified_time_idx on media (modified_time);
	CREATE INDEX media_path_idx on media (path);
	CREATE INDEX media_provider_idx on media (provider);
	CREATE INDEX media_title_idx on media (title);
	CREATE TRIGGER album_cleanup DELETE ON media BEGIN DELETE FROM album WHERE (SELECT count(*) FROM media WHERE album_id=old.album_id)=1 AND album_id=old.album_id;END;
	CREATE TRIGGER bookmark_cleanup DELETE ON media BEGIN DELETE FROM bookmark WHERE media_uuid=old.media_uuid;END;
	CREATE TRIGGER folder_cleanup DELETE ON media BEGIN DELETE FROM folder WHERE (SELECT count(*) FROM media WHERE folder_uuid=old.folder_uuid)=1 AND folder_uuid=old.folder_uuid;END;
	CREATE TRIGGER playlist_map_cleanup DELETE ON media BEGIN DELETE FROM playlist_map WHERE media_uuid=old.media_uuid;END;
	CREATE TRIGGER playlist_map_cleanup_1 DELETE ON playlist BEGIN DELETE FROM playlist_map WHERE playlist_id=old.playlist_id;END;
	CREATE TRIGGER tag_map_cleanup DELETE ON media BEGIN DELETE FROM tag_map WHERE media_uuid=old.media_uuid;END;
	CREATE TRIGGER tag_map_cleanup_1 DELETE ON tag BEGIN DELETE FROM tag_map WHERE tag_id=old.tag_id;END;

	CREATE VIEW IF NOT EXISTS playlist_view 
	AS
	SELECT 
	p.playlist_id, p.name, media_count, pm._id as pm_id, pm.play_order, m.media_uuid, path, file_name, media_type, mime_type, size, added_time, modified_time, thumbnail_path, description, rating, favourite, author, provider, content_name, category, location_tag, age_rating, keyword, is_drm, storage_type, longitude, latitude, altitude, width, height, datetaken, orientation, title, album, artist, genre, composer, year, recorded_date, copyright, track_num, bitrate, duration, played_count, last_played_time, last_played_position, samplerate, channel FROM playlist AS p 
	INNER JOIN playlist_map AS pm 
	INNER JOIN media AS m 
	INNER JOIN (SELECT count(playlist_id) as media_count, playlist_id FROM playlist_map group by playlist_id) as cnt_tbl
		ON (p.playlist_id=pm.playlist_id AND pm.media_uuid = m.media_uuid AND cnt_tbl.playlist_id=pm.playlist_id AND m.validity=1)
	UNION
	SELECT 
		playlist_id, name, 0, 0, -1, NULL, NULL, -1, -1, -1, -1, -1, NULL, NULL, -1, -1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, -1, -1, -1, -1, -1, -1, -1, -1, -1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, -1, -1, -1, -1, -1, -1, NULL, -1 FROM playlist 
	WHERE playlist_id 
	NOT IN (select playlist_id from playlist_map); 

	CREATE VIEW IF NOT EXISTS tag_view AS
	SELECT 
	t.tag_id, t.name, media_count, tm._id as tm_id, m.media_uuid, path, file_name, media_type, mime_type, size, added_time, modified_time, thumbnail_path, description, rating, favourite, author, provider, content_name, category, location_tag, age_rating, keyword, is_drm, storage_type, longitude, latitude, altitude, width, height, datetaken, orientation, title, album, artist, genre, composer, year, recorded_date, copyright, track_num, bitrate, duration, played_count, last_played_time, last_played_position, samplerate, channel FROM tag AS t 
	INNER JOIN tag_map AS tm 
	INNER JOIN media AS m 
	INNER JOIN (SELECT count(tag_id) as media_count, tag_id FROM tag_map group by tag_id) as cnt_tbl
		ON (t.tag_id=tm.tag_id AND tm.media_uuid = m.media_uuid AND cnt_tbl.tag_id=tm.tag_id AND m.validity=1)
	UNION
	SELECT 
		tag_id, name, 0, 0,  NULL, NULL, -1, -1, -1, -1, -1, NULL, NULL, -1, -1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, -1, -1, -1, -1, -1, -1, -1, -1, -1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, -1, -1, -1, -1, -1, -1, NULL, -1 FROM tag 
	WHERE tag_id 
	NOT IN (select tag_id from tag_map); 

	INSERT INTO media VALUES("60aea677-4742-408e-b5f7-f2628062d06d","/opt/media/Images/Default.jpg","Default.jpg",0,"image/jpeg",632118,3023047,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-a19569ad296e9655d1fbf216f195f801.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,720,280,"2011:10:20 18:41:26",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("84b3a64a-51ef-4b3a-bbaa-c527fbbcfa42","/opt/media/Images/image1.jpg","image1.jpg",0,"image/jpeg",751750,3023268,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-f5052c8428c4a22231d6ece0c63b74bd.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:08 15:59:47",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("51d282b7-06d7-4bce-aebc-59e46b15f7e7","/opt/media/Images/image13.jpg","image13.jpg",0,"image/jpeg",549310,3023473,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-825ded447a3ce04d14d737f93d7cee26.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:07 14:59:11",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("dd6d7c0b-273d-47f5-8a37-30ebac9ac3a3","/opt/media/Images/image4.jpg","image4.jpg",0,"image/jpeg",609139,3023702,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-8ea059905f24eea065a7998dc5ff1f7e.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"                               ",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:07 14:44:45",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("21141e5d-e6da-45e2-93d6-5fb5c5870adb","/opt/media/Images/image2.jpg","image2.jpg",0,"image/jpeg",254304,3023930,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-93d14e2e94dfbccc9f38a14c4be6a780.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:08 14:54:05",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("2ec6f64b-c982-4c6a-9a70-1323d27f4aa5","/opt/media/Images/image9.jpg","image9.jpg",0,"image/jpeg",1168466,3024130,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-e82b0d23bfecbddaad1b98be7674b96e.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2011:10:20 18:43:39",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("db1c184c-6f31-43b4-b924-8c00ac5b6197","/opt/media/Images/Home_default.jpg","Home_default.jpg",0,"image/jpeg",554116,3024507,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-66784c0b912f077f0a8de56a2f56161e.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,720,1280,"2012:02:07 14:44:33",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("1b25f4d9-ffff-4b83-8dbf-187a0a809985","/opt/media/Images/image15.jpg","image15.jpg",0,"image/jpeg",484926,3024713,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-de79768105a730492b3b28ca33ff89f4.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:07 15:00:59",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("b3ee9659-22bb-423d-99d0-ed35240545a8","/opt/media/Images/image12.jpg","image12.jpg",0,"image/jpeg",519167,3024908,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-e32fd6fd44abe296c14de2407bab1f93.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:07 14:50:16",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("0d905e54-4583-4de8-80c1-ee4117e06ddf","/opt/media/Images/image11.jpg","image11.jpg",0,"image/jpeg",656364,3025097,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-773fffb8f086e5954f15407b41c2635d.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,720,1280,"2012:02:07 14:49:37",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("bc1eae57-376e-4ff3-b6a0-edcff8c7a1b1","/opt/media/Images/image5.jpg","image5.jpg",0,"image/jpeg",773064,3025291,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-c468b6d8820bfc0d9311d76f6575251a.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:07 14:45:14",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("eec305ed-ccb4-4abb-93f9-f087c823b1d4","/opt/media/Images/image6.jpg","image6.jpg",0,"image/jpeg",682883,3025500,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-10555c13cdfe5a763a69e08489de3c70.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2011:10:20 18:39:26",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("53101826-d64e-4d26-b448-acc1d94511a5","/opt/media/Images/image14.jpg","image14.jpg",0,"image/jpeg",452386,3025742,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-6f7e6adae30603c45be7db083610d0a3.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:07 14:59:44",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("dbf546ed-e984-45de-a85e-b1d750005036","/opt/media/Images/image8.jpg","image8.jpg",0,"image/jpeg",930876,3026032,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-5876701a15ec16bd0226ed00044cad92.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2011:10:21 10:01:44",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("696835a1-eaec-4602-8310-5e7ad9f4429b","/opt/media/Images/image10.jpg","image10.jpg",0,"image/jpeg",1236980,3027125,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-70a952ceff9175115b8c3fd044cdf978.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2011:10:20 18:43:24",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("4a76c208-ca95-4b2f-9de1-86c82a45506d","/opt/media/Images/image16.jpg","image16.jpg",0,"image/jpeg",1443416,3027413,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-aa5afe63b8aaa41079f9f37297d0763f.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,720,1280,"2011:10:20 18:42:06",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("83b9fd32-cd53-4ba7-84b8-c3d507f4701d","/opt/media/Images/image7.jpg","image7.jpg",0,"image/jpeg",1073428,3027698,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-fc4557b53139ca8f35a3f13cea24ed13.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,720,1280,"2011:10:20 18:41:51",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO media VALUES("a2b3cbf8-82e3-456f-b912-74b0a646da6e","/opt/media/Images/image3.jpg","image3.jpg",0,"image/jpeg",738597,3027977,1337008628,"baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/data/file-manager-service/.thumb/phone/.jpg-03bdfd7e4d43c736819639b84a590b5f.jpg",NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,"No description",0,0,0,0,1000.0,1000.0,0.0,1280,720,"2012:02:07 14:46:13",1,0,0,0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1);
	INSERT INTO folder VALUES("baeb79e5-a9da-4667-aeaf-6b98830e4ce8","/opt/media/Images","Images",1337008628,0);
'
fi
#change permission
chmod 664 /opt/dbspace/.media.db
chmod 664 /opt/dbspace/.media.db-journal
chmod 775 /opt/data/file-manager-service
chmod 775 /opt/data/file-manager-service/.thumb
chmod 775 /opt/data/file-manager-service/.thumb/phone
chmod 775 /opt/data/file-manager-service/.thumb/mmc

#change owner
chown -R 5000:5000 /opt/media/*

#change group (6017: db_filemanager 5000: app)
chgrp 5000 /opt/dbspace
chgrp 6017 /opt/dbspace/.media.db
chgrp 6017 /opt/dbspace/.media.db-journal
chgrp 5000 /opt/data/file-manager-service/
chgrp 5000 /opt/data/file-manager-service/.thumb
chgrp 5000 /opt/data/file-manager-service/.thumb/phone
chgrp 5000 /opt/data/file-manager-service/.thumb/phone/.[a-z0-9]*.*
chgrp 5000 /opt/data/file-manager-service/.thumb/mmc

##delete unusing files
rm /opt/media/Downloads/.gitignore
rm /opt/media/Videos/.gitignore
rm /opt/media/Camera/.gitignore
rm /opt/media/Sounds/Voice\ recorder/.gitignore
rm /opt/media/Sounds/FM\ radio/.gitignore

%files
%defattr(-,root,root,-)
%{_optdir}/data/file-manager-service/plugin-config
%{_optdir}/data/file-manager-service/.thumb/*
%{_optdir}/media/*

%changelog
* Wed Jun 27 2012 Yong Yeon Kim <yy9875.kim@samsung.com> - 0.1.24
- delete default files for settings

