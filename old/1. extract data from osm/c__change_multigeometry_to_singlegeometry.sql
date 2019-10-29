--create a new table to store the roads as single geometries
CREATE TABLE roads.roads_single_geom (
	id SERIAL PRIMARY KEY,
	old_id CHARACTER VARYING,
	classification CHARACTER VARYING
);

--create a new single geometry column
SELECT AddGeometryColumn('roads', 'roads_single_geom', 'geom', 4326, 'LINESTRING', 2);

--change the multilinestrings into linestrings
INSERT INTO roads.roads_single_geom (old_id, classification, geom)
SELECT id, highway, (ST_Dump(geom)).geom FROM roads.roads;
