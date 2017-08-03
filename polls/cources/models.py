from pony.orm import *

db = Database()
db.bind(provider='sqlite', filename='db.sqlite',create_db=True)

class Exam(db.Entity):
    name = PrimaryKey(str)
    testFinish = Required(bool,sql_default=False)
    questions = Set('Question')

class Question(db.Entity):
    name = PrimaryKey(str)
    outId = Required(str)
    answers = Set('Answer')
    exam = Required(Exam)


class Answer(db.Entity):
    id = PrimaryKey(int,auto=True)
    value = Required(str)
    question = Required(Question)



db.generate_mapping(create_tables=True)
sql_debug(True)


def test_db():
    with db_session:

        exam1 = Exam(name='test',testFinish=False)

        q1 = Question(outId='abcdssss1231',name='测试题目1',exam = exam1)
        q2 = Question(outId='abcdssss1232',name='测试题目2',exam = exam1)

        qa1 = Answer(value='正确',question=q1)
        qa2 = Answer(value='错误',question=q1)

        e1 = select(p for p in Exam).first()

        commit()



