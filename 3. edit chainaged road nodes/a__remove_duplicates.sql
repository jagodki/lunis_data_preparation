WITH startpoints_to_keep AS (
		SELECT a.edge_id, MIN(b.id) AS node_id, COUNT(a.edge_id) AS count_start
		FROM roads.roads_rdbl a
		INNER JOIN chainage.roads_rdbl_chainage b
		ON st_intersects(ST_Startpoint(a.geom), b.geom)
		GROUP BY a.edge_id
	), endpoints_to_keep AS (
		SELECT a.edge_id, MIN(b.id) AS node_id, COUNT(a.edge_id) AS count_end
		FROM roads.roads_rdbl a
		INNER JOIN chainage.roads_rdbl_chainage b
		ON st_intersects(ST_Endpoint(a.geom), b.geom)
		GROUP BY a.edge_id
    ), points_in_the_middle_of_their_line AS (
    	SELECT a.id AS node_id, b.edge_id
    	FROM chainage.roads_rdbl_chainage a
    	INNER JOIN roads.roads_rdbl b
    	ON a.old_id = b.edge_id AND NOT ST_Touches(b.geom, a.geom)
    )
DELETE FROM chainage.roads_rdbl_chainage
WHERE id NOT IN (SELECT node_id FROM startpoints_to_keep)
AND id NOT IN (SELECT node_id FROM endpoints_to_keep)
AND id NOT IN (SELECT node_id FROM points_in_the_middle_of_their_line);