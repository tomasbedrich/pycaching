#!/usr/bin/env python3
import unittest
from datetime import date
from unittest import mock

from pycaching.i18nhelper import I18NHelperFactory


class TestI18NHelperFactory(unittest.TestCase):
    def setUp(self):
        pass

    def test_factory_create_helper(self):
        f = I18NHelperFactory.create("de-DE")
        pass

    def test_factory_create_unsupported_language(self):
        with self.assertRaises(NotImplementedError):
            f = I18NHelperFactory.create("xx-XX")

    def test_factory_list_supported_language(self):
        supported_language = I18NHelperFactory.supported_languages()
        self.assertEqual(len(supported_language[0]), 3)
        pass

    def test_factory_get_i18nhelper_classes(self):
        x = I18NHelperFactory.get_i18nhelper_classes()
        self.assertEqual(list, type(x))


class TestI18NHelperInterface(unittest.TestCase):
    def setUp(self):
        pass

    def test_interface(self):
        helpers = I18NHelperFactory.get_i18nhelper_classes()
        for helper_class in helpers:
            helper = helper_class()
            self.assertEqual(str, type(helper.language))
            self.assertEqual(str, type(helper.language_name))
            self.assertEqual(str, type(helper.language_name_en))
            self.assertEqual(str, type(helper._country_pattern))
            self.assertEqual(str, type(helper._author_pattern))
