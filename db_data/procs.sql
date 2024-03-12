use agoutdoors;

DROP PROCEDURE IF EXISTS insert_into_db;

DELIMITER //
CREATE PROCEDURE insert_into_db (
    IN table_name VARCHAR(200),
    IN columns_list VARCHAR(5000),
    IN input_values VARCHAR(5000)
)
BEGIN
    SET @sql = CONCAT("INSERT INTO ", table_name, " (", columns_list, ") VALUES (", input_values, ");");
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS select_all

DELIMITER //

CREATE PROCEDURE select_all (
    IN table_name VARCHAR(200)
)
BEGIN
    SET @sql = CONCAT('SELECT * FROM ', table_name, ';');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;