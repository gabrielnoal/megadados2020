DROP TABLE IF EXISTS user;
CREATE TABLE user (
    user_uuid BINARY(16) PRIMARY KEY,
    name NVARCHAR(1024)
);

ALTER TABLE tasks
    ADD user_uuid BINARY(16) DEFAULT NULL,
    ADD CONSTRAINT
      FOREIGN KEY (user_uuid) REFERENCES user(user_uuid);
