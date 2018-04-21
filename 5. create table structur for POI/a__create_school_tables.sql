--create a new schema called 'lunis'
CREATE SCHEMA lunis;

----------------------------------------
--create administration schema and depending tables
CREATE SCHEMA administration;
CREATE TABLE administration.country(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING
);
CREATE TABLE administration.region(
	id SERIAL PRIMARY KEY,
	country_id INTEGER REFERENCES administration.country(id),
	name CHARACTER VARYING
);
CREATE TABLE administration.city(
	id SERIAL PRIMARY KEY,
	region_id INTEGER REFERENCES administration.region(id),
	name CHARACTER VARYING,
	last_update TIMESTAMP
);

--add a geometry column to the city table
SELECT addGeometryColumn('administration', 'city', 'geom', 4326, 'POLYGON', 2);

----------------------------------------
--create address schema and depending tables
CREATE SCHEMA addresses;
CREATE TABLE addresses.country(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING
);
CREATE TABLE addresses.city(
	id SERIAL PRIMARY KEY,
	country_id INTEGER REFERENCES addresses.country(id),
	name CHARACTER VARYING
);
CREATE TABLE addresses.postal_code(
	id SERIAL PRIMARY KEY,
	city_id INTEGER REFERENCES addresses.city(id),
	code CHARACTER VARYING
);
CREATE TABLE addresses.street(
	id SERIAL PRIMARY KEY,
	postal_code_id INTEGER REFERENCES addresses.postal_code(id),
	name CHARACTER VARYING
);
CREATE TABLE addresses.housenumber(
	id SERIAL PRIMARY KEY,
	street_id INTEGER REFERENCES addresses.street(id),
	number CHARACTER VARYING
);
CREATE VIEW adresses.adresses_view AS
	SELECT h.id AS id, co.name AS country, ci.name AS city, p.code AS postal_code, s.name AS street, h.number AS housenumber
	FROM addresses.country co, addresses.city ci, addresses.postal_code p, addresses.street s, addresses.housenumber h
	WHERE h.street_id = s.id AND s.postal_code_id = p.id AND p.city_id = ci.id AND ci.country_id = co.id;

----------------------------------------
--create schools schema and depending tables
CREATE SCHEMA schools;
CREATE TABLE schools.school_type(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING
);
CREATE TABLE schools.specialisation(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING
);
CREATE TABLE schools.schools(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING,
	administration_id INTEGER REFERENCES administration.city(id),
	address INTEGER REFERENCES addresses.housenumber(id),
	school_type INTEGER REFERENCES schools.school_type(id),
	specialisation INTEGER REFERENCES lunis.specialisation(id),
	website CHARACTER VARYING,
	wikipedia CHARACTER VARYING,
	mail CHARACTER VARYING,
	telefon CHARACTER VARYING,
	source CHARACTER VARYING
);

SELECT addGeometryColumn('schools', 'schools', 'geom', 4326, 'POINT', 2);

----------------------------------------
--create lunis schema and depending views
CREATE VIEW lunis.administration_views AS
	SELECT ci.id AS id, ci.name AS city, r.name AS region, co.name AS country, ci.last_update AS last_update, ci.geom AS geom
	FROM administration.country co, administration.region r, administration.city ci
	WHERE co.id = r.country_id AND r.id = ci.region_id;
CREATE VIEW lunis.schools_view AS
	SELECT s_s.id, s_s.name, (admin_ci.name || '/' || admin_r.name || '/' || admin_co.name) AS district,
		   (add_s.name || ' ' || add_h.number || ', ' add_p.code || ' ' || add_ci.name || ', ' add_ci.name) AS address
		   s_t.name AS school_type, s_spec.name AS specialisations, s_s.geom AS geom
	FROM schools.schools s_s, schools.school_type s_t, schools.specialisation s_spec,
		 administration.country admin_co, administration.region admin_r, administration.city admin_ci,
		 addresses.housenumber add_h, addresses.street add_s, addresses.postal_code add_p, addresses.city add_ci, addresses.country add_co
	WHERE s.admin_id = a.id AND s.school_type = t.id AND s.specialisation = spec.id;