from contextlib import contextmanager
from datetime import datetime, timedelta
from random import randint, choice
from sqlite3 import Error

import numpy as np
import psycopg2
from faker import Faker

fake = Faker()


@contextmanager
def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='567234')
        # print(conn)
        yield conn
        conn.commit()
    except Error as e:
        print(e)
        conn.rollback()
    finally:
        conn.close()


def create_tables(conn):
    with open('init_db.sql', 'r') as f:
        sql = f.read()
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def initialize():
    with create_connection() as conn:
        if conn is not None:
            create_tables(conn)
        else:
            print('Error: can\'t create the database connection')


def scores_rand_gen():
    """
    Return score with skewed probability: higher scores in 50x are more probable
    """
    scores = np.arange(1, 10, 1)

    # Make each of the last 4 elements 50x more likely
    prob = [1.0] * (len(scores) - 4) + [50.0] * 4

    # Normalising to 1.0
    prob /= np.sum(prob)
    while True:
        yield int(np.random.choice(scores, 1, p=prob))


def date_gen():
    """
    Generate list of dates for exams
    """
    start_date = datetime.strptime("2021-10-01", "%Y-%m-%d")
    end_date = datetime.strptime("2022-09-05", "%Y-%m-%d")

    result = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.isoweekday() < 6:
            yield current_date
        current_date += timedelta(1)


def fill_tables():
    """
    sql-queries to fill all tables
    """
    sql_insert_groups_table = "INSERT INTO groups(group_n) VALUES(%s)"
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            for i in range(n_groups):
                cur.execute(sql_insert_groups_table, (i + 1,))
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    sql_insert_students_table = "INSERT INTO students(name,group_id,enroll_year) VALUES(%s, %s, %s)"
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            for _ in range(n_students):
                cur.execute(sql_insert_students_table, (fake.name(), randint(1, 3), str(randint(2020, 2022))))
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    titles = ['Dr.', 'Prof.']
    sql_insert_teachers_table = "INSERT INTO teachers(title,name) VALUES(%s, %s)"
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            for _ in range(n_teachers):
                cur.execute(sql_insert_teachers_table, (choice(titles), fake.name()))
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    sql_insert_subjects_table = "INSERT INTO subjects(title,teacher_id) VALUES(%s, %s)"
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            for i in range(n_subjects):
                cur.execute(sql_insert_subjects_table, (subject_names[i], randint(1, 3)))
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    sql_insert_exams_table = "INSERT INTO exams(student_id,subject_id,score,date) VALUES(%s, %s, %s, %s)"
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            scores = scores_rand_gen()
            exam_date = date_gen()
            for n in range(n_students):
                for c in range(n_subjects):
                    cur.execute(sql_insert_exams_table, (n+1, c+1, next(scores), next(exam_date)))
            cur.close()
        else:
            print('Error: can\'t create the database connection')


def sql_queries():
    """
    sql-queries from HW description
    """

    # 1. 5 студентов с наибольшим средним баллом по всем предметам
    sql_query = """
        SELECT students.name, round(avg(exams.score), 1) avg_score
        FROM students, exams
        WHERE students.s_id = exams.student_id
        GROUP BY students.name
        ORDER BY avg_score DESC
        LIMIT 5;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            print("1. 5 students with highest avg score:")
            res = cur.fetchall()
            for el in res:
                print(f'\t- {el[0]}: {el[1]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 2. 1 студент с наивысшим средним баллом по одному предмету
    with create_connection() as conn:
        if conn is not None:
            print()
            print("2. 1 students with highest score on each subject:")
            for c_name in subject_names:
                sql_query = f"""
                    SELECT subj.title, s.name, e.score as score
                    FROM exams e
                    LEFT JOIN students s ON s.s_id = e.student_id
                    LEFT JOIN subjects subj ON subj.subj_id = e.subject_id
                    WHERE subj.title = '{c_name}'
                    GROUP BY s.s_id, subj.subj_id, score
                    ORDER BY score DESC 
                    LIMIT 1;
                    """

                cur = conn.cursor()
                cur.execute(sql_query, (n_subjects,))
                el = cur.fetchone()
                print(f'\t- {el[0]}: {el[1]} - {el[2]}')
                cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 3. Средний балл в группе по одному предмету
    sql_query = """
        SELECT subj.title, gr.group_n, round(avg(e.score), 2) avg_score
        FROM exams e
        LEFT JOIN students s ON s.s_id = e.student_id
        LEFT JOIN subjects subj ON subj.subj_id = e.subject_id
        LEFT JOIN groups gr ON gr.g_id = s.group_id
        WHERE subj.subj_id = 1
        GROUP BY subj.title, gr.group_n
        ORDER BY avg_score DESC 
        LIMIT 5;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            print()
            print("3. Avg score in a group for one subject:")
            res = cur.fetchall()
            for el in res:
                print(f'\t- {el[0]}, group {el[1]}: {el[2]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 4. Средний балл в потоке
    sql_query = """
        SELECT round(avg(e.score), 2) avg_score
        FROM exams e;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            print()
            print("5. Avg score in the stream")
            res = cur.fetchall()
            for el in res:
                print(f'\t- {el[0]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 5. Какие курсы читает преподаватель
    sql_query = """
        SELECT t.title, t.name, s.title
        FROM teachers t
        LEFT JOIN subjects s ON s.teacher_id = t.t_id;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            print()
            print("6. Teachers on subjects")
            res = cur.fetchall()
            for el in res:
                print(f'\t- {el[0]} {el[1]}: {el[2]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 6. Список студентов в группе
    sql_query = """
        SELECT gr.group_n, s.name
        FROM students s
        LEFT JOIN groups gr ON s.group_id = gr.g_id
        where gr.g_id = 2;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            res = cur.fetchall()
            print()
            print(f"7. List of students in group {res[0][0]}:")
            for el in res:
                print(f'\t- {el[1]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 7. Оценки студентов в группе по предмету
    sql_query = """
        SELECT gr.group_n, subj.title, s.name, e.score
        FROM exams e
        LEFT JOIN students s ON s.s_id = e.student_id
        LEFT JOIN groups gr ON s.group_id = gr.g_id
        LEFT JOIN subjects subj ON subj.subj_id = e.subject_id
        WHERE gr.g_id = 2 AND subj.subj_id = 1;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            res = cur.fetchall()
            print()
            print(f"7. Scores of students in group {res[0][0]} on subjects {res[0][1]}:")
            for el in res:
                print(f'\t- {el[2]}: {el[3]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 8. Оценки студентов в группе по предмету на последнем занятии.
    sql_query = """
        SELECT gr.group_n, subj.title, s.name, e.score, e.date
        FROM exams e
        LEFT JOIN students s ON s.s_id = e.student_id
        LEFT JOIN groups gr ON s.group_id = gr.g_id
        LEFT JOIN subjects subj ON subj.subj_id = e.subject_id
        WHERE subj.subj_id = 1 AND gr.g_id = 1 AND e.date = (
            SELECT e.date
            FROM exams e
            LEFT JOIN students s ON s.s_id = e.student_id
            LEFT JOIN groups gr ON s.group_id = gr.g_id
            WHERE e.subject_id = 1 AND gr.g_id = 1
            ORDER BY e.date DESC
            LIMIT 1
            )
        ORDER BY e.date DESC;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            res = cur.fetchall()
            print()
            print(f"8. Last scores of students in group {res[0][0]} on subjects {res[0][1]}:")
            for el in res:
                print(f'\t- {el[2]} - {el[3]}, on {el[4].date()}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 9. Список курсов, которые посещает студент.
    sql_query = """
        SELECT s.name, subj.title
        FROM exams e
        LEFT JOIN students s ON s.s_id = e.student_id
        LEFT JOIN subjects subj ON subj.subj_id = e.subject_id
        WHERE s.s_id = 1;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            res = cur.fetchall()
            print()
            print(f"9. List of subjects attended by student {res[0][0]}:")
            for el in res:
                print(f'\t- {el[1]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 10. Список курсов, которые студенту читает преподаватель.
    sql_query = """
        SELECT t.title, t.name, s.name, subj.title
        FROM exams e
        LEFT JOIN students s ON s.s_id = e.student_id
        LEFT JOIN subjects subj ON subj.subj_id = e.subject_id
        LEFT JOIN teachers t on subj.teacher_id = t.t_id
        WHERE s.s_id = 1 AND t.t_id = 1;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            res = cur.fetchall()
            print()
            print(f"10. List of subjects handled by {res[0][0]} {res[0][1]} and attended by student {res[0][2]}:")
            for el in res:
                print(f'\t- {el[3]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 11. Средний балл, который преподаватель ставит студенту.
    sql_query = """
        SELECT t.title, t.name, s.name, round(avg(e.score), 2) as avg_score
        FROM teachers t
        LEFT JOIN subjects subj ON subj.teacher_id = t.t_id
        LEFT JOIN exams e ON subj.subj_id = e.subject_id
        LEFT JOIN students s  ON s.s_id = e.student_id
        WHERE s.s_id = 1 AND t.t_id = 1
        GROUP BY s.name, t.title, t.name;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            res = cur.fetchall()
            print()
            print(
                f"11. Average score that {res[0][0]} {res[0][1]} grades {res[0][2]} :")
            for el in res:
                print(f'\t- {el[3]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')

    # 12. Средний балл, который ставит преподаватель.
    sql_query = """
        SELECT t.title, t.name, round(avg(e.score), 2) as avg_score
        FROM exams e
        LEFT JOIN subjects subj ON subj.subj_id = e.subject_id
        LEFT JOIN teachers t ON t.t_id = subj.teacher_id
        WHERE t.t_id = 2
        GROUP BY t.title, t.name;
        """
    with create_connection() as conn:
        if conn is not None:
            cur = conn.cursor()
            cur.execute(sql_query)
            res = cur.fetchall()
            print()
            print(
                f"12. Average score graded by {res[0][0]} {res[0][1]}:")
            for el in res:
                print(f'\t- {el[2]}')
            cur.close()
        else:
            print('Error: can\'t create the database connection')


if __name__ == '__main__':
    n_students = 30
    n_groups = 3
    n_teachers = 3
    subject_names = ["CS50", "Data Science", "OpenCV I", "SQL DBs", "Python"]
    n_subjects = len(subject_names)

    initialize()
    fill_tables()
    sql_queries()
