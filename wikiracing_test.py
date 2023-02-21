import unittest

from wikiracing import WikiRacer


class WikiRacerTest(unittest.TestCase):

    racer = WikiRacer()

    def test_1(self):
        path = self.racer.find_path('Дружба', 'Рим')
        self.assertEqual(path, ['Дружба', 'Якопо Понтормо', 'Рим'])

    def test_2(self):
        path = self.racer.find_path('Мітохондріальна ДНК', 'Вітамін K')
        self.fail("implement me")

    def test_3(self):
        path = self.racer.find_path('Марка (грошова одиниця)', 'Китайський календар')
        self.fail("implement me")

    def test_4(self):
        path = self.racer.find_path('Фестиваль', 'Пілястра')
        self.fail("implement me")

    def test_5(self):
        path = self.racer.find_path('Дружина (військо)', '6 жовтня')
        self.fail("implement me")


if __name__ == '__main__':
    unittest.main()
