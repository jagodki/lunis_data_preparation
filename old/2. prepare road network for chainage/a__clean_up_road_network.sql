--enable topology-extension of postgis
CREATE EXTENSION postgis_topology;

--create the topology on the roads-table
SELECT topology.CreateTopology('roads_topo', 25833, 0.5);
SELECT topology.AddTopoGeometryColumn('roads_topo', 'roads', 'roads_single_geom', 'topo_geom', 'LINESTRING');

--update the topo-geometry
UPDATE roads.roads_single_geom SET topo_geom = topology.toTopoGeom(ST_Transform(geom, 25833), 'roads_topo', 1, 0.5);
