SELECT *
FROM shortest_path(
	'SELECT edge_id AS id,
				  start_id::int4 AS source,
				  end_id::int4 AS target,
				  ST_Length(geom)::double precision AS cost
    FROM roads.roads_rdbl',
	325,
	719,
	false,
	false
);