from unittest import TestCase

from polls.rule.models import *


class TestBasicData(TestCase):
    @db_session
    def test_save_onetree(self):
        cleanData()

        rule = Rule(name='拣选')

        zhongshuo = Person(name='钟硕')
        huangjiang = Person(name='黄江')
        wangze = Person(name='王泽')
        taozhen = Person(name='陶臻')
        xuchun = Person(name='徐纯')

        # 管理员权限

        root = saveRootRule(zhongshuo, rule)

        saveRule(zhongshuo, wangze, rule)
        saveRule(zhongshuo, wangze, rule)
        # saveRule(wangze, taozhen, rule)
        # saveRule(taozhen, xuchun, rule)
        # saveRule(xuchun, huangjiang, rule)

        commit()

    @db_session
    def test_save_moretree(self):
        commit()
