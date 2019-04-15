ALTER TABLE grid_preparation.grid
ADD COLUMN school_id_1 DOUBLE PRECISION;

WITH regular_points_with_values AS (
SELECT a.id, ((b.school_id_1_max + b.school_id_1_min) / 2) AS distance_value, a.geom
FROM grid_preparation.regular_points a, grid_preparation.filled_contours b
WHERE st_intersects(a.geom, b.geom)
),
grid_with_null_values AS (
SELECT a.id, avg(b.distance_value) AS distance_value
FROM grid_preparation.grid a
LEFT JOIN regular_points_with_values b
ON st_intersects(a.geom, b.geom)
GROUP BY a.id
)
UPDATE grid_preparation.grid a
SET school_id_1 = b.distance_value
FROM grid_with_null_values b
WHERE a.id = b.id;

UPDATE grid_preparation.grid
SET school_id_1 = -99
WHERE school_id_1 IS NULL;