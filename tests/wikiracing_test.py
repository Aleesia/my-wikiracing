import unittest
from src.wikiracing import WikiRacer


class WikiRacerTest(unittest.TestCase):

    racer = WikiRacer()

    def test_1(self):
        path = self.racer.find_path('Дружба', 'Рим')
        self.assertEqual(path, ['Дружба', 'Якопо Понтормо', 'Рим'])

    def test_2(self):
        path = self.racer.find_path('Мітохондріальна ДНК', 'Вітамін K')
        self.assertEqual(path, ['Мітохондріальна ДНК', 'Дезоксирибонуклеїнова кислота', 'Аденозинтрифосфат', 'Вітамін K'])

    def test_3(self):
        path = self.racer.find_path('Марка (грошова одиниця)', 'Китайський календар')
        self.assertEqual(path, ['Марка (грошова одиниця)', 'Європа', 'Рік', 'Китайський календар'])

    def test_4(self):
        path = self.racer.find_path('Фестиваль', 'Пілястра')
        self.assertEqual(path, ['Фестиваль', 'Бароко', 'Пілястра'])

    def test_5(self):
        path = self.racer.find_path('Дружина (військо)', '6 жовтня')
        self.assertEqual(path, ['Дружина (військо)', 'Велике князівство Московське', '22 жовтня', '6 жовтня'])

if __name__ == '__main__':
    unittest.main()
