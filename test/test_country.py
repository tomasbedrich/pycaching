#!/usr/bin/env python3
import unittest

from pycaching.country import CountryStateDict, CountryState, CountryStateAmbiguityValue, CountryStateUnknownName


class TestCountryStateDict(unittest.TestCase):
    def setUp(self):
        pass

    def test_unique_country(self):
        names = [country.lower() for country in CountryStateDict.countries.values()]
        self.assertEqual(250, len(names))
        for name in names:
            self.assertEqual(1, names.count(name), f'Country name {name} is not unique')

    def test_unique_state(self):
        names = [state.lower() for state in CountryStateDict.states.values()]
        self.assertEqual(465, len(names))
        for name in names:
            if name in ('distrito federal', 'limburg'):
                continue
            self.assertEqual(1, names.count(name), f'State name {name} is not unique')


class TestCountryStateProperties(unittest.TestCase):
    def setUp(self):
        pass

    def test_ctor(self):
        c = CountryState()

        try:
            c = CountryState(4711)
            self.assertTrue(False)
        except ValueError:
            pass
        except Exception:
            self.assertTrue(False)

        try:
            c = CountryState(2, 4711)
            self.assertTrue(False)
        except ValueError:
            pass
        except Exception:
            self.assertTrue(False)

        try:
            c = CountryState(sid=4711)
            self.assertTrue(False)
        except ValueError:
            pass
        except Exception:
            self.assertTrue(False)

        try:
            c = CountryState(2, 77)
            self.assertTrue(False)
        except ValueError:
            pass
        except Exception:
            self.assertTrue(False)

        c = CountryState(2,27)
        self.assertEqual(str(c),'Montana, United States')

    def test_from_string(self):
        with self.subTest('only country'):
            c = CountryState.from_string('gErMaNy')
            self.assertEqual(c.country_id, 79)
            self.assertIsNone(c.state_id)
            self.assertEqual(c.country_name, 'Germany')
            self.assertFalse(c.has_state)

        with self.subTest('only state'):
            c = CountryState.from_string('bAyErN')
            self.assertEqual(c.country_id, 79)
            self.assertEqual(c.state_id, 136)
            self.assertEqual(c.country_name, 'Germany')
            self.assertEqual(c.state_name, 'Bayern')
            self.assertTrue(c.has_state)

        with self.subTest('both state, country'):
            c = CountryState.from_string('bAyErN , Germany')
            self.assertEqual(c.country_id, 79)
            self.assertEqual(c.state_id, 136)
            self.assertEqual(c.country_name, 'Germany')
            self.assertEqual(c.state_name, 'Bayern')
            self.assertTrue(c.has_state)

        with self.subTest('both country, state'):
            c = CountryState.from_string('Germany, bAyErN')
            self.assertEqual(c.country_id, 79)
            self.assertEqual(c.state_id, 136)
            self.assertEqual(c.country_name, 'Germany')
            self.assertEqual(c.state_name, 'Bayern')
            self.assertTrue(c.has_state)

        with self.subTest('Bonaire, Sint Eustatius and Saba'):
            c = CountryState.from_string('Bonaire, Sint Eustatius and Saba')
            self.assertEqual(c.country_id, 279)
            self.assertIsNone(c.state_id)
            self.assertEqual(c.country_name, 'Bonaire, Sint Eustatius and Saba')
            self.assertFalse(c.has_state)

        with self.subTest('Bonaire'):
            c = CountryState.from_string('Bonaire')
            self.assertEqual(c.country_id, 279)
            self.assertEqual(c.state_id, 523)
            self.assertTrue(c.has_state)

        with self.subTest('Sint Eustatius'):
            c = CountryState.from_string('Sint Eustatius')
            self.assertEqual(c.country_id, 279)
            self.assertEqual(c.state_id, 524)
            self.assertTrue(c.has_state)

        with self.subTest('Saba'):
            c = CountryState.from_string('Saba')
            self.assertEqual(c.country_id, 279)
            self.assertEqual(c.state_id, 525)
            self.assertTrue(c.has_state)

        with self.subTest('Sint Eustatius, Bonaire, Sint Eustatius and Saba'):  # GC4NDTH
            c = CountryState.from_string('Sint Eustatius, Bonaire, Sint Eustatius and Saba')
            self.assertEqual(c.country_id, 279)
            self.assertEqual(c.state_id, 524)
            self.assertTrue(c.has_state)

    def test_all_country(self):
        for country_id, name in CountryStateDict.countries.items():
            with self.subTest(name):
                c = CountryState.from_string(name)
                self.assertEqual(c.country_id, country_id)


    def test_country_as_state(self):
        for country_id, name in CountryStateDict.countries.items():
            if name in ('Luxembourg', 'Georgia'):
                continue

            try:
                c = CountryState.from_string_state(name)
                self.assertTrue(False, str(c))
            except CountryStateUnknownName:
                pass
            except Exception:
                self.assertTrue(False, str(c))


    def test_state_as_country(self):
        for country_id, name in CountryStateDict.states.items():
            if name in ('Luxembourg', 'Georgia'):
                continue

            try:
                c = CountryState.from_string_country(name)
                self.assertTrue(False, str(c))
            except CountryStateUnknownName:
                pass
            except Exception:
                self.assertTrue(False, str(c))



    def test_all_state(self):
        for state_id, name in CountryStateDict.states.items():
            '''
                Exclude ....

                - Georgia, Luxembourg are countries and states
                - Limburg, Distrito Federal are states in different countries
            '''

            if name in ('Georgia','Luxembourg', 'Limburg', 'Distrito Federal'):
                continue

            with self.subTest(name):
                c = CountryState.from_string(name)
                self.assertEqual(c.state_id, state_id)

    def test_ambiguity_Luxembourg(self):
        with self.subTest('from_string() - Luxembourg'):
            c = CountryState.from_string('Luxembourg')
            self.assertEqual(c.country_id, 8)
            self.assertIsNone(c.state_id)
            self.assertFalse(c.has_state)

        with self.subTest('from_string_country() - Luxembourg'):
            c = CountryState.from_string_country('Luxembourg')
            self.assertEqual(c.country_id, 8)
            self.assertIsNone(c.state_id)
            self.assertFalse(c.has_state)

        with self.subTest('from_string_state() - Luxembourg'):
            c = CountryState.from_string_state('Luxembourg')
            self.assertEqual(c.country_id, 4)
            self.assertEqual(c.state_id, 90)
            self.assertTrue(c.has_state)

        with self.subTest('from_string() - Luxembourg'):
            c = CountryState.from_string('Luxembourg, Belgium')
            self.assertEqual(c.country_id, 4)
            self.assertEqual(c.state_id, 90)
            self.assertTrue(c.has_state)

    def test_ambiguity_Georgia(self):
        with self.subTest('from_string() - Georgia, United States'):
            c = CountryState.from_string('Georgia, United States')
            self.assertEqual(c.country_id, 2)
            self.assertEqual(c.state_id, 11)
            self.assertTrue(c.has_state)

        with self.subTest('from_string() - Georgia'):
            c = CountryState.from_string('Georgia')
            self.assertEqual(c.country_id, 78)
            self.assertIsNone(c.state_id)
            self.assertFalse(c.has_state)

        with self.subTest('from_string_country() - Georgia'):
            c = CountryState.from_string_country('Georgia')
            self.assertEqual(c.country_id, 78)
            self.assertIsNone(c.state_id)
            self.assertFalse(c.has_state)

        with self.subTest('from_string_state() - Georgia'):
            c = CountryState.from_string_state('Georgia')
            self.assertEqual(c.country_id, 2)
            self.assertEqual(c.state_id, 11)
            self.assertTrue(c.has_state)

    def test_ambiguity_Limburg(self):
        name = 'Limburg'
        with self.subTest(f'from_string({name})'):
            try:
                c = CountryState.from_string(name)
                self.assertTrue(False)
            except CountryStateAmbiguityValue:
                pass

        with self.subTest(f'from_string_state({name})'):
            try:
                c = CountryState.from_string_state(name)
                self.assertTrue(False)
            except CountryStateAmbiguityValue:
                pass

        name = 'Limburg, Belgium'
        with self.subTest(f'from_string({name})'):
            c = CountryState.from_string(name)
            self.assertEqual(c.country_id,4)
            self.assertEqual(c.state_id, 89)
            self.assertTrue(c.has_state)

        name = 'Limburg, Netherlands'
        with self.subTest(f'from_string({name})'):
            c = CountryState.from_string(name)
            self.assertEqual(c.country_id, 141)
            self.assertEqual(c.state_id, 393)
            self.assertTrue(c.has_state)

    def test_ambiguity_Distrito_Federal(self):
        name = 'Distrito Federal'
        with self.subTest(f'from_string({name})'):
            try:
                c = CountryState.from_string(name)
                self.assertTrue(False)
            except CountryStateAmbiguityValue:
                pass

        with self.subTest(f'from_string_state({name})'):
            try:
                c = CountryState.from_string_state(name)
                self.assertTrue(False)
            except CountryStateAmbiguityValue:
                pass

        name = 'Distrito Federal, Brazil'
        with self.subTest(f'from_string({name})'):
            c = CountryState.from_string(name)
            self.assertEqual(c.country_id, 34)
            self.assertEqual(c.state_id, 168)
            self.assertTrue(c.has_state)

        name = 'Distrito Federal, Mexico'
        with self.subTest(f'from_string({name})'):
            c = CountryState.from_string(name)
            self.assertEqual(c.country_id, 228)
            self.assertEqual(c.state_id, 462)
            self.assertTrue(c.has_state)

    def test_special_names(self):
        c = CountryState.from_string('Curaçao')
        self.assertEqual(c.country_id, 54)
        self.assertIsNone(c.state_id)
        self.assertFalse(c.has_state)

        c = CountryState.from_string('Bonaire, Sint Eustatius and Saba')
        self.assertEqual(c.country_id, 279)
        self.assertIsNone(c.state_id)
        self.assertFalse(c.has_state)

        c = CountryState.from_string_country('Bonaire, Sint Eustatius and Saba')
        self.assertEqual(c.country_id, 279)
        self.assertIsNone(c.state_id)
        self.assertFalse(c.has_state)

        c = CountryState.from_string('Côte d\'Ivoire')
        self.assertEqual(c.country_id, 100)
        self.assertIsNone(c.state_id)
        self.assertFalse(c.has_state)

        c = CountryState.from_string_country('Côte d\'Ivoire')
        self.assertEqual(c.country_id, 100)
        self.assertIsNone(c.state_id)
        self.assertFalse(c.has_state)

