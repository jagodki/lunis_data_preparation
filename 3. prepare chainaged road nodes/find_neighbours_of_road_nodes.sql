DO $$
	DECLARE
		equidistance CHARACTER VARYING := '100';
        line_id CHARACTER VARYING := 'id';
        point_id CHARACTER VARYING := 'id';
		predecessor INTEGER := NULL;
        i record;
        j record;
        k record;
	BEGIN
		--iterate through the IDs of all lines of the road network
        [ <<first_loop>> ]
		FOR i IN SELECT line_id FROM roads.roads_rdbl LOOP
			
			--iterate through all nodes on the current line in ASCENDING order of its number on line
			[ <<second_loop>> ]
            FOR j IN SELECT * FROM roads.road_nodes_rdbl WHERE old_id = i.line_id ORDER BY number_on_line ASC LOOP
				
				--if no predecessor is set, than it is the first node on the current line
				IF equidistance != NULL
				THEN UPDATE roads.road_nodes_rdbl SET neighbours = neighbours || '{{predecessor::CHARACTER VARYING, equidistance}}' WHERE point_id = j.point_id;
				
				--save the ID of the current dataset as predecessor of the next loop
				predecessor := j.point_id;
				
			END LOOP [ second_loop ];
			
			--iterate through all nodes on the current line in DESCENDING order of its number on line
			predecessor := NULL;
            [ <<third_loop>> ]
			FOR k IN SELECT * FROM roads.road_nodes_rdbl WHERE old_id = i.line_id ORDER BY number_on_line DESC LOOP
				
				--if no predecessor is set, than it is the first node on the current line
				IF equidistance != NULL
				THEN UPDATE roads.road_nodes_rdbl SET neighbours = neighbours || '{{predecessor::CHARACTER VARYING, equidistance}}' WHERE point_id = j.point_id;
				
				--save the ID of the current dataset as predecessor of the next loop
				predecessor := j.point_id;
				
			END LOOP [ third_loop ];
			
		END LOOP [ first_loop ];
END $$
