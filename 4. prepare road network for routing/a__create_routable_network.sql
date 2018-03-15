--add columns to store mandatory information for routing
ALTER TABLE pgchainage.roads_rdbl_substring
ADD COLUMN  start_id integer,
ADD COLUMN end_id integer,
ADD COLUMN cost double precision;

--fill the new columns
WITH startnodes AS (
		SELECT c.id, s.id AS edge_id
		FROM pgchainage.roads_rdbl_chainage c, pgchainage.roads_rdbl_substring s
		WHERE ST_Intersects(c.geom, ST_StartPoint(s.geom))
	), endnodes AS (
		SELECT c.id, s.id AS edge_id
		FROM pgchainage.roads_rdbl_chainage c, pgchainage.roads_rdbl_substring s
		WHERE ST_Intersects(c.geom, ST_EndPoint(s.geom))
	)
UPDATE pgchainage.roads_rdbl_substring r
SET start_id = s.id, end_id = e.id, cost = ST_Length(geom)
FROM startnodes s, endnodes e
WHERE r.id = s.edge_id AND r.id = e.edge_id;

--check, whether datasets have null-values in the columns start_id, end_id, cost (mandatory for routing)
SELECT *
FROM pgchainage.roads_rdbl_substring
WHERE start_id IS NULL OR end_id IS NULL OR cost IS NULL;