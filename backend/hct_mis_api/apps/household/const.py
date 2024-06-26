from django.utils.translation import gettext_lazy as _

from django_countries.data import COUNTRIES

NATIONALITIES = (
    ("AF", _("Afghan")),
    ("AL", _("Albanian")),
    ("DZ", _("Algerian")),
    ("AD", _("Andorran")),
    ("AO", _("Angolan")),
    ("AR", _("Argentinian")),
    ("AM", _("Armenian")),
    ("A", _("Australian")),
    ("AT", _("Austrian")),
    ("AZ", _("Azerbaijani")),
    ("BS", _("Bahamian")),
    ("BH", _("Bahraini")),
    ("BD", _("Bangladeshi")),
    ("BB", _("Barbadian")),
    ("BY", _("Belorussian")),
    ("BE", _("Belgian")),
    ("BZ", _("Belizian")),
    ("BJ", _("Beninese")),
    ("BT", _("Bhutanese")),
    ("BO", _("Bolivian")),
    ("BA", _("Bosnian")),
    ("BW", _("Botswanan")),
    ("BR", _("Brazilian")),
    ("GB", _("British")),
    ("BN", _("Bruneian")),
    ("BG", _("Bulgarian")),
    ("BF", _("Burkinese")),
    ("MM", _("Burmese")),
    ("BF", _("Burundian")),
    ("BI", _("Cambodian")),
    ("CM", _("Cameroonian")),
    ("CA", _("Canadian")),
    ("CV", _("Cape Verdean")),
    ("TD", _("Chadian")),
    ("CL", _("Chilean")),
    ("CN", _("Chinese")),
    ("CO", _("Colombian")),
    ("CG", _("Congolese")),
    ("CR", _("Costa Rican")),
    ("HR", _("Croatian")),
    ("C", _("Cuban")),
    ("CY", _("Cypriot")),
    ("CZ", _("Czech")),
    ("DK", _("Danish")),
    ("DJ", _("Djiboutian")),
    ("DM", _("Dominican")),
    ("DO", _("Dominican")),
    ("EC", _("Ecuadorean")),
    ("EG", _("Egyptian")),
    ("SV", _("Salvadorean")),
    ("GB", _("English")),
    ("ER", _("Eritrean")),
    ("EE", _("Estonian")),
    ("ET", _("Ethiopian")),
    ("FJ", _("Fijian")),
    ("FI", _("Finnish")),
    ("FR", _("French")),
    ("GA", _("Gabonese")),
    ("GM", _("Gambian")),
    ("GE", _("Georgian")),
    ("DE", _("German")),
    ("GH", _("Ghanaian")),
    ("GR", _("Greek")),
    ("GD", _("Grenadian")),
    ("GT", _("Guatemalan")),
    ("GQ", _("Guinean")),
    ("GY", _("Guyanese")),
    ("HT", _("Haitian")),
    ("NL", _("Dutch")),
    ("HN", _("Honduran")),
    ("H", _("Hungarian")),
    ("IS", _("Icelandic")),
    ("IO", _("Indian")),
    ("ID", _("Indonesian")),
    ("IR", _("Iranian")),
    ("IQ", _("Iraqi")),
    ("IE", _("Irish")),
    ("IL", _("Israeli")),
    ("IT", _("Italian")),
    ("JM", _("Jamaican")),
    ("JP", _("Japanese")),
    ("JO", _("Jordanian")),
    ("KZ", _("Kazakh")),
    ("KE", _("Kenyan")),
    ("KW", _("Kuwaiti")),
    ("LA", _("Laotian")),
    ("LV", _("Latvian")),
    ("LB", _("Lebanese")),
    ("LR", _("Liberian")),
    ("LY", _("Libyan")),
    ("LT", _("Lithuanian")),
    ("MK", _("Macedonian")),
    ("MG", _("Malagasay")),
    ("MW", _("Malawian")),
    ("MY", _("Malaysian")),
    ("MV", _("Maldivian")),
    ("ML", _("Malian")),
    ("MT", _("Maltese")),
    ("MR", _("Mauritanian")),
    ("M", _("Mauritian")),
    ("MX", _("Mexican")),
    ("MD", _("Moldovan")),
    ("MC", _("Monacan")),
    ("MN", _("Mongolian")),
    ("ME", _("Montenegrin")),
    ("MA", _("Moroccan")),
    ("MZ", _("Mozambican")),
    ("NA", _("Namibian")),
    ("NP", _("Nepalese")),
    ("NI", _("Nicaraguan")),
    ("NE", _("Nigerien")),
    ("NG", _("Nigerian")),
    ("KP", _("North Korean")),
    ("NO", _("Norwegian")),
    ("OM", _("Omani")),
    ("PK", _("Pakistani")),
    ("PA", _("Panamanian")),
    ("PG", _("Guinean")),
    ("PY", _("Paraguayan")),
    ("PE", _("Peruvian")),
    ("PH", _("Philippine")),
    ("PL", _("Polish")),
    ("PT", _("Portuguese")),
    ("QA", _("Qatari")),
    ("RO", _("Romanian")),
    ("R", _("Russian")),
    ("RW", _("Rwandan")),
    ("SA", _("Saudi")),
    ("AE", _("Scottish")),
    ("SN", _("Senegalese")),
    ("RS", _("Serbian")),
    ("SC", _("Seychellois")),
    ("SL", _("Sierra Leonian")),
    ("SG", _("Singaporean")),
    ("SK", _("Slovak")),
    ("SI", _("Slovenian")),
    ("SO", _("Somali")),
    ("ZA", _("South African")),
    ("KR", _("South Korean")),
    ("ES", _("Spanish")),
    ("LK", _("Sri Lankan")),
    ("SD", _("Sudanese")),
    ("SR", _("Surinamese")),
    ("SZ", _("Swazi")),
    ("SE", _("Swedish")),
    ("CH", _("Swiss")),
    ("SY", _("Syrian")),
    ("TW", _("Taiwanese")),
    ("TJ", _("Tadjik")),
    ("TZ", _("Tanzanian")),
    ("TH", _("Thai")),
    ("TG", _("Togolese")),
    ("TT", _("Trinidadian")),
    ("TN", _("Tunisian")),
    ("TR", _("Turkish")),
    ("TM", _("Turkmen")),
    ("TV", _("Tuvaluan")),
    ("UG", _("Ugandan")),
    ("UA", _("Ukrainian")),
    ("UY", _("Uruguayan")),
    ("UZ", _("Uzbek")),
    ("V", _("Vanuatuan")),
    ("VE", _("Venezuelan")),
    ("VN", _("Vietnamese")),
    ("GB", _("Welsh")),
    ("YE", _("Yemeni")),
    ("ZM", _("Zambian")),
    ("ZW", _("Zimbabwean")),
)

COUNTRIES_NAME_ALPHA2 = {str(name): code for code, name in COUNTRIES.items()}
