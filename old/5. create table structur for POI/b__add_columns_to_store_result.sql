--add columns dynamically to the road nodes for storing the distances to each POI
DO $BODY$
DECLARE
	i RECORD;
BEGIN
       FOR i IN SELECT id FROM schools.schools LOOP
               EXECUTE 'ALTER TABLE pgchainage.edge_data_chainage ADD COLUMN school_id_' || i.id || ' double precision;';
       END LOOP;
END
$BODY$
