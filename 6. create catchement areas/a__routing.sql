--enable pgrouting
CREATE EXTENSION pgrouting;

--create catchment area from all road nodes to each POI
DO $BODY$
DECLARE
	i RECORD;
BEGIN
    FOR i IN
    SELECT a.id AS node_id, b.id AS school_id
    FROM pgchainage.roads_rdbl_chainage a, lunis.schools b
    ORDER BY ST_Distance(a.geom, ST_Transform(b.geom, 25833)) asc
    LIMIT 1
    LOOP
		EXECUTE
        	'UPDATE pgchainage.roads_rdbl_chainage c ' ||
            'SET school_id_' || i.school_id || '= foo2.cost ' ||
            'FROM (' ||
            'SELECT id, (SELECT SUM(cost) FROM (SELECT * FROM pgr_dijkstra(''' ||
            'SELECT id, start_id AS source, end_id AS target, cost FROM pgchainage.roads_rdbl_substring'', ' ||
            i.node_id || ', id, FALSE)) AS foo) AS cost ' ||
            'from pgchainage.roads_rdbl_chainage) foo2 ' ||
            'WHERE c.id = foo2.id;';
       END LOOP;
END
$BODY$