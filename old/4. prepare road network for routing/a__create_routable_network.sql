--add columns to store mandatory information for routing, i.e. IDs of the start and end nodes
ALTER TABLE pgchainage.edge_data_substring
ADD COLUMN start_id integer,
ADD COLUMN end_id integer,
ADD COLUMN cost double precision;

--create spatial index over nodes to improve speed of the following query
CREATE INDEX edge_data_chainage_gix ON pgchainage.edge_data_chainage 
USING GIST (geom);

--fill in the new columns
WITH startnodes AS (
		SELECT c.id, s.id AS edge_id
		FROM pgchainage.edge_data_chainage c, pgchainage.edge_data_substring s
		WHERE ST_Intersects(c.geom, ST_StartPoint(s.geom))
	), endnodes AS (
		SELECT c.id, s.id AS edge_id
		FROM pgchainage.edge_data_chainage c, pgchainage.edge_data_substring s
		WHERE ST_Intersects(c.geom, ST_EndPoint(s.geom))
	)
UPDATE pgchainage.edge_data_substring r
SET start_id = s.id, end_id = e.id, cost = ST_Length(r.geom)
FROM startnodes s, endnodes e
WHERE r.id = s.edge_id AND r.id = e.edge_id;

--check, whether datasets have null-values in the columns start_id, end_id, cost (mandatory for routing)
SELECT *
FROM pgchainage.edge_data_substring
WHERE start_id IS NULL OR end_id IS NULL OR cost IS NULL;

--create indices on start_id and end_id for faster routing
CREATE INDEX IF NOT EXISTS edge_data_substring_start_idx ON pgchainage.edge_data_substring (start_id);
CREATE INDEX IF NOT EXISTS edge_data_substring_end_idx ON pgchainage.edge_data_substring (end_id);