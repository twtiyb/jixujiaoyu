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
    root = Optional('RuleRelation', reverse='root')

#
# class RootNode(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     rule = Required(Rule)
#     s_person = Required(Person, reverse="s_ruleRelations")
#     t_person = Required(Person, reverse="t_ruleRelations")


db.generate_mapping(create_tables=True)
sql_debug(True)

@db_session
def test_basicData():
    # e1 = select(p for p in Exam).first()
    # cleanRelation()
    rule = Rule(name='拣选')

    zhongshuo = Person(name='钟硕')
    huangjiang = Person(name='黄江')
    wangze = Person(name='王泽')
    taozhen = Person(name='陶臻')
    xuchun = Person(name='徐纯')

    # 简单的授权
    rootZ = RuleRelation(rule=rule, s_person=zhongshuo, t_person=zhongshuo)
    # rootZ.root = rootZ
    z2w = RuleRelation(rule=rule, s_person=zhongshuo, t_person=wangze)
    w2t = RuleRelation(rule=rule, s_person=wangze, t_person=taozhen)
    t2x = RuleRelation(rule=rule, s_person=taozhen, t_person=xuchun)

    commit()


@db_session
def cleanData():
    db.execute('delete from RuleRelation')
    db.execute('delete from Rule')
    db.execute('delete from Person')
    commit()

@db_session
def cleanRelation():
    db.execute('delete from RuleRelation')
    commit()


@db_session
def test_basic():
    commit()


@db_session
def test_basic2():
    commit()


# 是否存在相同父节点
def existsNode(person, lineNode):
    return True;
