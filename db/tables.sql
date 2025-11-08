use lingoDB;
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
	name VARCHAR(120), 
	email VARCHAR(120), 
	phone VARCHAR(50), 
	create_date DATETIME NOT NULL, 
	update_date DATETIME NOT NULL
);

CREATE TABLE subject_category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    description VARCHAR(256)
);
INSERT INTO subject_category VALUES(1,'language','human languages and linguistics');
INSERT INTO subject_category VALUES(2,'programming','computer programming and software development');
INSERT INTO subject_category VALUES(3,'mathematics','mathematical concepts and theories');
INSERT INTO subject_category VALUES(4,'science','natural and physical sciences');
INSERT INTO subject_category VALUES(5,'history','historical events and periods');
INSERT INTO subject_category VALUES(6,'art','visual and performing arts');

CREATE TABLE subject (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    category_id INTEGER,
    name VARCHAR(30) NOT NULL,
    description VARCHAR(128),
    FOREIGN KEY (category_id) REFERENCES subject_category(id)
);
INSERT INTO subject VALUES(1,'en',1,'English','The study of the English language and its literature.');
INSERT INTO subject VALUES(2,'es',1,'Spanish','The study of the Spanish language and its literature.');
INSERT INTO subject VALUES(3,'ja',1,'Japanese','The study of the Japanese language and its literature.');
INSERT INTO subject VALUES(4,'fr',1,'French','The study of the French language and its literature.');
INSERT INTO subject VALUES(5,'de',1,'German','The study of the German language and its literature.');
INSERT INTO subject VALUES(6,'zh',1,'Chinese','The study of the Chinese language and its literature.');
INSERT INTO subject VALUES(7,'ru',1,'Russian','The study of the Russian language and its literature.');
INSERT INTO subject VALUES(8,'it',1,'Italian','The study of the Italian language and its literature.');
INSERT INTO subject VALUES(9,'pt',1,'Portuguese','The study of the Portuguese language and its literature.');

CREATE TABLE subject_translation (
	id INT AUTO_INCREMENT PRIMARY KEY,
	subject_id INT,
	name VARCHAR(30),
	description VARCHAR(128),
	FOREIGN KEY (subject_id) REFERENCES subject(id)
);

CREATE TABLE subject_level (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level INTEGER NOT NULL,
    subject_category_id INTEGER,
    name VARCHAR(30) NOT NULL,
    description VARCHAR(512),
    FOREIGN KEY (subject_category_id) REFERENCES subject_category(id)
);
INSERT INTO subject_level VALUES(1,1,1,'Novice Low','Communicates minimally with isolated words and memorized phrases. Often relies on gestures and repetition.');
INSERT INTO subject_level VALUES(2,2,1,'Novice Mid','Can produce simple phrases and respond to direct questions on familiar topics. Still limited to memorized language.');
INSERT INTO subject_level VALUES(3,3,1,'Novice High','Can handle short social interactions using learned phrases. May attempt to create language but with frequent errors.');
INSERT INTO subject_level VALUES(4,4,1,'Intermediate Low','Can express basic needs and preferences. Speech is halting and relies on memorized chunks.');
INSERT INTO subject_level VALUES(5,5,1,'Intermediate Mid','Can ask and answer questions, handle simple transactions, and describe in present tense. Speech is more fluid but limited to familiar contexts.');
INSERT INTO subject_level VALUES(6,6,1,'Intermediate High','Can participate in conversations on everyday topics. Begins to narrate and describe in past and future tenses with some control.');
INSERT INTO subject_level VALUES(7,7,1,'Advanced Low','Can narrate and describe across major time frames. Handles routine social and work situations with confidence.');
INSERT INTO subject_level VALUES(8,8,1,'Advanced Mid','Can elaborate on topics, support opinions, and manage complications in conversations. Shows good control of grammar and vocabulary.');
INSERT INTO subject_level VALUES(9,9,1,'Advanced High','Can handle complex tasks and unexpected situations. Language is accurate and nuanced, though not always native-like.');
INSERT INTO subject_level VALUES(10,10,1,'Superior','Can discuss abstract topics, hypothesize, and tailor language to different audiences. Demonstrates fluency, accuracy, and cultural appropriateness.');
INSERT INTO subject_level VALUES(11,11,1,'Distinguished','Can reflect on complex ideas, persuade, and negotiate in highly sophisticated ways. Language is precise, nuanced, and appropriate for any context.');

CREATE TABLE course (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INTEGER,
    subject_level_id INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subject(id),
    FOREIGN KEY (subject_level_id) REFERENCES subject_level(id)
);
CREATE TABLE user_course (
    user_id INTEGER,
    course_id INTEGER,
    primary_lang_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    enrollment_date DATE,
    completion_date DATE,
    PRIMARY KEY (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id)
);


CREATE TABLE topic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    subject_category_id INTEGER,
    FOREIGN KEY (subject_category_id) REFERENCES subject_category(id)
);
CREATE TABLE user_topic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INTEGER,
    course_id INTEGER,
    topic_id INTEGER,
    name VARCHAR(128),
    is_active BOOLEAN DEFAULT TRUE,
    exercise_count INTEGER DEFAULT 0,
    correct_percentage REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (topic_id) REFERENCES topic(id)
);
CREATE TABLE subject_level_translation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_level_id INTEGER,
    language_code VARCHAR(10),
    name VARCHAR(30),
    description VARCHAR(512),
    FOREIGN KEY (subject_level_id) REFERENCES subject_level(id)
);

CREATE TABLE exercise_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_topic_id INT,
    question VARCHAR(256),
    answer VARCHAR(256),
    score INT,
    create_date DATE,
    FOREIGN KEY (user_topic_id) REFERENCES user_topic(id)
);

