import inspect
import re
import sys


class I18NHelperFactory:
    @staticmethod
    def get_i18nhelper_classes():
        clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        i18n = [_class for name, _class in clsmembers if hasattr(_class, '_language')]
        return i18n

    @classmethod
    def create(cls, language, *args, **kwargs):
        classes = cls.get_i18nhelper_classes()
        for _class in classes:
            if _class._language == language:
                return _class(*args, **kwargs)
        raise NotImplementedError(f'There is no I18N helper for language: {language}')

    @classmethod
    def supported_languages(cls):
        classes = cls.get_i18nhelper_classes()
        l = [(_class._language, _class._language_name, _class._language_name_en) for _class in classes]
        l.sort(key=lambda _: _[0])
        return l


class I18NHelperBase:
    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return f'I18NHelper for {self.language_name_en} ({self.language_name}|{self.language})'

    @property
    def language(self):
        """
        Returns the code of the supported language of the helper class

        :return:
        """
        return self._language

    @property
    def language_name(self):
        """
        Returns the name of the supported language of the helper class

        :return:
        """
        return self._language_name

    @property
    def language_name_en(self):
        """
        Returns the english name of the supported language of the helper class

        :return:
        """
        return self._language_name_en

    def country(self, text):
        """
        Extract the country/state from the text

        :param text: String with the country/state name
        :return:
        """
        return self._attribute("_country_pattern", text)

    def author(self, text):
        """

        :param text:
        :return:
        """
        return self._attribute("_author_pattern", text)

    def _attribute(self, attribute, text):
        if not hasattr(self,attribute):
            raise NotImplementedError(f"{self} has no implementation for {attribute} (text={text})")
        m = re.match(getattr(self, attribute), text)
        if m is None:
            raise ValueError(f"{self.__class__} rule '{getattr(self, attribute)}' doesn't match '{text}'")
        for i in range(1,len(m.groups())+1):
            if m[i] is not None:
                return m[i]
        raise Exception


class I18NHelper_enUS(I18NHelperBase):
    _language = "en-US"
    _language_name = "English"
    _language_name_en = "English"
    _country_pattern = r"In (.+)"
    _author_pattern = r"A cache by (.+)|An event cache by (.+)"


class I18NHelper_deDE(I18NHelperBase):
    _language = "de-DE"
    _language_name = "Deutsch"
    _language_name_en = "German"
    _country_pattern = r"In (.+)"
    _author_pattern = r"Ein Geocache von (.+)"


class I18NHelper_jaJP(I18NHelperBase):
    _language = "ja-JP"
    _language_name = "日本語"
    _language_name_en = "Japanese"
    _country_pattern = r"所在地：(.+)"
    _author_pattern = r"(.+) さんのジオキャッシュ"


class I18NHelper_csSZ(I18NHelperBase):
    _language = "cs-CZ"
    _language_name = "Čeština"
    _language_name_en = "Czech"
    _country_pattern = r'V (.+)'
    _author_pattern = r'Kešku založil (.+)'


class I18NHelper_bgBG(I18NHelperBase):
    _language = "bg-BG"
    _language_name = "Български"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"В района на (.+)"
    _author_pattern = r"Кеш от (.+)"


class I18NHelper_caES(I18NHelperBase):
    _language = "ca-ES"
    _language_name = "Català"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"A (.+)"
    _author_pattern = r"Un geoamagatall de (.+)"


class I18NHelper_daDK(I18NHelperBase):
    _language = "da-DK"
    _language_name = "Dansk"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"I (.+)"
    _author_pattern = r"En cache af (.+)"


class I18NHelper_elGR(I18NHelperBase):
    _language = "el-GR"
    _language_name = "Ελληνικά"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Στην (.+)"
    _author_pattern = r"Μία κρύπτη από τον/την (.+)"


class I18NHelper_esES(I18NHelperBase):
    _language = "es-ES"
    _language_name = "Español"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"En (.+)"
    _author_pattern = r"Un caché de (.+)"


class I18NHelper_etEE(I18NHelperBase):
    _language = "et-EE"
    _language_name = "Eesti"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Asub: (.+)"
    _author_pattern = r"Peidetud (.+) poolt"


class I18NHelper_fiFI(I18NHelperBase):
    _language = "fi-FI"
    _language_name = "Suomi"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Maa: (.+)"
    _author_pattern = r"Kätkön omistaja: (.+)"


class I18NHelper_frFR(I18NHelperBase):
    _language = "fr-FR"
    _language_name = "Français"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Au/En (.+)"
    _author_pattern = r"Une cache par (.+)"


class I18NHelper_huHU(I18NHelperBase):
    _language = "hu-HU"
    _language_name = "Magyar"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Itt: (.+)"
    _author_pattern = r"A geoláda tulajdonosa (.+)"


class I18NHelper_itIT(I18NHelperBase):
    _language = "it-IT"
    _language_name = "Italiano"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"In (.+)"
    _author_pattern = r"Un cache di (.+)"


class I18NHelper_koKR(I18NHelperBase):
    _language = "ko-KR"
    _language_name = "한국어"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"(.+)에 있음"
    _author_pattern = r"설치자: (.+)"


class I18NHelper_lbLU(I18NHelperBase):
    _language = "lb-LU"
    _language_name = "Lëtzebuergesch"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"An \"(.+)\""
    _author_pattern = r"En Cache vum (.+)"


class I18NHelper_lvLV(I18NHelperBase):
    _language = "lv-LV"
    _language_name = "Latviešu"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Iekš (.+)"
    _author_pattern = r"Slēpņa autors (.+)"


class I18NHelper_nbNO(I18NHelperBase):
    _language = "nb-NO"
    _language_name = "Norsk, Bokmål"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"I (.+)"
    _author_pattern = r"En cache av (.+)"


class I18NHelper_nlNL(I18NHelperBase):
    _language = "nl-NL"
    _language_name = "Nederlands"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"In (.+)"
    _author_pattern = r"Een cache van (.+)"


class I18NHelper_plPL(I18NHelperBase):
    _language = "pl-PL"
    _language_name = "Polski"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"w (.+)"
    _author_pattern = r"Skrytka należąca do (.+)"


class I18NHelper_ptPT(I18NHelperBase):
    _language = "pt-PT"
    _language_name = "Português"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Em (.+)"
    _author_pattern = r"Uma geocache de (.+)"


class I18NHelper_roRO(I18NHelperBase):
    _language = "ro-RO"
    _language_name = "Română"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"În (.+)"
    _author_pattern = r"Un cache de către (.+)"


class I18NHelper_ruRU(I18NHelperBase):
    _language = "ru-RU"
    _language_name = "Русский"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"Где: (.+)"
    _author_pattern = r"Владелец тайника: (.+)"


class I18NHelper_skSK(I18NHelperBase):
    _language = "sk-SK"
    _language_name = "Slovenčina"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"V (.+)"
    _author_pattern = r"Skrýšu založil\(a\) (.+)"


class I18NHelper_slSI(I18NHelperBase):
    _language = "sl-SI"
    _language_name = "Slovenščina"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"(.+)"
    _author_pattern = r"Lastnik zaklada: (.+)"


class I18NHelper_svSE(I18NHelperBase):
    _language = "sv-SE"
    _language_name = "Svenska"
    _language_name_en = _language_name  # TODO
    _country_pattern = r"i (.+)"
    _author_pattern = r"En cache av (.+)"
