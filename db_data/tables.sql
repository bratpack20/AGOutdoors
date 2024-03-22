use agoutdoors;


CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    username BLOB,
    password BLOB,
    PRIMARY KEY (user_id)
);


CREATE TABLE gallery_entry (
    id INT NOT NULL AUTO_INCREMENT,
    position int,
    image_name VARCHAR(1000),
    description VARCHAR(5000),
    PRIMARY KEY (id)
);