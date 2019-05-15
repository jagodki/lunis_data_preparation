alter table grid_preparation.grid
add column grid_values double precision ARRAY;

update grid_preparation.grid
set grid_values = ARRAY[school_id_1, school_id_2, school_id_3, school_id_4, school_id_5, school_id_6, school_id_7, school_id_8, school_id_9, school_id_10, school_id_11, school_id_12, school_id_13, school_id_14, school_id_15];
