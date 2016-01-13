-- Construct tables

-- TABLE: equipment
CREATE TABLE equipment (
    equipment_id int  NOT NULL,
    equipment_type int  NOT NULL,
    location integer ARRAY[3]
    -- CONSTRAINT equipment_pk PRIMARY KEY (equipment_id)
);

