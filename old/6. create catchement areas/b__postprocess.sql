--replace null values with a maximum distance
DO $BODY$
DECLARE
	i RECORD;
BEGIN
    FOR i IN
		SELECT id AS school_id
    	FROM schools.schools
    LOOP
		EXECUTE
        	'UPDATE pgchainage.edge_data_chainage c ' ||
            'SET school_id_' || i.school_id || ' = ' || 999999999.99 ||
            'WHERE school_id_' || i.school_id || ' is NULL;';
    END LOOP;
END
$BODY$

--add an additional geometry column with EPSG:4326
SELECT AddGeometryColumn('pgchainage', 'edge_data_chainage', 'geom_wgs', 4326, 'POINT', 2);
UPDATE pgchainage.edge_data_chainage
SET geom_wgs = ST_Transform(geom, 4326);