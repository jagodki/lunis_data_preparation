--create two new columns
alter table grid_preparation.grid
add column cell_values double precision ARRAY;

alter table grid_preparation.grid
add column school_ids character varying ARRAY;

--update the new columns
update grid_preparation.grid
set cell_values = ARRAY[school_id_1, school_id_2, school_id_3, school_id_4, school_id_5, school_id_6, school_id_7, school_id_8, school_id_9, school_id_10, school_id_11, school_id_12, school_id_13, school_id_14, school_id_15];

update grid_preparation.grid
set school_ids = ARRAY['school_id_1', 'school_id_2', 'school_id_3', 'school_id_4', 'school_id_5', 'school_id_6', 'school_id_7', 'school_id_8', 'school_id_9', 'school_id_10', 'school_id_11', 'school_id_12', 'school_id_13', 'school_id_14', 'school_id_15'];

--create a GeoJSON output
SELECT jsonb_build_object(
    'type', 'FeatureCollection',
    'name', 'grid',
    'crs', 4326,
    'features', jsonb_agg(features.feature)
)
FROM (
	SELECT jsonb_build_object(
		'type', 'Feature',
		'id', id,
		'geometry', ST_AsGeoJSON(geom)::jsonb,
		'properties', to_jsonb(inputs) - 'id' - 'geom'
	) AS feature
	FROM (
		SELECT id, st_transform(geom, 4326) as geom, cell_values, school_ids
		FROM grid_preparation.grid
	) inputs
) features;