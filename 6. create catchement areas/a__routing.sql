CREATE EXTENSION pgrouting;

select * from roads.roads_rdbl a
inner join (
SELECT *
FROM pgr_dijkstra(
	'SELECT edge_id AS id,
				  start_id::int4 AS source,
				  end_id::int4 AS target,
				  ST_Length(geom)::double precision AS cost
    FROM roads.roads_rdbl',
	325,
	719,
	false
)) as route on a.edge_id = route.edge;

create table pgchainage.catchment_905 as
select
    id,
    the_geom,
    (select sum(cost) from (
       SELECT * FROM shortest_path('
       SELECT id,
          start_id AS source,
          end_id AS target,
          cost
       FROM network',
       905,
       id,
       false,
       false)) as foo ) as cost
from pgchainage.roads_rdbl_chainage;