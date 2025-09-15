import tkinter as tk
#from tkinter import messagebox, Text, Entry, Frame, Tk, Button
#print(tk.TkVersion)


data_dict = {
	"Countries": {
    "Afghanistan":       {
                "capital":  "Kabul",
                "currency": "Afghani",
                "language": "Dari Persian_Pashto",
          },
    "Albania":       {
                "capital":  "Tirane",
                "currency": "Lek",
                "language": "Albanian",
          },
    "Algeria":       {
                "capital":  "Algiers",
                "currency": "Algerian Dinar",
                "language": "Arabic_Tamazight_French",
          },
    "Andorra":       {
                "capital":  "Andorra la Vella",
                "currency": "Euro",
                "language": "Catalan",
          },
    "Angola":       {
                "capital":  "Luanda",
                "currency": "Kwanza",
                "language": "Portuguese",
          },
    "Antigua & Barbuda":       {
                "capital":  "Saint John's",
                "currency": "East Caribbean Dollar",
                "language": "English",
          },
    "Argentina":       {
                "capital":  "Buenos Aires",
                "currency": "Argentine Peso",
                "language": "Spanish",
          },
    "Armenia":       {
                "capital":  "Yerevan",
                "currency": "Dram",
                "language": "Armenian",
          },
    "Australia":       {
                "capital":  "Canberra",
                "currency": "Australian Dollar",
                "language": "English",
          },
    "Austria":       {
                "capital":  "Vienna",
                "currency": "Euro",
                "language": "German",
          },
    "Azerbaijan":       {
                "capital":  "Baku",
                "currency": "Manat",
                "language": "Azerbaijani",
          },
    "The Bahamas":       {
                "capital":  "Nassau",
                "currency": "Bahamian Dollar",
                "language": "English",
          },
    "Bahrain":       {
                "capital":  "Manama",
                "currency": "Bahraini Dinar",
                "language": "Arabic",
          },
    "Bangladesh":       {
                "capital":  "Dhaka",
                "currency": "Taka",
                "language": "Bangla",
          },
    "Barbados":       {
                "capital":  "Bridgetown",
                "currency": "Barbadian Dollar",
                "language": "English",
          },
    "Belarus":       {
                "capital":  "Minsk",
                "currency": "Belarusian Ruble",
                "language": "Belarusian_Russian",
          },
    "Belgium":       {
                "capital":  "Brussels",
                "currency": "Euro",
                "language": "Dutch_French_German",
          },
    "Belize":       {
                "capital":  "Belmopan",
                "currency": "Belize Dollar",
                "language": "English",
          },
    "Benin":       {
                "capital":  "Porto-Novo",
                "currency": "West African CFA Franc",
                "language": "French",
          },
    "Bhutan":       {
                "capital":  "Thimphu",
                "currency": "Ngultrum",
                "language": "Dzongkha",
          },
    "Bolivia":       {
                "capital":  "La Paz_Sucre",
                "currency": "Boliviano",
                "language": "Spanish_Quechua_Aymara",
          },
    "Bosnia and Herzegovina":       {
                "capital":  "Sarajevo",
                "currency": "Convertible Mark",
                "language": "Bosnian_Croatian_Serbian",
          },
    "Botswana":       {
                "capital":  "Gaborone",
                "currency": "Pula",
                "language": "English_Tswana",
          },
    "Brazil":       {
                "capital":  "Brasilia",
                "currency": "Real",
                "language": "Portuguese",
          },
    "Brunei":       {
                "capital":  "Bandar Seri Begawan",
                "currency": "Brunei Dollar",
                "language": "Malay",
          },
    "Bulgaria":       {
                "capital":  "Sofia",
                "currency": "Lev",
                "language": "Bulgarian",
          },
    "Burkina Faso":       {
                "capital":  "Ouagadougou",
                "currency": "West African CFA Franc",
                "language": "French",
          },
    "Burundi":       {
                "capital":  "Bujumbura",
                "currency": "Burundi Franc",
                "language": "Kirundi_French",
          },
    "Cambodia":       {
                "capital":  "Phnom Penh",
                "currency": "Riel",
                "language": "Khmer",
          },
    "Cameroon":       {
                "capital":  "Yaounde",
                "currency": "Central African CFA Franc",
                "language": "French_English",
          },
    "Canada":       {
                "capital":  "Ottawa",
                "currency": "Canadian Dollar",
                "language": "English_French",
          },
    "Cape Verde":       {
                "capital":  "Praia",
                "currency": "Cape Verdean Escudo",
                "language": "Portuguese",
          },
    "Central African Republic":       {
                "capital":  "Bangui",
                "currency": "Central African CFA Franc",
                "language": "Sango_French",
          },
    "Chad":       {
                "capital":  "N'Djamena",
                "currency": "Central African CFA Franc",
                "language": "French_Arabic",
          },
    "Chile":       {
                "capital":  "Santiago",
                "currency": "Chilean Peso",
                "language": "Spanish",
          },
    "China":       {
                "capital":  "Beijing",
                "currency": "Chinese Yuan",
                "language": "Mandarin",
          },
    "Colombia":       {
                "capital":  "Bogota",
                "currency": "Colombian Peso",
                "language": "Spanish",
          },
    "Comoros":       {
                "capital":  "Moron",
                "currency": "Comorian Franc",
                "language": "Comorian_Arabic_French",
          },
    "Democratic Republic Of the Congo":       {
                "capital":  "Kinshasa",
                "currency": "Congolese Franc",
                "language": "French",
          },
    "Republic of the Congo":       {
                "capital":  "Brazzaville",
                "currency": "Central African CFA Franc",
                "language": "French",
          },
    "Costa Rica":       {
                "capital":  "San Jose",
                "currency": "Colon",
                "language": "Spanish",
          },
    "Cote d'Ivoire (Ivory Coast)":       {
                "capital":  "Yamoussoukro_Abidjan",
                "currency": "West African CFA Franc",
                "language": "French",
          },
    "Croatia":       {
                "capital":  "Zagreb",
                "currency": "Croatian",
                "language": "Kuna",
          },
    "Cuba":       {
                "capital":  "Havana",
                "currency": "Cuban Peso",
                "language": "Spanish",
          },
    "Cyprus":       {
                "capital":  "Nicosia",
                "currency": "Euro",
                "language": "Greek_Turkish",
          },
    "Czech Republic":       {
                "capital":  "Prague",
                "currency": "Czech Koruna",
                "language": "Czech_Slovak",
          },
    "Denmark":       {
                "capital":  "Copenhagen",
                "currency": "Danish Krone",
                "language": "Danish",
          },
    "Djibouti":       {
                "capital":  "Djibouti",
                "currency": "Djiboutian Franc",
                "language": "Arabic_French",
          },
    "Dominica":       {
                "capital":  "Rosesau",
                "currency": "East Caribbean Dollar",
                "language": "English_French",
          },
    "Antillean Creole Dominican Republic":       {
                "capital":  "Santo Domingo",
                "currency": "Dominican Peso",
                "language": "Spanish",
          },
    "East Timor (Timor-Leste)":       {
                "capital":  "Dilli",
                "currency": "United States Dollar",
                "language": "Tetum_Portuguese_Indonesian",
          },
    "Ecuador":       {
                "capital":  "Quito",
                "currency": "United States Dollar",
                "language": "Spanish",
          },
    "Egypt":       {
                "capital":  "Cairo",
                "currency": "Egyptian Pound",
                "language": "Arabic",
          },
    "El Salvador":       {
                "capital":  "San Salvador",
                "currency": "United States Dollar",
                "language": "Spanish",
          },
    "Equitorial Guinea":       {
                "capital":  "Malabo",
                "currency": "Central African CFA Franc",
                "language": "Spanish_French_Portuguese",
          },
    "Eritrea":       {
                "capital":  "Asmara",
                "currency": "Nakfa",
                "language": "Arabic_Tigrinya_English",
          },
    "Estonia":       {
                "capital":  "Tallinn",
                "currency": "Estonian Kroon_Euro",
                "language": "Estonian",
          },
    "Ethiopia":       {
                "capital":  "Addis Ababa",
                "currency": "Birr",
                "language": "Amharic",
          },
    "Fiji":       {
                "capital":  "Suva",
                "currency": "Fijian Dollar",
                "language": "English_Bau Fijian_Hindi",
          },
    "Finland":       {
                "capital":  "Helsinki",
                "currency": "Euro",
                "language": "Finnish_Swedish",
          },
    "France":       {
                "capital":  "Paris",
                "currency": "Euro_CFP Franc",
                "language": "French",
          },
    "Gabon":       {
                "capital":  "Libreville",
                "currency": "Central African CFA Franc",
                "language": "French",
          },
    "The Gambia":       {
                "capital":  "Banjul",
                "currency": "Dalasi",
                "language": "English",
          },
    "Georgia":       {
                "capital":  "Tbilisi",
                "currency": "Lari",
                "language": "Georgian",
          },
    "Germany":       {
                "capital":  "Berlin",
                "currency": "Euro",
                "language": "German",
          },
    "Ghana":       {
                "capital":  "Accra",
                "currency": "Ghanaian Cedi",
                "language": "English",
          },
    "Greece":       {
                "capital":  "Athens",
                "currency": "Euro",
                "language": "Greek",
          },
    "Grenada":       {
                "capital":  "St. George's",
                "currency": "East Caribbean Dollar",
                "language": "English_Patois",
          },
    "Guatemala":       {
                "capital":  "Guatemala City",
                "currency": "Quetzal",
                "language": "Spanish",
          },
    "Guinea":       {
                "capital":  "Conakry",
                "currency": "Guinean Franc",
                "language": "French",
          },
    "Guinea-Bissau":       {
                "capital":  "Bissau",
                "currency": "West African CFA Franc",
                "language": "Portuguese",
          },
    "Guyana":       {
                "capital":  "Georgetown",
                "currency": "Guyanese Dollar",
                "language": "English",
          },
    "Haiti":       {
                "capital":  "Port-au-Prince",
                "currency": "Gourde",
                "language": "Haitian Creole_French",
          },
    "Honduras":       {
                "capital":  "Tegucigalpa",
                "currency": "Lempira",
                "language": "Spanish",
          },
    "Hungary":       {
                "capital":  "Budapest",
                "currency": "Forint",
                "language": "Hungarian",
          },
    "Iceland":       {
                "capital":  "Reykjavik",
                "currency": "Icelandic Krona",
                "language": "Icelandic",
          },
    "India":       {
                "capital":  "New Delhi",
                "currency": "Indian Rupee",
                "language": "Hindi_English",
          },
    "Indonesia":       {
                "capital":  "Jakarta",
                "currency": "Rupiah",
                "language": "Indonesian",
          },
    "Iran":       {
                "capital":  "Tehran",
                "currency": "Rial",
                "language": "Persian",
          },
    "Iraq":       {
                "capital":  "Baghdad",
                "currency": "Iraqi Dinar",
                "language": "Arabic_Kurdish",
          },
    "Republic of Ireland":       {
                "capital":  "Dublin",
                "currency": "Euro",
                "language": "English_Irish",
          },
    "Israel":       {
                "capital":  "Jerusalem",
                "currency": "Shekel",
                "language": "Hebrew_Arabic",
          },
    "Italy":       {
                "capital":  "Rome",
                "currency": "Euro",
                "language": "Italian",
          },
    "Jamaica":       {
                "capital":  "Kingston",
                "currency": "Jamaican Dollar",
                "language": "English",
          },
    "Japan":       {
                "capital":  "Tokyo",
                "currency": "Yen",
                "language": "Japanese",
          },
    "Jordan":       {
                "capital":  "Amman",
                "currency": "Jordanian Dinar",
                "language": "Arabic",
          },
    "Kazakhstan":       {
                "capital":  "Astana",
                "currency": "Tenge",
                "language": "Kazakh_Russian",
          },
    "Kenya":       {
                "capital":  "Nairobi",
                "currency": "Kenyan Shilling",
                "language": "Swahili_English",
          },
    "Kiribati":       {
                "capital":  "Tarawa Atoll",
                "currency": "Kiribati Dollar",
                "language": "English_Gilbertese",
          },
    "North Korea":       {
                "capital":  "Pyongyang",
                "currency": "North Korean Won",
                "language": "Korean",
          },
    "South Korea":       {
                "capital":  "Seoul",
                "currency": "South Korean Won",
                "language": "Korean",
          },
    "Kosovo":       {
                "capital":  "Pristina",
                "currency": "Euro",
                "language": "Albanian_Serbian",
          },
    "Kuwait":       {
                "capital":  "Kuwait City",
                "currency": "Kuwaiti Dollar",
                "language": "Arabic_English",
          },
    "Kyrgyzstan":       {
                "capital":  "Bishkek",
                "currency": "Som",
                "language": "Kyrgyz_Russian",
          },
    "Laos":       {
                "capital":  "Vientiane",
                "currency": "Kip",
                "language": "Lao (Laotian)",
          },
    "Latvia":       {
                "capital":  "Riga",
                "currency": "Lats",
                "language": "Latvian",
          },
    "Lebanon":       {
                "capital":  "Beirut",
                "currency": "Lebanese Pound",
                "language": "Arabic_French",
          },
    "Lesotho":       {
                "capital":  "Maseru",
                "currency": "Loti",
                "language": "Sesotho_English",
          },
    "Liberia":       {
                "capital":  "Monrovia",
                "currency": "Liberian Dollar",
                "language": "English",
          },
    "Libya":       {
                "capital":  "Tripoli",
                "currency": "Libyan Dinar",
                "language": "Arabic",
          },
    "Liechtenstein":       {
                "capital":  "Vaduz",
                "currency": "Swiss Franc",
                "language": "German",
          },
    "Lithuania":       {
                "capital":  "Vilnius",
                "currency": "Lithuanian Litas",
                "language": "Lithuanian",
          },
    "Luxembourg":       {
                "capital":  "Luxembourg",
                "currency": "Euro",
                "language": "German_French_Luxembourgish",
          },
    "Macedonia":       {
                "capital":  "Skopje",
                "currency": "Macedonian Denar",
                "language": "Macedonian",
          },
    "Madagascar":       {
                "capital":  "Antananarivo",
                "currency": "Malagasy Ariary",
                "language": "Malagasy_French_English",
          },
    "Malawi":       {
                "capital":  "Lilongwe",
                "currency": "Malawi Kwacha",
                "language": "English",
          },
    "Malaysia":       {
                "capital":  "Kuala Lumpur",
                "currency": "Ringgit",
                "language": "Malay",
          },
    "Maldives":       {
                "capital":  "Male",
                "currency": "Maldivian Rufiyaa",
                "language": "Dhivehi",
          },
    "Mali":       {
                "capital":  "Bamako",
                "currency": "West African CFA Franc",
                "language": "French",
          },
    "Malta":       {
                "capital":  "Valletta",
                "currency": "Euro",
                "language": "Maltese_English",
          },
    "Marshall Islands":       {
                "capital":  "Majuro",
                "currency": "United States Dollar",
                "language": "Marshallese_English",
          },
    "Mauritania":       {
                "capital":  "Nouakchott",
                "currency": "Ouguiya",
                "language": "Arabic",
          },
    "Mauritius":       {
                "capital":  "Port Louis",
                "currency": "Mauritian Rupee",
                "language": "English",
          },
    "Mexico":       {
                "capital":  "Mexico City",
                "currency": "Mexican Peso",
                "language": "Spanish",
          },
    "Federal States of Micronesia":       {
                "capital":  "Palikir",
                "currency": "United States Dollar",
                "language": "English",
          },
    "Moldova":       {
                "capital":  "Chisinau",
                "currency": "Moldovan Leu",
                "language": "Moldovan (Romanian)",
          },
    "Monaco":       {
                "capital":  "Monaco",
                "currency": "Euro",
                "language": "French_Italian_English",
          },
    "Mongolia":       {
                "capital":  "Ulaanbaatar",
                "currency": "Togrog",
                "language": "Mongolian",
          },
    "Montenegro":       {
                "capital":  "Podgorica",
                "currency": "Euro",
                "language": "Montenegrin",
          },
    "Morocco":       {
                "capital":  "Rabat",
                "currency": "Moroccan Dirham",
                "language": "Arabic",
          },
    "Mozambique":       {
                "capital":  "Maputo",
                "currency": "Mozambican Metical",
                "language": "Portuguese",
          },
    "Myanmar (Burma)":       {
                "capital":  "Nypyidaw",
                "currency": "Kyat",
                "language": "Burmese",
          },
    "Namibia":       {
                "capital":  "Windhoek",
                "currency": "Namibian Dollar",
                "language": "English_Afrikaans_German",
          },
    "Nauru":       {
                "capital":  "Yaren",
                "currency": "Australian Dollar",
                "language": "English_Nauran",
          },
    "Nepal":       {
                "capital":  "Kathmandu",
                "currency": "Nepalese Rupee",
                "language": "Nepali",
          },
    "Netherlands":       {
                "capital":  "Amsterdam_The Hague",
                "currency": "Euro",
                "language": "Dutch",
          },
    "New Zealand":       {
                "capital":  "Wellington",
                "currency": "New Zealand Dollar",
                "language": "English",
          },
    "Nicaragua":       {
                "capital":  "Managua",
                "currency": "Cordoba",
                "language": "Spanish",
          },
    "Niger":       {
                "capital":  "Niamey",
                "currency": "West African CFA Franc",
                "language": "French",
          },
    "Nigeria":       {
                "capital":  "Abuja",
                "currency": "Naira",
                "language": "English",
          },
    "Norway":       {
                "capital":  "Oslo",
                "currency": "Norwegian Krone",
                "language": "Norwegian",
          },
    "Oman":       {
                "capital":  "Muscat",
                "currency": "Omani Rial",
                "language": "Arabic",
          },
    "Pakistan":       {
                "capital":  "Islamabad",
                "currency": "Pakistani Rupee",
                "language": "Urdu_English",
          },
    "Palau":       {
                "capital":  "Melekeok",
                "currency": "United States Dollar",
                "language": "English_Palauan",
          },
    "Panama":       {
                "capital":  "Panama City",
                "currency": "Balboa",
                "language": "Spanish",
          },
    "Papa New Guinea":       {
                "capital":  "Port Moresby Papa",
                "currency": "Papa New Guinean Kina",
                "language": "English_Tok Pisin_Hiri Motu",
          },
    "Paraguay":       {
                "capital":  "Asuncion",
                "currency": "Guarani",
                "language": "Spanish_Guarani",
          },
    "Peru":       {
                "capital":  "Lima",
                "currency": "Nuevo Sol",
                "language": "Spanish",
          },
    "Phillipines":       {
                "capital":  "Manila",
                "currency": "Phillipine Peso",
                "language": "Filipino_English",
          },
    "Poland":       {
                "capital":  "Warsaw",
                "currency": "Zloty",
                "language": "Polish",
          },
    "Portugal":       {
                "capital":  "Lisbon",
                "currency": "Euro",
                "language": "Portuguese",
          },
    "Qatar":       {
                "capital":  "Doha",
                "currency": "Qatari Riyal",
                "language": "Arabic",
          },
    "Romania":       {
                "capital":  "Bucharest",
                "currency": "Romanian Rupee",
                "language": "Romanian",
          },
    "Russia":       {
                "capital":  "Moscow",
                "currency": "Ruble",
                "language": "Russian",
          },
    "Rwanda":       {
                "capital":  "Kigali",
                "currency": "Rwandan Franc",
                "language": "Kinyarwanda_French_English",
          }
    }
}








