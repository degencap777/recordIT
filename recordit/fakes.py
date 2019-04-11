# -*- coding: utf-8 -*-

from faker import Faker

from recordit import db
from recordit.models import Course, RecordTable, Report, User

fake = Faker('zh_CN')


def fake_admin():
    admin = User(
        name='Zero',
        number='007',
        remark=fake.text()
    )
    admin.set_password('recordit')

    db.session.add(admin)
    db.session.commit()


def fake_student(count=50):
    for _ in range(count):
        number = '2016' + fake.random_number(digits=8, fix_len=True)
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
