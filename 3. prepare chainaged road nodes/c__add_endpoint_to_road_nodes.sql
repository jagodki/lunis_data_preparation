WITH roads_temp AS (SELECT edge_id, ST_NPoints(geom) AS count_vertices, ST_Endpoint(geom) AS endpoint FROM roads.roads_rdbl)
INSERT INTO roads.road_nodes_rdbl(old_id, geom, number_on_line)
SELECT edge_id, endpoint, (count_vertices + 1) FROM roads_temp;