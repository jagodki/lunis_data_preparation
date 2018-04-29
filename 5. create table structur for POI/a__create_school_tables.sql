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
	last_update TIMESTAMP,
	source CHARACTER VARYING
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
CREATE VIEW addresses.adresses_view AS
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
CREATE TABLE schools.agency(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING
);
CREATE TABLE schools.schools(
	id SERIAL PRIMARY KEY,
	name CHARACTER VARYING,
	administration_id INTEGER REFERENCES administration.city(id),
	address INTEGER REFERENCES addresses.housenumber(id),
	agency_id INTEGER REFERENCES schools.agency(id),
	school_type INTEGER REFERENCES schools.school_type(id),
	website CHARACTER VARYING,
	wikipedia CHARACTER VARYING,
	mail CHARACTER VARYING,
	telefon CHARACTER VARYING
);
CREATE TABLE schools.specialisation_schools_join(
	id SERIAL PRIMARY KEY,
	school_id INTEGER REFERENCES schools.schools(id),
	specialisation_id INTEGER REFERENCES schools.specialisation(id)
);

SELECT addGeometryColumn('schools', 'schools', 'geom', 4326, 'POINT', 2);

----------------------------------------
--create a new schema called 'lunis'
CREATE SCHEMA lunis;

--create depending views in schema 'lunis'
CREATE VIEW lunis.administration_views AS
	SELECT ci.id AS id, ci.name AS city, r.name AS region, co.name AS country, ci.source AS source, ci.last_update AS last_update, ci.geom AS geom
	FROM administration.country co, administration.region r, administration.city ci
	WHERE co.id = r.country_id AND r.id = ci.region_id;
	
CREATE VIEW lunis.schools_view AS
	SELECT s_s.id, s_s.name, (admin_ci.name || '/' || admin_r.name || '/' || admin_co.name) AS district,
		   (add_s.name || ' ' || add_h.number || ', ' || add_p.code || ' ' || add_ci.name || ', ' || add_co.name) AS school_address, 
		   s_a.name AS agency, s_t.name AS school_type, string_agg(s_spec.name, ', ' ORDER BY s_spec.name) AS school_specialisations, s_s.website AS website, s_s.wikipedia AS wikipedia,
		   s_s.mail AS mail, s_s.telefon AS telefon, s_s.geom AS geom
	FROM schools.schools s_s, schools.school_type s_t, schools.specialisation s_spec, schools.specialisation_schools_join s_s_j, schools.agency s_a,
		 administration.country admin_co, administration.region admin_r, administration.city admin_ci,
		 addresses.housenumber add_h, addresses.street add_s, addresses.postal_code add_p, addresses.city add_ci, addresses.country add_co
	WHERE s_s.school_type = s_t.id AND s_s.id = s_s_j.school_id AND s_spec.id = s_s_j.specialisation_id AND s_a.id = s_s.agency_id AND
		  s_s.administration_id = admin_ci.id AND admin_ci.region_id = admin_r.id AND admin_r.country_id = admin_co.id AND
		  s_s.address = add_h.id AND add_h.street_id = add_s.id AND add_s.postal_code_id = add_p.id AND
		  add_p.city_id = add_ci.id AND add_ci.country_id = add_co.id
	GROUP BY s_s.id, district, school_address, s_a.name, s_t.name, s_s.website, s_s.wikipedia, s_s.mail, s_s.telefon, s_s.geom;