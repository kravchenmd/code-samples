-- Table: groups
DROP TABLE IF EXISTS groups CASCADE;
CREATE TABLE groups (
    g_id SERIAL PRIMARY KEY,
    group_n INTEGER UNIQUE NOT NULL
);

-- Table: students
DROP TABLE IF EXISTS students CASCADE;
CREATE TABLE students (
    s_id SERIAL PRIMARY KEY,
    name VARCHAR(60) UNIQUE NOT NULL,
    group_id INTEGER,
    enroll_year VARCHAR(4),
    FOREIGN KEY (group_id) REFERENCES groups (g_id)
      ON DELETE SET NULL
      ON UPDATE CASCADE
);

-- Table: teachers
DROP TABLE IF EXISTS teachers CASCADE;
CREATE TABLE teachers (
    t_id SERIAL PRIMARY KEY,
    title VARCHAR(5),
    name VARCHAR(100) NOT NULL
);

-- Table: subjects
DROP TABLE IF EXISTS subjects CASCADE;
CREATE TABLE subjects (
    subj_id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    teacher_id INTEGER,
    FOREIGN KEY (teacher_id) REFERENCES teachers (t_id)
      ON DELETE SET NULL
      ON UPDATE CASCADE
);

-- Table: exams
DROP TABLE IF EXISTS exams;
CREATE TABLE exams (
    student_id SERIAL REFERENCES students(s_id),
    subject_id SERIAL REFERENCES subjects(subj_id),
    score integer,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pk PRIMARY KEY(student_id, subject_id)
);