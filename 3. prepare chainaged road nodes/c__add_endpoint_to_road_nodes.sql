WITH roads_temp AS (
		SELECT edge_id, ST_Endpoint(geom) AS endpoint
		FROM roads.roads_rdbl
	),	nodes_temp AS (
		SELECT old_id, MAX(number_on_line) AS max_number_on_line
		FROM chainage.roads_rdbl_chainage
		GROUP BY old_id
	)
INSERT INTO chainage.roads_rdbl_chainage(
	old_id,
	geom,
	number_on_line
)
SELECT r.edge_id, r.endpoint, (n.max_number_on_line + 1)
FROM roads_temp r, nodes_temp n
WHERE r.edge_id = n.old_id;