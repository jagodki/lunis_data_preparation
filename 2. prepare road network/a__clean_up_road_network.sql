--enable topology-extension of postgis
CREATE EXTENSION postgis_topology;

--create the topology on the roads-table
SELECT topology.CreateTopology('roads_rdbl_topo', 25833);
SELECT topology.AddTopoGeometryColumn('roads_rdbl_topo', 'temp', 'roads_rdbl_final', 'topo_geom', 'LINESTRING');

--update the topo-geometry
UPDATE temp.roads_rdbl_final SET topo_geom = topology.toTopoGeom(ST_Transform(geom, 25833), 'roads_rdbl_topo', 1, 0.5);

--join the cleaned up road network with the attributes of the source layer
SELECT e.edge_id, r.type, e.geom
INTO roads.roads_rdbl
FROM roads_rdbl_topo.edge e,
     roads_rdbl_topo.relation rel,
     temp.roads_rdbl_final r
WHERE e.edge_id = rel.element_id
AND rel.topogeo_id = (r.topo_geom).id;

--make the new road relation routable
SELECT a.*, b.start_node AS start_id, b.end_node AS end_id, c.geom AS startpoint, d.geom AS endpoint
FROM roads.roads_rdbl AS a, roads_rdbl_topo.edge_data AS b, roads_rdbl_topo.node AS c, roads_rdbl_topo.node AS d
WHERE a.edge_id = b.edge_id
AND b.start_node = c.node_id
AND b.end_node = d.node_id;