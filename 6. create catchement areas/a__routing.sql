--enable pgrouting
CREATE EXTENSION pgrouting;

--create catchment area from all road nodes to each POI
DO $BODY$
DECLARE
	i RECORD;
BEGIN
    FOR i IN
		SELECT DISTINCT ON (b.id) a.id AS node_id, b.id AS school_id, MIN(ST_Distance(ST_Transform(b.geom, 25833), a.geom)) AS distance
    	FROM pgchainage.edge_data_chainage a, schools.schools b
    	GROUP BY a.id, b.id
		ORDER BY b.id, ST_Distance(ST_Transform(b.geom, 25833), a.geom) ASC
    LOOP
		EXECUTE
        	'UPDATE pgchainage.edge_data_chainage c ' ||
            'SET school_id_' || i.school_id || '= foo2.cost ' ||
            'FROM (' ||
            'SELECT id, (SELECT SUM(cost) FROM (SELECT * FROM pgr_dijkstra(''' ||
            'SELECT id, start_id AS source, end_id AS target, cost FROM pgchainage.edge_data_substring'', ' ||
            i.node_id || ', id, FALSE)) AS foo) AS cost ' ||
            'from pgchainage.edge_data_chainage) foo2 ' ||
            'WHERE c.id = foo2.id;';
        EXECUTE
        	'UPDATE pgchainage.edge_data_chainage c ' ||
        	'SET school_id_' || i.school_id || '= 0.0' ||
        	'WHERE c.id = ' || i.node_id || ';';
    END LOOP;
END
$BODY$
