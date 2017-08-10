from pony.orm import *

db = Database()
db.bind(provider='sqlite', filename='rules.sqlite', create_db=True)


class Person(db.Entity):
    name = PrimaryKey(str)
    s_ruleRelations = Set('RuleRelation')
    t_ruleRelations = Set('RuleRelation')


class Rule(db.Entity):
    name = PrimaryKey(str)
    ruleRelations = Set('RuleRelation')


class RuleRelation(db.Entity):
    id = PrimaryKey(int, auto=True)
    rule = Required(Rule)
    s_person = Required(Person, reverse="s_ruleRelations")
    t_person = Required(Person, reverse="t_ruleRelations")


db.generate_mapping(create_tables=True)
sql_debug(True)

if __name__ == '__main__':
    with db_session:
        # exam1 = Exam(name='test',testFinish=False)
        #
        # q1 = Question(outId='abcdssss1231',name='测试题目1',exam = exam1)
        # q2 = Question(outId='abcdssss1232',name='测试题目2',exam = exam1)
        #
        # qa1 = Answer(value='正确',question=q1)
        # qa2 = Answer(value='错误',question=q1)
        #
        # e1 = select(p for p in Exam).first()

        rule = Rule(name='拣选')

        zhongshuo = Person(name='钟硕')
        huangjiang = Person(name='黄江')
        wangze = Person(name='王泽')
        taozhen = Person(name='陶臻')
        xuchun = Person(name='徐纯')

        z2w = RuleRelation(rule=rule, s_person=zhongshuo, t_person=wangze)
        w2t = RuleRelation(rule=rule, s_person=wangze, t_person=taozhen)
        t2x = RuleRelation(rule=rule, s_person=taozhen, t_person=xuchun)



        commit()
