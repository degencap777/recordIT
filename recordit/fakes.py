# -*- coding: utf-8 -*-

from faker import Faker
from sqlalchemy.sql.expression import func

from recordit import db
from recordit.models import Course, RecordTable, Report, User, Role

fake = Faker('zh_CN')


def fake_admin():
    admin = User(
        name=fake.name(),
        number='007',
        remark=fake.text()
    )
    admin.set_password('recordit')

    db.session.add(admin)
    db.session.commit()


def fake_teacher(count=1):
    for i in range(count):
        print(i)
        user = User(
            name=fake.name(),
            number=str(fake.random_number(digits=4, fix_len=True)),
            remark=fake.text(),
        )
        user.set_password('recordit')
        user.set_role('Teacher')

        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()


def fake_student(count=50, grade='2016'):
    for i in range(count):
        print(i)
        number = grade + str(fake.random_number(digits=8, fix_len=True))
        user = User(
            name=fake.name(),
            number=number,
            remark=fake.text(),
        )
        user.set_password('recordit')

        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()


def fake_course(count=1):
    role_teacher = Role.query.filter_by(name='Teacher').first()
    role_student = Role.query.filter_by(name='Student').first()
    for i in range(count):
        print(i)
        teacher = User.query.filter_by(
            role_id=role_teacher.id).order_by(func.random()).first()
        student = User.query.filter_by(
            role_id=role_student.id).order_by(func.random()).first()
        course = Course(
            teacher_id=teacher.id,
            name=fake.text(max_nb_chars=10),
            grade=student.grade,
            remark=fake.text()
        )
        db.session.add(course)
        try:
            db.session.commit()
        except:
            db.session.rollback()


def fake_report(count=3):
    role = Role.query.filter_by(name='Student').first()
    for i in range(count):
        print(i)
        user = User.query.filter_by(
            role_id=role.id).order_by(func.random()).first()
        course = Course.query.filter_by(grade=user.grade).order_by(func.random()).first()
        if course:
            report = Report(
                course_id=course.id,
                speaker_id=user.id,
                name=fake.text(max_nb_chars=10),
                remark=fake.text()
            )

            db.session.add(report)
            try:
                db.session.commit()
            except:
                db.session.rollback()


def fake_record(count=10):
    for i in range(count):
        print(i)
        user = User.query.order_by(func.random()).first()
        report = Report.query.filter(
            Report.speaker_id != user.id).order_by(func.random()).first()
        if report:
            record = RecordTable(
                report_id=report.id,
                user_id=user.id,
                score=fake.random_int(min=0, max=100),
                remark=fake.text()
            )

            db.session.add(record)
            try:
                db.session.commit()
            except:
                db.session.rollback()
