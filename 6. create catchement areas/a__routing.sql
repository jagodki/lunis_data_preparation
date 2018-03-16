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