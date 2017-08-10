import json
from pony.orm import *
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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
def saveRootRule(t_person, rule):
    root = RuleRelation(rule=rule, s_person=t_person, t_person=t_person)
    flush()
    root.root = root


@db_session
def saveRule(s_person, t_person, rule):
    # 获取 授权人 拥有当前 rule 的 trees
    s_trees = select(p for p in RuleRelation if p.t_person == s_person and p.rule == rule)
    t_trees = select(p for p in RuleRelation if p.t_person == t_person and p.rule == rule)

    for s in s_trees:
        # 查看是否已经授权过这颗树
        if haveSameRule(s, t_trees):
            continue
        else:
            newRule = RuleRelation(rule=rule, s_person=s_person, t_person=t_person)
            newRule.root = s.root
            log.info('save ' + s_person.name + ' to ' + t_person.name
                     + ": " + str(newRule.to_dict())
                     + ": " + str(s.to_dict()))
    commit()

def haveSameRule(relation, t_trees):
    for t in t_trees:
        if t.id == relation.id and t.root == relation.root:
            return True
    return False


def removeRule(s_person, t_person, rule):
    log.info('remove ' + s_person.name + ' to ' + t_person.name)


# 是否存在相同父节点
def existsNode(person, lineNode):
    return True
