use agoutdoors;


CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    username BLOB,
    password BLOB,
    PRIMARY KEY (user_id)
);