--enable topology-extension of postgis
CREATE EXTENSION postgis_topology;

--create the topology on the roads-table
SELECT topology.CreateTopology('roads_rdbl_topo', 25833);
SELECT topology.AddTopoGeometryColumn('roads_rdbl_topo', 'temp', 'roads_rdbl_final', 'topo_geom', 'LINESTRING');

--update the topo-geometry
UPDATE temp.roads_rdbl_final SET topo_geom = topology.toTopoGeom(ST_Transform(geom, 25833), 'roads_rdbl_topo', 1, 0.5);
