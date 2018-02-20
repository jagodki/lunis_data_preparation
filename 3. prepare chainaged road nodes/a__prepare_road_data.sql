--add additional columns to the table of the chainaged road network
ALTER TABLE roads.road_nodes_rdbl
ADD COLUMN neighbours CHARACTER VARYING[][],
ADD COLUMN nearest_neighbour INTEGER,
ADD COLUMN cumulated_distance DOUBLE PRECISION;
