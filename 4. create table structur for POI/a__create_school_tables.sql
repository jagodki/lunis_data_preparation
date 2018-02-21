--create a new schema called 'lunis'
CREATE SCHEMA lunis;

--create administration table
CREATE TABLE lunis.administration(
	id SERIAL PRIMARY KEY,
	country CHARACTER VARYING,
	region CHARACTER VARYING,
	city CHARACTER VARYING,
	last_update TIMESTAMP
);

--add a geometry column to the adminstration table
SELECT addGeometryColumn('lunis', 'administration', 'geom', 4326, 'POLYGON', 2);

--create table 'school_type'
CREATE TABLE lunis.school_type(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING
);

--create table 'specialisation'
CREATE TABLE lunis.specialisation(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING
);

--create schools table
CREATE TABLE lunis.schools(
	id SERIAL PRIMARY KEY,
	admin_id INTEGER REFERENCES lunis.administration(id) ON UPDATE CASCADE ON DELETE CASCADE,
	school_type INTEGER REFERENCES lunis.school_type(id) ON UPDATE CASCADE,
	specialisation INTEGER REFERENCES lunis.specialisation(id) ON UPDATE CASCADE,
	website CHARACTER VARYING,
	wikipedia CHARACTER VARYING,
	mail CHARACTER VARYING,
	telefon CHARACTER VARYING,
	source CHARACTER VARYING
);

--add a geometry column to the school table
SELECT addGeometryColumn('lunis', 'schools', 'geom', 4326, 'POINT', 2);

--create a view of schools
CREATE VIEW schools_view AS
	SELECT s.id, (a.city || '/' || a.region || '/' || a.country) as district, t.name AS school_type, spec.name AS sepcialisations
	FROM lunis.schools s, lunis.administration a, lunis.school_type t, lunis.specialisation spec
	WHERE s.admin_id = a.id and s.school_type = t.id and s.specialisation = spec.id
;