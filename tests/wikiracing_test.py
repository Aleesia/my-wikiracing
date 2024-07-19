import unittest
from src.wikiracing import WikiRacer


class WikiRacerTest(unittest.TestCase):

    racer = WikiRacer()

    def test_1(self):
        print("Test 1")
        path = self.racer.find_path('Дружба', 'Рим')
        self.assertEqual(path, ['Дружба', 'Якопо Понтормо', 'Рим'])
        print(path)

    def test_2(self):
        print("Test 2")
        path = self.racer.find_path('Мітохондріальна ДНК', 'Вітамін K')
        print(path)
        self.assertEqual(path, ['Мітохондріальна ДНК', 'Дезоксирибонуклеїнова кислота', 'Аденозинтрифосфат', 'Вітамін K'])

    def test_3(self):
        path = self.racer.find_path('Марка (грошова одиниця)', 'Китайський календар')
        print("found path from Марка (грошова одиниця) to Китайський календар: ")
        print(path)
        self.assertEqual(path, ['Марка (грошова одиниця)', 'Європа', 'Хвилина', 'Китайський календар'])

    def test_4(self):
        path = self.racer.find_path('Фестиваль', 'Пілястра')
        print("found path from Фестиваль to Пілястра: ")
        print(path)
        self.assertEqual(path, ['Фестиваль', 'Бароко', 'Пілястра'])

    def test_5(self):
        path = self.racer.find_path('Дружина (військо)', '6 жовтня')
        print("found path from Дружина (військо) to 6 жовтня: ")
        print(path)
        # self.assertEqual(path, ['Марка (грошова одиниця)', 'Європа', '15 жовтня', '6 жовтня'])
        self.fail("Implement me")

    def test_6(self):
        path = self.racer.find_path('Натяжні стелі', 'Мошногір\'я')
        print("found path from Натяжні стелі to 6 Мошногір\'я: ")
        print(path)

if __name__ == '__main__':
    unittest.main()
