--enable pgrouting
CREATE EXTENSION pgrouting;

--create catchment area
create table pgchainage.catchment_905 as
select
    id,
    geom,
    (select sum(cost) from (
       SELECT * FROM pgr_dijkstra('
       SELECT id,
          start_id AS source,
          end_id AS target,
          cost
       FROM pgchainage.roads_rdbl_substring',
       905,
       id,
	   false)) as foo ) as cost
from pgchainage.roads_rdbl_chainage;

--create catchment area from all road nodes to each POI
DO $BODY$
DECLARE
	i RECORD;
BEGIN
       FOR i IN SELECT id, geom FROM lunis.schools LOOP
               EXECUTE
                       'UPDATE pgchainage.pgchainage.roads_rdbl_chainage c' ||
                       'SET school_id_' || i.id || '= foo2.cost' ||
                       'FROM (' ||
                       'SELECT id, (SELECT SUM(cost) FROM (SELECT * FROM pgr_dijkstra(''' ||
                       'SELECT id, start_id AS source, end_id AS target, cost FROM pgchainage.roads_rdbl_substring'',' ||
                       'geom, id, FALSE)) AS foo) AS cost' ||
                       'from pgchainage.roads_rdbl_chainage) foo2' ||
                       'WHERE c.id = foo.id;';
       END LOOP;
END
$BODY$