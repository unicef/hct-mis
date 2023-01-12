from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class Language:
    english: str
    alpha2: str
    alpha3: str


LANGUAGES: List[Language] = [
    Language(english="Afar", alpha2="aa", alpha3="aar"),
    Language(english="Abkhazian", alpha2="ab", alpha3="abk"),
    Language(english="Afrikaans", alpha2="af", alpha3="afr"),
    Language(english="Akan", alpha2="ak", alpha3="aka"),
    Language(english="Albanian", alpha2="sq", alpha3="alb"),
    Language(english="Amharic", alpha2="am", alpha3="amh"),
    Language(english="Arabic", alpha2="ar", alpha3="ara"),
    Language(english="Aragonese", alpha2="an", alpha3="arg"),
    Language(english="Armenian", alpha2="hy", alpha3="arm"),
    Language(english="Assamese", alpha2="as", alpha3="asm"),
    Language(english="Avaric", alpha2="av", alpha3="ava"),
    Language(english="Avestan", alpha2="ae", alpha3="ave"),
    Language(english="Aymara", alpha2="ay", alpha3="aym"),
    Language(english="Azerbaijani", alpha2="az", alpha3="aze"),
    Language(english="Bashkir", alpha2="ba", alpha3="bak"),
    Language(english="Bambara", alpha2="bm", alpha3="bam"),
    Language(english="Basque", alpha2="eu", alpha3="baq"),
    Language(english="Belarusian", alpha2="be", alpha3="bel"),
    Language(english="Bengali", alpha2="bn", alpha3="ben"),
    Language(english="Bihari languages", alpha2="bh", alpha3="bih"),
    Language(english="Bislama", alpha2="bi", alpha3="bis"),
    Language(english="Bosnian", alpha2="bs", alpha3="bos"),
    Language(english="Breton", alpha2="br", alpha3="bre"),
    Language(english="Bulgarian", alpha2="bg", alpha3="bul"),
    Language(english="Burmese", alpha2="my", alpha3="bur"),
    Language(english="Catalan; Valencian", alpha2="ca", alpha3="cat"),
    Language(english="Chamorro", alpha2="ch", alpha3="cha"),
    Language(english="Chechen", alpha2="ce", alpha3="che"),
    Language(english="Chinese", alpha2="zh", alpha3="chi"),
    Language(
        english="Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic",
        alpha2="cu",
        alpha3="chu",
    ),
    Language(english="Chuvash", alpha2="cv", alpha3="chv"),
    Language(english="Cornish", alpha2="kw", alpha3="cor"),
    Language(english="Corsican", alpha2="co", alpha3="cos"),
    Language(english="Cree", alpha2="cr", alpha3="cre"),
    Language(english="Czech", alpha2="cs", alpha3="cze"),
    Language(english="Danish", alpha2="da", alpha3="dan"),
    Language(english="Divehi; Dhivehi; Maldivian", alpha2="dv", alpha3="div"),
    Language(english="Dutch; Flemish", alpha2="nl", alpha3="dut"),
    Language(english="Dzongkha", alpha2="dz", alpha3="dzo"),
    Language(english="English", alpha2="en", alpha3="eng"),
    Language(english="Esperanto", alpha2="eo", alpha3="epo"),
    Language(english="Estonian", alpha2="et", alpha3="est"),
    Language(english="Ewe", alpha2="ee", alpha3="ewe"),
    Language(english="Faroese", alpha2="fo", alpha3="fao"),
    Language(english="Fijian", alpha2="fj", alpha3="fij"),
    Language(english="Finnish", alpha2="fi", alpha3="fin"),
    Language(english="French", alpha2="fr", alpha3="fre"),
    Language(english="Western Frisian", alpha2="fy", alpha3="fry"),
    Language(english="Fulah", alpha2="ff", alpha3="ful"),
    Language(english="Georgian", alpha2="ka", alpha3="geo"),
    Language(english="German", alpha2="de", alpha3="ger"),
    Language(english="Gaelic; Scottish Gaelic", alpha2="gd", alpha3="gla"),
    Language(english="Irish", alpha2="ga", alpha3="gle"),
    Language(english="Galician", alpha2="gl", alpha3="glg"),
    Language(english="Manx", alpha2="gv", alpha3="glv"),
    Language(english="Greek, Modern (1453-)", alpha2="el", alpha3="gre"),
    Language(english="Guarani", alpha2="gn", alpha3="grn"),
    Language(english="Gujarati", alpha2="gu", alpha3="guj"),
    Language(english="Haitian; Haitian Creole", alpha2="ht", alpha3="hat"),
    Language(english="Hausa", alpha2="ha", alpha3="hau"),
    Language(english="Hebrew", alpha2="he", alpha3="heb"),
    Language(english="Herero", alpha2="hz", alpha3="her"),
    Language(english="Hindi", alpha2="hi", alpha3="hin"),
    Language(english="Hiri Motu", alpha2="ho", alpha3="hmo"),
    Language(english="Croatian", alpha2="hr", alpha3="hrv"),
    Language(english="Hungarian", alpha2="hu", alpha3="hun"),
    Language(english="Igbo", alpha2="ig", alpha3="ibo"),
    Language(english="Icelandic", alpha2="is", alpha3="ice"),
    Language(english="Ido", alpha2="io", alpha3="ido"),
    Language(english="Sichuan Yi; Nuosu", alpha2="ii", alpha3="iii"),
    Language(english="Inuktitut", alpha2="iu", alpha3="iku"),
    Language(english="Interlingue; Occidental", alpha2="ie", alpha3="ile"),
    Language(english="Interlingua (International Auxiliary Language Association)", alpha2="ia", alpha3="ina"),
    Language(english="Indonesian", alpha2="id", alpha3="ind"),
    Language(english="Inupiaq", alpha2="ik", alpha3="ipk"),
    Language(english="Italian", alpha2="it", alpha3="ita"),
    Language(english="Javanese", alpha2="jv", alpha3="jav"),
    Language(english="Japanese", alpha2="ja", alpha3="jpn"),
    Language(english="Kalaallisut; Greenlandic", alpha2="kl", alpha3="kal"),
    Language(english="Kannada", alpha2="kn", alpha3="kan"),
    Language(english="Kashmiri", alpha2="ks", alpha3="kas"),
    Language(english="Kanuri", alpha2="kr", alpha3="kau"),
    Language(english="Kazakh", alpha2="kk", alpha3="kaz"),
    Language(english="Central Khmer", alpha2="km", alpha3="khm"),
    Language(english="Kikuyu; Gikuyu", alpha2="ki", alpha3="kik"),
    Language(english="Kinyarwanda", alpha2="rw", alpha3="kin"),
    Language(english="Kirghiz; Kyrgyz", alpha2="ky", alpha3="kir"),
    Language(english="Komi", alpha2="kv", alpha3="kom"),
    Language(english="Kongo", alpha2="kg", alpha3="kon"),
    Language(english="Korean", alpha2="ko", alpha3="kor"),
    Language(english="Kuanyama; Kwanyama", alpha2="kj", alpha3="kua"),
    Language(english="Kurdish", alpha2="ku", alpha3="kur"),
    Language(english="Lao", alpha2="lo", alpha3="lao"),
    Language(english="Latin", alpha2="la", alpha3="lat"),
    Language(english="Latvian", alpha2="lv", alpha3="lav"),
    Language(english="Limburgan; Limburger; Limburgish", alpha2="li", alpha3="lim"),
    Language(english="Lingala", alpha2="ln", alpha3="lin"),
    Language(english="Lithuanian", alpha2="lt", alpha3="lit"),
    Language(english="Luxembourgish; Letzeburgesch", alpha2="lb", alpha3="ltz"),
    Language(english="Luba-Katanga", alpha2="lu", alpha3="lub"),
    Language(english="Ganda", alpha2="lg", alpha3="lug"),
    Language(english="Macedonian", alpha2="mk", alpha3="mac"),
    Language(english="Marshallese", alpha2="mh", alpha3="mah"),
    Language(english="Malayalam", alpha2="ml", alpha3="mal"),
    Language(english="Maori", alpha2="mi", alpha3="mao"),
    Language(english="Marathi", alpha2="mr", alpha3="mar"),
    Language(english="Malay", alpha2="ms", alpha3="may"),
    Language(english="Malagasy", alpha2="mg", alpha3="mlg"),
    Language(english="Maltese", alpha2="mt", alpha3="mlt"),
    Language(english="Mongolian", alpha2="mn", alpha3="mon"),
    Language(english="Nauru", alpha2="na", alpha3="nau"),
    Language(english="Navajo; Navaho", alpha2="nv", alpha3="nav"),
    Language(english="Ndebele, South; South Ndebele", alpha2="nr", alpha3="nbl"),
    Language(english="Ndebele, North; North Ndebele", alpha2="nd", alpha3="nde"),
    Language(english="Ndonga", alpha2="ng", alpha3="ndo"),
    Language(english="Nepali", alpha2="ne", alpha3="nep"),
    Language(english="Norwegian Nynorsk; Nynorsk, Norwegian", alpha2="nn", alpha3="nno"),
    Language(english="Bokm\u00e5l, Norwegian; Norwegian Bokm\u00e5l", alpha2="nb", alpha3="nob"),
    Language(english="Norwegian", alpha2="no", alpha3="nor"),
    Language(english="Chichewa; Chewa; Nyanja", alpha2="ny", alpha3="nya"),
    Language(english="Occitan (post 1500)", alpha2="oc", alpha3="oci"),
    Language(english="Ojibwa", alpha2="oj", alpha3="oji"),
    Language(english="Oriya", alpha2="or", alpha3="ori"),
    Language(english="Oromo", alpha2="om", alpha3="orm"),
    Language(english="Ossetian; Ossetic", alpha2="os", alpha3="oss"),
    Language(english="Panjabi; Punjabi", alpha2="pa", alpha3="pan"),
    Language(english="Persian", alpha2="fa", alpha3="per"),
    Language(english="Pali", alpha2="pi", alpha3="pli"),
    Language(english="Polish", alpha2="pl", alpha3="pol"),
    Language(english="Portuguese", alpha2="pt", alpha3="por"),
    Language(english="Pushto; Pashto", alpha2="ps", alpha3="pus"),
    Language(english="Quechua", alpha2="qu", alpha3="que"),
    Language(english="Romansh", alpha2="rm", alpha3="roh"),
    Language(english="Romanian; Moldavian; Moldovan", alpha2="ro", alpha3="rum"),
    Language(english="Rundi", alpha2="rn", alpha3="run"),
    Language(english="Russian", alpha2="ru", alpha3="rus"),
    Language(english="Sango", alpha2="sg", alpha3="sag"),
    Language(english="Sanskrit", alpha2="sa", alpha3="san"),
    Language(english="Sinhala; Sinhalese", alpha2="si", alpha3="sin"),
    Language(english="Slovak", alpha2="sk", alpha3="slo"),
    Language(english="Slovenian", alpha2="sl", alpha3="slv"),
    Language(english="Northern Sami", alpha2="se", alpha3="sme"),
    Language(english="Samoan", alpha2="sm", alpha3="smo"),
    Language(english="Shona", alpha2="sn", alpha3="sna"),
    Language(english="Sindhi", alpha2="sd", alpha3="snd"),
    Language(english="Somali", alpha2="so", alpha3="som"),
    Language(english="Sotho, Southern", alpha2="st", alpha3="sot"),
    Language(english="Spanish; Castilian", alpha2="es", alpha3="spa"),
    Language(english="Sardinian", alpha2="sc", alpha3="srd"),
    Language(english="Serbian", alpha2="sr", alpha3="srp"),
    Language(english="Swati", alpha2="ss", alpha3="ssw"),
    Language(english="Sundanese", alpha2="su", alpha3="sun"),
    Language(english="Swahili", alpha2="sw", alpha3="swa"),
    Language(english="Swedish", alpha2="sv", alpha3="swe"),
    Language(english="Tahitian", alpha2="ty", alpha3="tah"),
    Language(english="Tamil", alpha2="ta", alpha3="tam"),
    Language(english="Tatar", alpha2="tt", alpha3="tat"),
    Language(english="Telugu", alpha2="te", alpha3="tel"),
    Language(english="Tajik", alpha2="tg", alpha3="tgk"),
    Language(english="Tagalog", alpha2="tl", alpha3="tgl"),
    Language(english="Thai", alpha2="th", alpha3="tha"),
    Language(english="Tibetan", alpha2="bo", alpha3="tib"),
    Language(english="Tigrinya", alpha2="ti", alpha3="tir"),
    Language(english="Tonga (Tonga Islands)", alpha2="to", alpha3="ton"),
    Language(english="Tswana", alpha2="tn", alpha3="tsn"),
    Language(english="Tsonga", alpha2="ts", alpha3="tso"),
    Language(english="Turkmen", alpha2="tk", alpha3="tuk"),
    Language(english="Turkish", alpha2="tr", alpha3="tur"),
    Language(english="Twi", alpha2="tw", alpha3="twi"),
    Language(english="Uighur; Uyghur", alpha2="ug", alpha3="uig"),
    Language(english="Ukrainian", alpha2="uk", alpha3="ukr"),
    Language(english="Urdu", alpha2="ur", alpha3="urd"),
    Language(english="Uzbek", alpha2="uz", alpha3="uzb"),
    Language(english="Venda", alpha2="ve", alpha3="ven"),
    Language(english="Vietnamese", alpha2="vi", alpha3="vie"),
    Language(english="Volap\u00fck", alpha2="vo", alpha3="vol"),
    Language(english="Welsh", alpha2="cy", alpha3="wel"),
    Language(english="Walloon", alpha2="wa", alpha3="wln"),
    Language(english="Wolof", alpha2="wo", alpha3="wol"),
    Language(english="Xhosa", alpha2="xh", alpha3="xho"),
    Language(english="Yiddish", alpha2="yi", alpha3="yid"),
    Language(english="Yoruba", alpha2="yo", alpha3="yor"),
    Language(english="Zhuang; Chuang", alpha2="za", alpha3="zha"),
    Language(english="Zulu", alpha2="zu", alpha3="zul"),
]


class Languages:
    @classmethod
    def get_choices(cls) -> List[Dict[str, Any]]:
        return [
            {
                "label": {"English(EN)": language.english},
                "value": language.alpha2,
            }
            for language in LANGUAGES
        ]

    @classmethod
    def get_tuple(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((lang.alpha2, lang.english) for lang in LANGUAGES)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        return any(code in (language.alpha2, language.alpha3) for language in LANGUAGES)

    @classmethod
    def filter_by_name(cls, name: str) -> List[Language]:
        return [language for language in LANGUAGES if name.lower() in language.english.lower()]
