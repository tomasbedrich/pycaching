import re

__countries__ = {
    2: 'United States',
    3: 'Australia',
    4: 'Belgium',
    5: 'Canada',
    6: 'Chile',
    7: 'Ireland',
    8: 'Luxembourg',
    9: 'New Zealand',
    10: 'Sweden',
    11: 'United Kingdom',
    12: 'Afghanistan',
    13: 'Antigua and Barbuda',
    14: 'Algeria',
    15: 'Armenia',
    16: 'Andorra',
    17: 'Angola',
    18: 'Antarctica',
    19: 'Argentina',
    20: 'Aruba',
    21: 'Azerbaijan',
    23: 'Bahamas',
    24: 'Bangladesh',
    25: 'Barbados',
    26: 'Benin',
    27: 'Bermuda',
    29: 'Bahrain',
    30: 'Bhutan',
    31: 'Belize',
    32: 'Bolivia',
    33: 'Botswana',
    34: 'Brazil',
    35: 'Burundi',
    36: 'Brunei',
    37: 'Bulgaria',
    39: 'British Virgin Islands',
    40: 'Belarus',
    41: 'New Caledonia',
    42: 'Cambodia',
    43: 'Cameroon',
    44: 'Cayman Islands',
    46: 'Central African Republic',
    47: 'China',
    48: 'Cook Islands',
    49: 'Colombia',
    50: 'Comoros',
    51: 'Congo',
    52: 'Costa Rica',
    53: 'Croatia',
    54: 'Curaçao',
    55: 'Cyprus',
    56: 'Czechia',
    57: 'Denmark',
    58: 'Djibouti',
    59: 'Dominica',
    60: 'Dominican Republic',
    61: 'Ecuador',
    62: 'Equatorial Guinea',
    63: 'Egypt',
    64: 'El Salvador',
    65: 'Eritrea',
    66: 'Estonia',
    67: 'Ethiopia',
    68: 'Faroe Islands',
    69: 'Falkland Islands',
    70: 'French Guiana',
    71: 'Fiji',
    72: 'Finland',
    73: 'France',
    74: 'French Polynesia',
    75: 'Gabon',
    76: 'Gambia',
    77: 'Guadeloupe',
    78: 'Georgia',
    79: 'Germany',
    80: 'Gibraltar',
    81: 'Grenada',
    82: 'Greece',
    83: 'Greenland',
    84: 'Guatemala',
    85: 'Guinea-Bissau',
    86: 'Guernsey',
    87: 'Guyana',
    89: 'Haiti',
    90: 'Honduras',
    91: 'Hong Kong',
    92: 'Hungary',
    93: 'Iceland',
    94: 'India',
    95: 'Indonesia',
    96: 'Iran',
    97: 'Iraq',
    98: 'Israel',
    99: 'Italy',
    100: 'Côte d\'Ivoire',
    101: 'Jamaica',
    102: 'Jersey',
    103: 'Jordan',
    104: 'Japan',
    106: 'Kazakhstan',
    107: 'Kenya',
    108: 'Kyrgyzstan',
    109: 'Kiribati',
    110: 'Laos',
    111: 'Latvia',
    112: 'Libya',
    113: 'Lebanon',
    114: 'Lesotho',
    115: 'Liberia',
    116: 'Liechtenstein',
    117: 'Lithuania',
    119: 'Madagascar',
    121: 'Malaysia',
    122: 'Martinique',
    123: 'Mauritania',
    124: 'Maldives',
    125: 'North Macedonia',
    127: 'Mali',
    128: 'Malta',
    129: 'Malawi',
    130: 'Monaco',
    131: 'Mongolia',
    132: 'Morocco',
    133: 'Mozambique',
    134: 'Mauritius',
    135: 'Montserrat',
    136: 'Myanmar',
    137: 'Namibia',
    138: 'Nauru',
    140: 'Nepal',
    141: 'Netherlands',
    143: 'Niger',
    144: 'Nicaragua',
    145: 'Nigeria',
    146: 'North Korea',
    147: 'Norway',
    149: 'Niue',
    150: 'Oman',
    151: 'Pakistan',
    152: 'Panama',
    153: 'Peru',
    154: 'Philippines',
    155: 'Pitcairn',
    156: 'Papua New Guinea',
    158: 'Poland',
    159: 'Portugal',
    160: 'Qatar',
    161: 'Réunion',
    162: 'Romania',
    163: 'Russia',
    164: 'Rwanda',
    165: 'South Africa',
    166: 'Saudi Arabia',
    167: 'Senegal',
    168: 'Seychelles',
    169: 'Saint Barthélemy',
    171: 'Saint Helena',
    173: 'Saint Lucia',
    174: 'Saint Martin',
    175: 'Saint Pierre and Miquelon',
    176: 'Sao Tome and Principe',
    177: 'Saint Vincent and the Grenadines',
    178: 'Sierra Leone',
    179: 'Singapore',
    180: 'South Korea',
    181: 'Slovenia',
    182: 'Slovakia',
    183: 'San Marino',
    184: 'Solomon Islands',
    185: 'Somalia',
    186: 'Spain',
    187: 'Sri Lanka',
    188: 'Sudan',
    189: 'Suriname',
    190: 'Swaziland',
    192: 'Switzerland',
    193: 'Syria',
    194: 'Taiwan',
    195: 'Tajikistan',
    196: 'Tanzania',
    197: 'Turks and Caicos Islands',
    198: 'Thailand',
    199: 'Turkmenistan',
    200: 'Togo',
    201: 'Tonga',
    202: 'Trinidad and Tobago',
    203: 'Tunisia',
    204: 'Turkey',
    205: 'Tuvalu',
    206: 'United Arab Emirates',
    207: 'Ukraine',
    208: 'Uganda',
    210: 'Uruguay',
    211: 'Uzbekistan',
    212: 'Vanuatu',
    213: 'Vatican City State',
    214: 'Venezuela',
    215: 'Vietnam',
    216: 'Burkina Faso',
    217: 'Samoa',
    218: 'Wallis and Futuna Islands',
    220: 'Yemen',
    222: 'Serbia',
    224: 'Zambia',
    225: 'Zimbabwe',
    226: 'Puerto Rico',
    227: 'Austria',
    228: 'Mexico',
    229: 'Guam',
    234: 'Bosnia and Herzegovina',
    235: 'US Virgin Islands',
    236: 'Northern Mariana Islands',
    237: 'Moldova',
    238: 'Cuba',
    239: 'Cabo Verde',
    240: 'Marshall Islands',
    241: 'Kuwait',
    242: 'Micronesia',
    243: 'Isle of Man',
    244: 'Albania',
    245: 'American Samoa',
    246: 'Anguilla',
    247: 'Bouvet Island',
    248: 'British Indian Ocean Territory',
    249: 'Chad',
    250: 'Christmas Island',
    251: 'Cocos (Keeling) Islands',
    252: 'Timor-Leste',
    253: 'French Southern and Antarctic Territories',
    254: 'Ghana',
    255: 'Guinea',
    256: 'Heard Island and McDonald Islands',
    257: 'Democratic Republic of the Congo',
    258: 'Macao',
    259: 'Mayotte',
    260: 'Norfolk Island',
    261: 'Palau',
    262: 'Paraguay',
    264: 'Saint Kitts and Nevis',
    267: 'South Georgia and the South Sandwich Islands',
    268: 'Svalbard and Jan Mayen Islands',
    269: 'Tokelau',
    270: 'US Minor Outlying Islands',
    271: 'Western Sahara',
    272: 'Aland Islands',
    274: 'Montenegro',
    276: 'Palestine',
    278: 'South Sudan',
    279: 'Bonaire, Sint Eustatius and Saba',
    280: 'Sark',
    281: 'Sint Maarten',
}
__states__ = {
    2: "Alaska",
    3: "Arizona",
    4: "Arkansas",
    5: "California",
    6: "Colorado",
    7: "Connecticut",
    8: "District of Columbia",
    9: "Delaware",
    10: "Florida",
    11: "Georgia",
    12: "Hawaii",
    13: "Idaho",
    14: "Illinois",
    15: "Indiana",
    16: "Iowa",
    17: "Kansas",
    18: "Kentucky",
    19: "Louisiana",
    20: "Maine",
    21: "Maryland",
    22: "Massachusetts",
    23: "Michigan",
    24: "Minnesota",
    25: "Mississippi",
    26: "Missouri",
    27: "Montana",
    28: "Nebraska",
    29: "Nevada",
    30: "New Hampshire",
    31: "New Jersey",
    32: "New Mexico",
    33: "New York",
    34: "North Carolina",
    35: "North Dakota",
    36: "Ohio",
    37: "Oklahoma",
    38: "Oregon",
    39: "Pennsylvania",
    40: "Rhode Island",
    41: "South Carolina",
    42: "South Dakota",
    43: "Tennessee",
    44: "Texas",
    45: "Utah",
    46: "Vermont",
    47: "Virginia",
    48: "Washington",
    49: "West Virginia",
    50: "Wisconsin",
    51: "Wyoming",
    52: "New South Wales",
    53: "Victoria",
    54: "Queensland",
    55: "South Australia",
    56: "Western Australia",
    57: "Tasmania",
    58: "Northern Territory",
    59: "Australian Capital Territory",
    60: "Alabama",
    62: "Québec",
    63: "Alberta",
    64: "British Columbia",
    65: "Manitoba",
    66: "New Brunswick",
    67: "Newfoundland and Labrador",
    68: "Nova Scotia",
    69: "Ontario",
    70: "Prince Edward Island",
    71: "Saskatchewan",
    72: "Northwest Territories",
    73: "Nunavut",
    74: "Yukon Territory",
    76: "Oost-Vlaanderen",
    78: "Vlaams-Brabant",
    80: "Liège",
    81: "Namur",
    82: "North Island",
    86: "South Island",
    87: "Antwerpen",
    88: "Hainaut",
    89: "Limburg",
    90: "Luxembourg",
    91: "Brabant wallon",
    92: "West-Vlaanderen",
    93: "Brussels",
    95: "Aveiro",
    96: "Beja",
    97: "Braga",
    98: "Bragança",
    99: "Castelo Branco",
    100: "Coimbra",
    101: "Évora",
    102: "Faro",
    103: "Guarda",
    104: "Leiria",
    105: "Lisboa",
    106: "Portalegre",
    107: "Porto",
    108: "Santarém",
    109: "Setúbal",
    110: "Viana do Castelo",
    111: "Viseu",
    112: "Vila Real",
    113: "Arquipélago da Madeira",
    114: "Arquipélago dos Açores",
    115: "Castilla y León",
    116: "Andalucía",
    117: "Castilla-La Mancha",
    119: "Aragón",
    120: "Extremadura",
    121: "Cataluña",
    122: "Galicia",
    123: "Comunidad Valenciana",
    124: "Región de Murcia",
    125: "Principado de Asturias",
    126: "Comunidad Foral de Navarra",
    127: "Comunidad de Madrid",
    128: "Islas Canarias",
    129: "País Vasco",
    130: "Cantabria",
    131: "La Rioja",
    132: "Islas Baleares",
    133: "Ceuta",
    134: "Melilla",
    135: "Baden-Württemberg",
    136: "Bayern",
    137: "Berlin",
    138: "Brandenburg",
    139: "Bremen",
    140: "Hamburg",
    141: "Mecklenburg-Vorpommern",
    142: "Niedersachsen",
    143: "Nordrhein-Westfalen",
    144: "Rheinland-Pfalz",
    145: "Saarland",
    146: "Sachsen",
    147: "Sachsen-Anhalt",
    148: "Schleswig-Holstein",
    149: "Thüringen",
    150: "Hessen",
    152: "Western Cape",
    153: "Eastern Cape",
    154: "Northern Cape",
    155: "Mpumalanga",
    156: "North West",
    157: "Kwazulu Natal",
    158: "Limpopo",
    159: "Gauteng",
    160: "Free State",
    162: "Acre",
    163: "Alagoas",
    164: "Amapá",
    165: "Amazonas",
    166: "Bahia",
    167: "Ceará",
    168: "Distrito Federal",
    169: "Espírito Santo",
    170: "Goiás",
    171: "Maranhão",
    172: "Mato Grosso",
    173: "Mato Grosso do Sul",
    174: "Minas Gerais",
    175: "Pará",
    176: "Paraíba",
    177: "Paraná",
    178: "Pernambuco",
    179: "Piauí",
    180: "Rio de Janeiro",
    181: "Rio Grande do Norte",
    182: "Rio Grande do Sul",
    183: "Rondônia",
    184: "Roraima",
    185: "Santa Catarina",
    186: "São Paulo",
    187: "Sergipe",
    188: "Tocantins",
    189: "Abruzzo",
    190: "Basilicata",
    192: "Calabria",
    193: "Campania",
    194: "Emilia–Romagna",
    195: "Friuli–Venezia Giulia",
    196: "Lazio",
    197: "Liguria",
    198: "Lombardia",
    199: "Marche",
    200: "Molise",
    201: "Piemonte",
    202: "Puglia",
    203: "Sardegna",
    204: "Sicilia",
    205: "Toscana",
    206: "Trentino–Alto Adige",
    207: "Umbria",
    208: "Valle d'Aosta",
    209: "Veneto",
    210: "Northern Scotland",
    211: "Southern Scotland",
    212: "North East England",
    213: "North West England",
    214: "Yorkshire",
    215: "East Midlands",
    216: "West Midlands",
    217: "North Wales",
    218: "South Wales",
    219: "Eastern England",
    220: "London",
    221: "Southern England",
    222: "South West England",
    223: "South East England",
    224: "Ulster",
    225: "Munster",
    226: "Dublin",
    227: "Connacht",
    228: "Leinster",
    241: "Oslo",
    249: "Rogaland",
    252: "Møre og Romsdal",
    255: "Nordland",
    258: "Burgenland",
    259: "Kärnten",
    260: "Niederösterreich",
    261: "Oberösterreich",
    262: "Salzburg",
    263: "Steiermark",
    264: "Tirol",
    265: "Vorarlberg",
    273: "Jihomoravský kraj",
    274: "Jihočeský kraj",
    275: "Královéhradecký kraj",
    276: "Karlovarský kraj",
    277: "Liberecký kraj",
    278: "Olomoucký kraj",
    279: "Moravskoslezský kraj",
    280: "Pardubický kraj",
    281: "Plzeňský kraj",
    282: "Středočeský kraj",
    283: "Ústecký kraj",
    284: "Kraj Vysočina",
    285: "Zlínský kraj",
    286: "Hlavní město Praha",
    287: "Banskobystrický kraj",
    288: "Bratislavský kraj",
    289: "Košický kraj",
    290: "Nitriansky kraj",
    291: "Prešovský kraj",
    292: "Trenčiansky kraj",
    293: "Trnavský kraj",
    294: "Žilinský kraj",
    295: "Wien",
    296: "Seoul",
    297: "Busan",
    298: "Daegu",
    299: "Incheon",
    300: "Gwangju",
    301: "Daejeon",
    302: "Ulsan",
    303: "Gyeonggido",
    304: "Gangwondo",
    305: "Chungcheong buk do",
    306: "Chungcheong nam do",
    307: "Jeolla buk do",
    308: "Jeolla nam do",
    309: "Gyeongsang buk do",
    310: "Gyeongsang nam do",
    311: "Jejudo",
    312: "Aichi",
    313: "Aomori",
    314: "Chiba",
    315: "Ehime",
    316: "Fukui",
    317: "Fukuoka",
    318: "Fukushima",
    319: "Gifu",
    320: "Gunma",
    321: "Hiroshima",
    322: "Hokkaido",
    323: "Hyogo",
    324: "Ibaraki",
    325: "Ishikawa",
    326: "Iwate",
    327: "Kagawa",
    328: "Kagoshima",
    329: "Kanagawa",
    330: "Kochi",
    331: "Kumamoto",
    332: "Kyoto",
    333: "Mie",
    334: "Miyagi",
    335: "Miyazaki",
    336: "Nagano",
    337: "Nagasaki",
    338: "Nara",
    339: "Niigata",
    340: "Oita",
    341: "Okayama",
    342: "Okinawa",
    343: "Osaka",
    344: "Saga",
    345: "Saitama",
    346: "Shiga",
    347: "Shimane",
    348: "Shizuoka",
    349: "Tochigi",
    350: "Tokushima",
    351: "Tokyo",
    352: "Tottori",
    353: "Toyama",
    354: "Wakayama",
    355: "Yamagata",
    356: "Yamaguchi",
    357: "Yamanashi",
    359: "Blekinge",
    360: "Dalarna",
    361: "Gotland",
    362: "Gävleborg",
    363: "Halland",
    364: "Jämtland",
    365: "Jönköping",
    366: "Kalmar",
    367: "Kronoberg",
    368: "Norrbotten",
    369: "Skåne",
    370: "Stockholm",
    371: "Södermanland",
    372: "Uppsala",
    373: "Värmland",
    374: "Västerbotten",
    375: "Västernorrland",
    376: "Västmanland",
    377: "Västra Götaland",
    378: "Örebro",
    379: "Östergötland",
    383: "Akita",
    384: "Groningen",
    385: "Drenthe",
    386: "Overijssel",
    387: "Gelderland",
    388: "Utrecht",
    389: "Noord-Holland",
    390: "Zuid-Holland",
    391: "Zeeland",
    392: "Noord-Brabant",
    393: "Limburg",
    394: "Friesland",
    395: "Flevoland",
    396: "Dolnośląskie",
    397: "Kujawsko-Pomorskie",
    398: "Lubelskie",
    399: "Lubuskie",
    400: "Łódzkie",
    401: "Małopolskie",
    402: "Mazowieckie",
    403: "Opolskie",
    404: "Podkarpackie",
    405: "Podlaskie",
    406: "Pomorskie",
    407: "Śląskie",
    408: "Świętokrzyskie",
    409: "Warmińsko-Mazurskie",
    410: "Wielkopolskie",
    411: "Zachodniopomorskie",
    416: "Bretagne",
    417: "Centre-Val-de-Loire",
    419: "Corse",
    422: "Île-de-France",
    428: "Pays de la Loire",
    431: "Provence-Alpes-Côte d'Azur",
    434: "Bács-Kiskun",
    435: "Baranya",
    436: "Békés",
    437: "Borsod-Abaúj-Zemplén",
    438: "Budapest",
    439: "Csongrád",
    440: "Fejér",
    441: "Gyor-Moson-Sopron",
    442: "Hajdú-Bihar",
    443: "Heves",
    444: "Jász-Nagykun-Szolnok",
    445: "Komárom-Esztergom",
    446: "Nógrád",
    447: "Pest",
    448: "Somogy",
    449: "Szabolcs-Szatmár-Bereg",
    450: "Tolna",
    451: "Vas",
    452: "Veszprém",
    453: "Zala",
    454: "Aguascalientes",
    455: "Baja California",
    456: "Baja California Sur",
    457: "Campeche",
    458: "Chiapas",
    459: "Chihuahua",
    460: "Coahuila",
    461: "Colima",
    462: "Distrito Federal",
    463: "Durango",
    464: "Guanajuato",
    465: "Guerrero",
    466: "Hidalgo",
    467: "Jalisco",
    468: "México",
    469: "Michoacán",
    470: "Morelos",
    471: "Nayarit",
    472: "Nuevo León",
    473: "Oaxaca",
    474: "Puebla",
    475: "Querétaro",
    476: "Quintana Roo",
    477: "San Luis Potosí",
    478: "Sinaloa",
    479: "Sonora",
    480: "Tabasco",
    481: "Tamaulipas",
    482: "Tlaxcala",
    483: "Veracruz",
    484: "Yucatán",
    485: "Zacatecas",
    486: "Chatham Islands",
    487: "Normandie",
    488: "Bourgogne-Franche-Comté",
    489: "Grand-Est",
    490: "Occitanie",
    491: "Nouvelle-Aquitaine",
    492: "Hauts-de-France",
    493: "Auvergne-Rhône-Alpes",
    494: "Trøndelag",
    495: "Sejong",
    497: "Aargau",
    498: "Appenzell Ausserrhoden",
    499: "Appenzell Innerrhoden",
    500: "Basel Landschaft",
    501: "Basel Stadt",
    502: "Bern",
    503: "Fribourg",
    504: "Genève",
    505: "Glarus",
    506: "Graubünden",
    507: "Jura",
    508: "Luzern",
    509: "Neuchâtel",
    510: "Nidwalden",
    511: "Obwalden",
    512: "Schaffhausen",
    513: "Schwyz",
    514: "Solothurn",
    515: "St. Gallen",
    516: "Thurgau",
    517: "Ticino",
    518: "Uri",
    519: "Valais",
    520: "Vaud",
    521: "Zug",
    522: "Zürich",
    523: "Bonaire",
    524: "Sint Eustatius",
    525: "Saba",
    526: "Vestland",
    527: "Agder",
    528: "Vestfold og Telemark",
    529: "Innlandet",
    530: "Viken",
    531: "Troms og Finnmark"
}
__state_to_country__ = {
    2: 2,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    7: 2,
    8: 2,
    9: 2,
    10: 2,
    11: 2,
    12: 2,
    13: 2,
    14: 2,
    15: 2,
    16: 2,
    17: 2,
    18: 2,
    19: 2,
    20: 2,
    21: 2,
    22: 2,
    23: 2,
    24: 2,
    25: 2,
    26: 2,
    27: 2,
    28: 2,
    29: 2,
    30: 2,
    31: 2,
    32: 2,
    33: 2,
    34: 2,
    35: 2,
    36: 2,
    37: 2,
    38: 2,
    39: 2,
    40: 2,
    41: 2,
    42: 2,
    43: 2,
    44: 2,
    45: 2,
    46: 2,
    47: 2,
    48: 2,
    49: 2,
    50: 2,
    51: 2,
    52: 3,
    53: 3,
    54: 3,
    55: 3,
    56: 3,
    57: 3,
    58: 3,
    59: 3,
    60: 2,
    62: 5,
    63: 5,
    64: 5,
    65: 5,
    66: 5,
    67: 5,
    68: 5,
    69: 5,
    70: 5,
    71: 5,
    72: 5,
    73: 5,
    74: 5,
    76: 4,
    78: 4,
    80: 4,
    81: 4,
    82: 9,
    86: 9,
    87: 4,
    88: 4,
    89: 4,
    90: 4,
    91: 4,
    92: 4,
    93: 4,
    95: 159,
    96: 159,
    97: 159,
    98: 159,
    99: 159,
    100: 159,
    101: 159,
    102: 159,
    103: 159,
    104: 159,
    105: 159,
    106: 159,
    107: 159,
    108: 159,
    109: 159,
    110: 159,
    111: 159,
    112: 159,
    113: 159,
    114: 159,
    115: 186,
    116: 186,
    117: 186,
    119: 186,
    120: 186,
    121: 186,
    122: 186,
    123: 186,
    124: 186,
    125: 186,
    126: 186,
    127: 186,
    128: 186,
    129: 186,
    130: 186,
    131: 186,
    132: 186,
    133: 186,
    134: 186,
    135: 79,
    136: 79,
    137: 79,
    138: 79,
    139: 79,
    140: 79,
    141: 79,
    142: 79,
    143: 79,
    144: 79,
    145: 79,
    146: 79,
    147: 79,
    148: 79,
    149: 79,
    150: 79,
    152: 165,
    153: 165,
    154: 165,
    155: 165,
    156: 165,
    157: 165,
    158: 165,
    159: 165,
    160: 165,
    162: 34,
    163: 34,
    164: 34,
    165: 34,
    166: 34,
    167: 34,
    168: 34,
    169: 34,
    170: 34,
    171: 34,
    172: 34,
    173: 34,
    174: 34,
    175: 34,
    176: 34,
    177: 34,
    178: 34,
    179: 34,
    180: 34,
    181: 34,
    182: 34,
    183: 34,
    184: 34,
    185: 34,
    186: 34,
    187: 34,
    188: 34,
    189: 99,
    190: 99,
    192: 99,
    193: 99,
    194: 99,
    195: 99,
    196: 99,
    197: 99,
    198: 99,
    199: 99,
    200: 99,
    201: 99,
    202: 99,
    203: 99,
    204: 99,
    205: 99,
    206: 99,
    207: 99,
    208: 99,
    209: 99,
    210: 11,
    211: 11,
    212: 11,
    213: 11,
    214: 11,
    215: 11,
    216: 11,
    217: 11,
    218: 11,
    219: 11,
    220: 11,
    221: 11,
    222: 11,
    223: 11,
    224: 7,
    225: 7,
    226: 7,
    227: 7,
    228: 7,
    241: 147,
    249: 147,
    252: 147,
    255: 147,
    258: 227,
    259: 227,
    260: 227,
    261: 227,
    262: 227,
    263: 227,
    264: 227,
    265: 227,
    273: 56,
    274: 56,
    275: 56,
    276: 56,
    277: 56,
    278: 56,
    279: 56,
    280: 56,
    281: 56,
    282: 56,
    283: 56,
    284: 56,
    285: 56,
    286: 56,
    287: 182,
    288: 182,
    289: 182,
    290: 182,
    291: 182,
    292: 182,
    293: 182,
    294: 182,
    295: 227,
    296: 180,
    297: 180,
    298: 180,
    299: 180,
    300: 180,
    301: 180,
    302: 180,
    303: 180,
    304: 180,
    305: 180,
    306: 180,
    307: 180,
    308: 180,
    309: 180,
    310: 180,
    311: 180,
    312: 104,
    313: 104,
    314: 104,
    315: 104,
    316: 104,
    317: 104,
    318: 104,
    319: 104,
    320: 104,
    321: 104,
    322: 104,
    323: 104,
    324: 104,
    325: 104,
    326: 104,
    327: 104,
    328: 104,
    329: 104,
    330: 104,
    331: 104,
    332: 104,
    333: 104,
    334: 104,
    335: 104,
    336: 104,
    337: 104,
    338: 104,
    339: 104,
    340: 104,
    341: 104,
    342: 104,
    343: 104,
    344: 104,
    345: 104,
    346: 104,
    347: 104,
    348: 104,
    349: 104,
    350: 104,
    351: 104,
    352: 104,
    353: 104,
    354: 104,
    355: 104,
    356: 104,
    357: 104,
    359: 10,
    360: 10,
    361: 10,
    362: 10,
    363: 10,
    364: 10,
    365: 10,
    366: 10,
    367: 10,
    368: 10,
    369: 10,
    370: 10,
    371: 10,
    372: 10,
    373: 10,
    374: 10,
    375: 10,
    376: 10,
    377: 10,
    378: 10,
    379: 10,
    383: 104,
    384: 141,
    385: 141,
    386: 141,
    387: 141,
    388: 141,
    389: 141,
    390: 141,
    391: 141,
    392: 141,
    393: 141,
    394: 141,
    395: 141,
    396: 158,
    397: 158,
    398: 158,
    399: 158,
    400: 158,
    401: 158,
    402: 158,
    403: 158,
    404: 158,
    405: 158,
    406: 158,
    407: 158,
    408: 158,
    409: 158,
    410: 158,
    411: 158,
    416: 73,
    417: 73,
    419: 73,
    422: 73,
    428: 73,
    431: 73,
    434: 92,
    435: 92,
    436: 92,
    437: 92,
    438: 92,
    439: 92,
    440: 92,
    441: 92,
    442: 92,
    443: 92,
    444: 92,
    445: 92,
    446: 92,
    447: 92,
    448: 92,
    449: 92,
    450: 92,
    451: 92,
    452: 92,
    453: 92,
    454: 228,
    455: 228,
    456: 228,
    457: 228,
    458: 228,
    459: 228,
    460: 228,
    461: 228,
    462: 228,
    463: 228,
    464: 228,
    465: 228,
    466: 228,
    467: 228,
    468: 228,
    469: 228,
    470: 228,
    471: 228,
    472: 228,
    473: 228,
    474: 228,
    475: 228,
    476: 228,
    477: 228,
    478: 228,
    479: 228,
    480: 228,
    481: 228,
    482: 228,
    483: 228,
    484: 228,
    485: 228,
    486: 9,
    487: 73,
    488: 73,
    489: 73,
    490: 73,
    491: 73,
    492: 73,
    493: 73,
    494: 147,
    495: 180,
    497: 192,
    498: 192,
    499: 192,
    500: 192,
    501: 192,
    502: 192,
    503: 192,
    504: 192,
    505: 192,
    506: 192,
    507: 192,
    508: 192,
    509: 192,
    510: 192,
    511: 192,
    512: 192,
    513: 192,
    514: 192,
    515: 192,
    516: 192,
    517: 192,
    518: 192,
    519: 192,
    520: 192,
    521: 192,
    522: 192,
    523: 279,
    524: 279,
    525: 279,
    526: 147,
    527: 147,
    528: 147,
    529: 147,
    530: 147,
    531: 147
}


def invert_dictionary(data):
    """Transforms a dictionary (int, string) into a dict (string, list of int)

    values are not unique, key are in lower case

    """
    inv_map = {}
    for key, value in data.items():
        inv_map[value.lower()] = inv_map.get(value.lower(), []) + [key]
    return inv_map

# https://stackoverflow.com/questions/128573/using-property-on-classmethods
class classproperty(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class CountryStateDict(object):
    _countries_id_name = __countries__
    _states_id_name = __states__
    _state_country = __state_to_country__

    @classproperty
    def countries(cls):
        return cls._countries_id_name

    @classproperty
    def states(cls):
        return cls._states_id_name

    @classproperty
    def state_country(cls):
        return cls._state_country

    @classmethod
    def dict_id_country_name(cls):
        return cls._countries_id_name

    @classmethod
    def dict_id_state_name(cls):
        return cls._states_id_name

    @classmethod
    def dict_country_name_id(cls):
        try:
            return cls._country_id_by_name
        except AttributeError:
            cls._country_id_by_name = invert_dictionary(cls._countries_id_name)
            return cls._country_id_by_name

    @classmethod
    def dict_state_name_id(cls):
        try:
            return cls._state_id_by_name
        except AttributeError:
            cls._state_id_by_name = invert_dictionary(cls._states_id_name)
            return cls._state_id_by_name

    @classmethod
    def country_name_by_id(cls, cid):
        return cls._countries_id_name[cid]

    @classmethod
    def state_name_by_id(cls, cid):
        return cls._states_id_name[cid]


class CountryStateUnknownName(ValueError):
    pass


class CountryStateUnknownCombination(ValueError):
    pass


class CountryStateAmbiguityValue(ValueError):
    pass


class CountryState:

    def __init__(self, cid=None, sid=None):
        if cid is not None and cid not in CountryStateDict.countries:
            raise ValueError(f'CountryState id={cid} unknown')
        if sid is not None and sid not in CountryStateDict.states:
            raise ValueError(f'State id={sid} unknown')
        if cid is not None and sid is not None and cid != CountryStateDict.state_country[sid]:
            raise ValueError(f'Combination of CountryState id={cid} and State id={sid} unknown')

        self._cid = CountryStateDict.state_country[sid] if (cid is None and sid is not None) else cid
        self._sid = sid

    def __str__(self):
        if self.has_state:
            return f'{self.state_name}, {self.country_name}'
        return f'{self.country_name}'

    @classmethod
    def ids_by_country_name(cls, name):
        results = CountryStateDict.dict_country_name_id().get(name.lower().strip(), [])
        return results

    @classmethod
    def ids_by_state_name(cls, name):
        results = CountryStateDict.dict_state_name_id().get(name.lower().strip(), [])
        return results

    @classmethod
    def from_string_country(cls, name):
        """Return a cache country from its country name."""
        ids = cls.ids_by_country_name(name)
        if len(ids) == 0:
            raise CountryStateUnknownName(f'CountryState {name} is unknown')
        elif len(ids) > 1:
            raise CountryStateAmbiguityValue(f'CountryState {name} is ambiguity')

        return CountryState(cid=ids[0], sid=None)

    @classmethod
    def from_string_state(cls, name):
        """Return a cache country from its state name."""
        ids = cls.ids_by_state_name(name)
        if len(ids) == 0:
            raise CountryStateUnknownName(f'State {name} is unknown')
        elif len(ids) > 1:
            raise CountryStateAmbiguityValue(f'State {name} is ambiguity')

        return CountryState(cid=None, sid=ids[0])

    @classmethod
    def from_string_country_state(cls, token):
        if len(token) < 2:
            raise ValueError(f'Combination {token} is unknown')  # TODO fehlermeldung

        cid = cls.ids_by_country_name(token[1])
        sids = cls.ids_by_state_name(token[0])

        if not (len(cid) == 1 and len(sids) > 0):
            cid = cls.ids_by_country_name(token[0])
            sids = cls.ids_by_state_name(token[1])

        if not (len(cid) == 1 and len(sids) > 0):
            raise CountryStateUnknownCombination(f'Combination {token} is unknown')

        for sid in sids:
            if CountryStateDict.state_country[sid] == cid[0]:
                return CountryState(cid=cid[0], sid=sid)

        raise CountryStateUnknownCombination(f'Combination {token} is unknown')

    @classmethod
    def from_string(cls, name):
        """Return a cache country from its name"""

        """
        Converts a name into a Country object

        The method try to parse the name in following order:
            State, Country
            Country, State
            Country
            State

        :param name:
        :return:
        """
        m = re.match(r'([^,]+),(.+)', name)  # split after the first
        if m:
            try:
                return cls.from_string_country_state((m[1], m[2]))
            except CountryStateUnknownName:
                pass
            except ValueError:
                pass

        try:
            return cls.from_string_country(name)
        except CountryStateUnknownName:
            pass

        try:
            return cls.from_string_state(name)
        except CountryStateUnknownName:
            pass

        raise CountryStateUnknownName(f'{name} is unknown')

    @property
    def country_id(self):
        return self._cid

    @property
    def country_name(self):
        return CountryStateDict.country_name_by_id(self._cid) if self._cid else None

    @property
    def state_id(self):
        return self._sid

    @property
    def state_name(self):
        return CountryStateDict.state_name_by_id(self._sid) if self._sid else None

    @property
    def has_state(self):
        return self._sid is not None



