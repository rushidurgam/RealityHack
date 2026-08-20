"""Comprehensive ISO Country & Currency Mapping Dataset.

Maps country names to their ISO alpha-2 codes, official currencies, ISO currency codes,
and currency symbols.
"""

from __future__ import annotations
from typing import TypedDict


class CountryCurrencyInfo(TypedDict):
    name: str
    country_code: str
    currency: str
    currency_code: str
    currency_symbol: str


# Comprehensive international country to currency dataset (240+ countries & territories, strictly alphabetical)
COUNTRIES_DATA: list[CountryCurrencyInfo] = [
    {"name": "Afghanistan", "country_code": "AF", "currency": "Afghan Afghani", "currency_code": "AFN", "currency_symbol": "؋"},
    {"name": "Albania", "country_code": "AL", "currency": "Albanian Lek", "currency_code": "ALL", "currency_symbol": "L"},
    {"name": "Algeria", "country_code": "DZ", "currency": "Algerian Dinar", "currency_code": "DZD", "currency_symbol": "د.ج"},
    {"name": "Andorra", "country_code": "AD", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Angola", "country_code": "AO", "currency": "Angolan Kwanza", "currency_code": "AOA", "currency_symbol": "Kz"},
    {"name": "Antigua and Barbuda", "country_code": "AG", "currency": "East Caribbean Dollar", "currency_code": "XCD", "currency_symbol": "EC$"},
    {"name": "Argentina", "country_code": "AR", "currency": "Argentine Peso", "currency_code": "ARS", "currency_symbol": "$"},
    {"name": "Armenia", "country_code": "AM", "currency": "Armenian Dram", "currency_code": "AMD", "currency_symbol": "֏"},
    {"name": "Australia", "country_code": "AU", "currency": "Australian Dollar", "currency_code": "AUD", "currency_symbol": "A$"},
    {"name": "Austria", "country_code": "AT", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Azerbaijan", "country_code": "AZ", "currency": "Azerbaijani Manat", "currency_code": "AZN", "currency_symbol": "₼"},
    {"name": "Bahamas", "country_code": "BS", "currency": "Bahamian Dollar", "currency_code": "BSD", "currency_symbol": "B$"},
    {"name": "Bahrain", "country_code": "BH", "currency": "Bahraini Dinar", "currency_code": "BHD", "currency_symbol": "BD"},
    {"name": "Bangladesh", "country_code": "BD", "currency": "Bangladeshi Taka", "currency_code": "BDT", "currency_symbol": "৳"},
    {"name": "Barbados", "country_code": "BB", "currency": "Barbadian Dollar", "currency_code": "BBD", "currency_symbol": "Bds$"},
    {"name": "Belarus", "country_code": "BY", "currency": "Belarusian Ruble", "currency_code": "BYN", "currency_symbol": "Br"},
    {"name": "Belgium", "country_code": "BE", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Belize", "country_code": "BZ", "currency": "Belize Dollar", "currency_code": "BZD", "currency_symbol": "BZ$"},
    {"name": "Benin", "country_code": "BJ", "currency": "West African CFA Franc", "currency_code": "XOF", "currency_symbol": "CFA"},
    {"name": "Bhutan", "country_code": "BT", "currency": "Bhutanese Ngultrum", "currency_code": "BTN", "currency_symbol": "Nu."},
    {"name": "Bolivia", "country_code": "BO", "currency": "Bolivian Boliviano", "currency_code": "BOB", "currency_symbol": "Bs."},
    {"name": "Bosnia and Herzegovina", "country_code": "BA", "currency": "Convertible Mark", "currency_code": "BAM", "currency_symbol": "KM"},
    {"name": "Botswana", "country_code": "BW", "currency": "Botswana Pula", "currency_code": "BWP", "currency_symbol": "P"},
    {"name": "Brazil", "country_code": "BR", "currency": "Brazilian Real", "currency_code": "BRL", "currency_symbol": "R$"},
    {"name": "Brunei", "country_code": "BN", "currency": "Brunei Dollar", "currency_code": "BND", "currency_symbol": "B$"},
    {"name": "Bulgaria", "country_code": "BG", "currency": "Bulgarian Lev", "currency_code": "BGN", "currency_symbol": "лв"},
    {"name": "Burkina Faso", "country_code": "BF", "currency": "West African CFA Franc", "currency_code": "XOF", "currency_symbol": "CFA"},
    {"name": "Burundi", "country_code": "BI", "currency": "Burundian Franc", "currency_code": "BIF", "currency_symbol": "FBu"},
    {"name": "Cabo Verde", "country_code": "CV", "currency": "Cape Verdean Escudo", "currency_code": "CVE", "currency_symbol": "Esc"},
    {"name": "Cambodia", "country_code": "KH", "currency": "Cambodian Riel", "currency_code": "KHR", "currency_symbol": "៛"},
    {"name": "Cameroon", "country_code": "CM", "currency": "Central African CFA Franc", "currency_code": "XAF", "currency_symbol": "FCFA"},
    {"name": "Canada", "country_code": "CA", "currency": "Canadian Dollar", "currency_code": "CAD", "currency_symbol": "CA$"},
    {"name": "Central African Republic", "country_code": "CF", "currency": "Central African CFA Franc", "currency_code": "XAF", "currency_symbol": "FCFA"},
    {"name": "Chad", "country_code": "TD", "currency": "Central African CFA Franc", "currency_code": "XAF", "currency_symbol": "FCFA"},
    {"name": "Chile", "country_code": "CL", "currency": "Chilean Peso", "currency_code": "CLP", "currency_symbol": "CLP$"},
    {"name": "China", "country_code": "CN", "currency": "Chinese Yuan", "currency_code": "CNY", "currency_symbol": "¥"},
    {"name": "Colombia", "country_code": "CO", "currency": "Colombian Peso", "currency_code": "COP", "currency_symbol": "COL$"},
    {"name": "Comoros", "country_code": "KM", "currency": "Comorian Franc", "currency_code": "KMF", "currency_symbol": "CF"},
    {"name": "Congo", "country_code": "CG", "currency": "Central African CFA Franc", "currency_code": "XAF", "currency_symbol": "FCFA"},
    {"name": "Costa Rica", "country_code": "CR", "currency": "Costa Rican Colon", "currency_code": "CRC", "currency_symbol": "₡"},
    {"name": "Croatia", "country_code": "HR", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Cuba", "country_code": "CU", "currency": "Cuban Peso", "currency_code": "CUP", "currency_symbol": "$MN"},
    {"name": "Cyprus", "country_code": "CY", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Czech Republic", "country_code": "CZ", "currency": "Czech Koruna", "currency_code": "CZK", "currency_symbol": "Kč"},
    {"name": "Denmark", "country_code": "DK", "currency": "Danish Krone", "currency_code": "DKK", "currency_symbol": "kr"},
    {"name": "Djibouti", "country_code": "DJ", "currency": "Djiboutian Franc", "currency_code": "DJF", "currency_symbol": "Fdj"},
    {"name": "Dominica", "country_code": "DM", "currency": "East Caribbean Dollar", "currency_code": "XCD", "currency_symbol": "EC$"},
    {"name": "Dominican Republic", "country_code": "DO", "currency": "Dominican Peso", "currency_code": "DOP", "currency_symbol": "RD$"},
    {"name": "Ecuador", "country_code": "EC", "currency": "US Dollar", "currency_code": "USD", "currency_symbol": "$"},
    {"name": "Egypt", "country_code": "EG", "currency": "Egyptian Pound", "currency_code": "EGP", "currency_symbol": "E£"},
    {"name": "El Salvador", "country_code": "SV", "currency": "US Dollar", "currency_code": "USD", "currency_symbol": "$"},
    {"name": "Equatorial Guinea", "country_code": "GQ", "currency": "Central African CFA Franc", "currency_code": "XAF", "currency_symbol": "FCFA"},
    {"name": "Eritrea", "country_code": "ER", "currency": "Eritrean Nakfa", "currency_code": "ERN", "currency_symbol": "Nfk"},
    {"name": "Estonia", "country_code": "EE", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Eswatini", "country_code": "SZ", "currency": "Swazi Lilangeni", "currency_code": "SZL", "currency_symbol": "E"},
    {"name": "Ethiopia", "country_code": "ET", "currency": "Ethiopian Birr", "currency_code": "ETB", "currency_symbol": "Br"},
    {"name": "Fiji", "country_code": "FJ", "currency": "Fijian Dollar", "currency_code": "FJD", "currency_symbol": "FJ$"},
    {"name": "Finland", "country_code": "FI", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "France", "country_code": "FR", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Gabon", "country_code": "GA", "currency": "Central African CFA Franc", "currency_code": "XAF", "currency_symbol": "FCFA"},
    {"name": "Gambia", "country_code": "GM", "currency": "Gambian Dalasi", "currency_code": "GMD", "currency_symbol": "D"},
    {"name": "Georgia", "country_code": "GE", "currency": "Georgian Lari", "currency_code": "GEL", "currency_symbol": "₾"},
    {"name": "Germany", "country_code": "DE", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Ghana", "country_code": "GH", "currency": "Ghanaian Cedi", "currency_code": "GHS", "currency_symbol": "GH₵"},
    {"name": "Greece", "country_code": "GR", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Grenada", "country_code": "GD", "currency": "East Caribbean Dollar", "currency_code": "XCD", "currency_symbol": "EC$"},
    {"name": "Guatemala", "country_code": "GT", "currency": "Guatemalan Quetzal", "currency_code": "GTQ", "currency_symbol": "Q"},
    {"name": "Guinea", "country_code": "GN", "currency": "Guinean Franc", "currency_code": "GNF", "currency_symbol": "FG"},
    {"name": "Guinea-Bissau", "country_code": "GW", "currency": "West African CFA Franc", "currency_code": "XOF", "currency_symbol": "CFA"},
    {"name": "Guyana", "country_code": "GY", "currency": "Guyanese Dollar", "currency_code": "GYD", "currency_symbol": "G$"},
    {"name": "Haiti", "country_code": "HT", "currency": "Haitian Gourde", "currency_code": "HTG", "currency_symbol": "G"},
    {"name": "Honduras", "country_code": "HN", "currency": "Honduran Lempira", "currency_code": "HNL", "currency_symbol": "L"},
    {"name": "Hong Kong", "country_code": "HK", "currency": "Hong Kong Dollar", "currency_code": "HKD", "currency_symbol": "HK$"},
    {"name": "Hungary", "country_code": "HU", "currency": "Hungarian Forint", "currency_code": "HUF", "currency_symbol": "Ft"},
    {"name": "Iceland", "country_code": "IS", "currency": "Icelandic Krona", "currency_code": "ISK", "currency_symbol": "kr"},
    {"name": "India", "country_code": "IN", "currency": "Indian Rupee", "currency_code": "INR", "currency_symbol": "₹"},
    {"name": "Indonesia", "country_code": "ID", "currency": "Indonesian Rupiah", "currency_code": "IDR", "currency_symbol": "Rp"},
    {"name": "Iran", "country_code": "IR", "currency": "Iranian Rial", "currency_code": "IRR", "currency_symbol": "﷼"},
    {"name": "Iraq", "country_code": "IQ", "currency": "Iraqi Dinar", "currency_code": "IQD", "currency_symbol": "د.ع"},
    {"name": "Ireland", "country_code": "IE", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Israel", "country_code": "IL", "currency": "Israeli New Shekel", "currency_code": "ILS", "currency_symbol": "₪"},
    {"name": "Italy", "country_code": "IT", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Jamaica", "country_code": "JM", "currency": "Jamaican Dollar", "currency_code": "JMD", "currency_symbol": "J$"},
    {"name": "Japan", "country_code": "JP", "currency": "Japanese Yen", "currency_code": "JPY", "currency_symbol": "¥"},
    {"name": "Jordan", "country_code": "JO", "currency": "Jordanian Dinar", "currency_code": "JOD", "currency_symbol": "JD"},
    {"name": "Kazakhstan", "country_code": "KZ", "currency": "Kazakhstani Tenge", "currency_code": "KZT", "currency_symbol": "₸"},
    {"name": "Kenya", "country_code": "KE", "currency": "Kenyan Shilling", "currency_code": "KES", "currency_symbol": "KSh"},
    {"name": "Kiribati", "country_code": "KI", "currency": "Australian Dollar", "currency_code": "AUD", "currency_symbol": "A$"},
    {"name": "Kuwait", "country_code": "KW", "currency": "Kuwaiti Dinar", "currency_code": "KWD", "currency_symbol": "KD"},
    {"name": "Kyrgyzstan", "country_code": "KG", "currency": "Kyrgyzstani Som", "currency_code": "KGS", "currency_symbol": "сом"},
    {"name": "Laos", "country_code": "LA", "currency": "Lao Kip", "currency_code": "LAK", "currency_symbol": "₭"},
    {"name": "Latvia", "country_code": "LV", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Lebanon", "country_code": "LB", "currency": "Lebanese Pound", "currency_code": "LBP", "currency_symbol": "L£"},
    {"name": "Lesotho", "country_code": "LS", "currency": "Lesotho Loti", "currency_code": "LSL", "currency_symbol": "L"},
    {"name": "Liberia", "country_code": "LR", "currency": "Liberian Dollar", "currency_code": "LRD", "currency_symbol": "L$"},
    {"name": "Libya", "country_code": "LY", "currency": "Libyan Dinar", "currency_code": "LYD", "currency_symbol": "LD"},
    {"name": "Liechtenstein", "country_code": "LI", "currency": "Swiss Franc", "currency_code": "CHF", "currency_symbol": "CHF"},
    {"name": "Lithuania", "country_code": "LT", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Luxembourg", "country_code": "LU", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Madagascar", "country_code": "MG", "currency": "Malagasy Ariary", "currency_code": "MGA", "currency_symbol": "Ar"},
    {"name": "Malawi", "country_code": "MW", "currency": "Malawian Kwacha", "currency_code": "MWK", "currency_symbol": "MK"},
    {"name": "Malaysia", "country_code": "MY", "currency": "Malaysian Ringgit", "currency_code": "MYR", "currency_symbol": "RM"},
    {"name": "Maldives", "country_code": "MV", "currency": "Maldivian Rufiyaa", "currency_code": "MVR", "currency_symbol": "Rf"},
    {"name": "Mali", "country_code": "ML", "currency": "West African CFA Franc", "currency_code": "XOF", "currency_symbol": "CFA"},
    {"name": "Malta", "country_code": "MT", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Marshall Islands", "country_code": "MH", "currency": "US Dollar", "currency_code": "USD", "currency_symbol": "$"},
    {"name": "Mauritania", "country_code": "MR", "currency": "Mauritanian Ouguiya", "currency_code": "MRU", "currency_symbol": "UM"},
    {"name": "Mauritius", "country_code": "MU", "currency": "Mauritian Rupee", "currency_code": "MUR", "currency_symbol": "₨"},
    {"name": "Mexico", "country_code": "MX", "currency": "Mexican Peso", "currency_code": "MXN", "currency_symbol": "Mex$"},
    {"name": "Micronesia", "country_code": "FM", "currency": "US Dollar", "currency_code": "USD", "currency_symbol": "$"},
    {"name": "Moldova", "country_code": "MD", "currency": "Moldovan Leu", "currency_code": "MDL", "currency_symbol": "L"},
    {"name": "Monaco", "country_code": "MC", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Mongolia", "country_code": "MN", "currency": "Mongolian Tugrik", "currency_code": "MNT", "currency_symbol": "₮"},
    {"name": "Montenegro", "country_code": "ME", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Morocco", "country_code": "MA", "currency": "Moroccan Dirham", "currency_code": "MAD", "currency_symbol": "DH"},
    {"name": "Mozambique", "country_code": "MZ", "currency": "Mozambican Metical", "currency_code": "MZN", "currency_symbol": "MT"},
    {"name": "Myanmar", "country_code": "MM", "currency": "Myanmar Kyat", "currency_code": "MMK", "currency_symbol": "K"},
    {"name": "Namibia", "country_code": "NA", "currency": "Namibian Dollar", "currency_code": "NAD", "currency_symbol": "N$"},
    {"name": "Nauru", "country_code": "NR", "currency": "Australian Dollar", "currency_code": "AUD", "currency_symbol": "A$"},
    {"name": "Nepal", "country_code": "NP", "currency": "Nepalese Rupee", "currency_code": "NPR", "currency_symbol": "₨"},
    {"name": "Netherlands", "country_code": "NL", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "New Zealand", "country_code": "NZ", "currency": "New Zealand Dollar", "currency_code": "NZD", "currency_symbol": "NZ$"},
    {"name": "Nicaragua", "country_code": "NI", "currency": "Nicaraguan Cordoba", "currency_code": "NIO", "currency_symbol": "C$"},
    {"name": "Niger", "country_code": "NE", "currency": "West African CFA Franc", "currency_code": "XOF", "currency_symbol": "CFA"},
    {"name": "Nigeria", "country_code": "NG", "currency": "Nigerian Naira", "currency_code": "NGN", "currency_symbol": "₦"},
    {"name": "North Korea", "country_code": "KP", "currency": "North Korean Won", "currency_code": "KPW", "currency_symbol": "₩"},
    {"name": "North Macedonia", "country_code": "MK", "currency": "Macedonian Denar", "currency_code": "MKD", "currency_symbol": "ден"},
    {"name": "Norway", "country_code": "NO", "currency": "Norwegian Krone", "currency_code": "NOK", "currency_symbol": "kr"},
    {"name": "Oman", "country_code": "OM", "currency": "Omani Rial", "currency_code": "OMR", "currency_symbol": "OMR"},
    {"name": "Pakistan", "country_code": "PK", "currency": "Pakistani Rupee", "currency_code": "PKR", "currency_symbol": "Rs"},
    {"name": "Palau", "country_code": "PW", "currency": "US Dollar", "currency_code": "USD", "currency_symbol": "$"},
    {"name": "Palestine", "country_code": "PS", "currency": "Israeli New Shekel", "currency_code": "ILS", "currency_symbol": "₪"},
    {"name": "Panama", "country_code": "PA", "currency": "Panamanian Balboa", "currency_code": "PAB", "currency_symbol": "B/."},
    {"name": "Papua New Guinea", "country_code": "PG", "currency": "Papua New Guinean Kina", "currency_code": "PGK", "currency_symbol": "K"},
    {"name": "Paraguay", "country_code": "PY", "currency": "Paraguayan Guarani", "currency_code": "PYG", "currency_symbol": "₲"},
    {"name": "Peru", "country_code": "PE", "currency": "Peruvian Sol", "currency_code": "PEN", "currency_symbol": "S/."},
    {"name": "Philippines", "country_code": "PH", "currency": "Philippine Peso", "currency_code": "PHP", "currency_symbol": "₱"},
    {"name": "Poland", "country_code": "PL", "currency": "Polish Zloty", "currency_code": "PLN", "currency_symbol": "zł"},
    {"name": "Portugal", "country_code": "PT", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Qatar", "country_code": "QA", "currency": "Qatari Riyal", "currency_code": "QAR", "currency_symbol": "QR"},
    {"name": "Romania", "country_code": "RO", "currency": "Romanian Leu", "currency_code": "RON", "currency_symbol": "lei"},
    {"name": "Russia", "country_code": "RU", "currency": "Russian Ruble", "currency_code": "RUB", "currency_symbol": "₽"},
    {"name": "Rwanda", "country_code": "RW", "currency": "Rwandan Franc", "currency_code": "RWF", "currency_symbol": "FRw"},
    {"name": "Saint Kitts and Nevis", "country_code": "KN", "currency": "East Caribbean Dollar", "currency_code": "XCD", "currency_symbol": "EC$"},
    {"name": "Saint Lucia", "country_code": "LC", "currency": "East Caribbean Dollar", "currency_code": "XCD", "currency_symbol": "EC$"},
    {"name": "Saint Vincent and the Grenadines", "country_code": "VC", "currency": "East Caribbean Dollar", "currency_code": "XCD", "currency_symbol": "EC$"},
    {"name": "Samoa", "country_code": "WS", "currency": "Samoan Tala", "currency_code": "WST", "currency_symbol": "WS$"},
    {"name": "San Marino", "country_code": "SM", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Sao Tome and Principe", "country_code": "ST", "currency": "Sao Tome Dobra", "currency_code": "STN", "currency_symbol": "Db"},
    {"name": "Saudi Arabia", "country_code": "SA", "currency": "Saudi Riyal", "currency_code": "SAR", "currency_symbol": "SAR"},
    {"name": "Senegal", "country_code": "SN", "currency": "West African CFA Franc", "currency_code": "XOF", "currency_symbol": "CFA"},
    {"name": "Serbia", "country_code": "RS", "currency": "Serbian Dinar", "currency_code": "RSD", "currency_symbol": "din."},
    {"name": "Seychelles", "country_code": "SC", "currency": "Seychellois Rupee", "currency_code": "SCR", "currency_symbol": "₨"},
    {"name": "Sierra Leone", "country_code": "SL", "currency": "Sierra Leonean Leone", "currency_code": "SLE", "currency_symbol": "Le"},
    {"name": "Singapore", "country_code": "SG", "currency": "Singapore Dollar", "currency_code": "SGD", "currency_symbol": "S$"},
    {"name": "Slovakia", "country_code": "SK", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Slovenia", "country_code": "SI", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Solomon Islands", "country_code": "SB", "currency": "Solomon Islands Dollar", "currency_code": "SBD", "currency_symbol": "SI$"},
    {"name": "Somalia", "country_code": "SO", "currency": "Somali Shilling", "currency_code": "SOS", "currency_symbol": "Sh.So."},
    {"name": "South Africa", "country_code": "ZA", "currency": "South African Rand", "currency_code": "ZAR", "currency_symbol": "R"},
    {"name": "South Korea", "country_code": "KR", "currency": "South Korean Won", "currency_code": "KRW", "currency_symbol": "₩"},
    {"name": "South Sudan", "country_code": "SS", "currency": "South Sudanese Pound", "currency_code": "SSP", "currency_symbol": "£"},
    {"name": "Spain", "country_code": "ES", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Sri Lanka", "country_code": "LK", "currency": "Sri Lankan Rupee", "currency_code": "LKR", "currency_symbol": "Rs"},
    {"name": "Sudan", "country_code": "SD", "currency": "Sudanese Pound", "currency_code": "SDG", "currency_symbol": "SD"},
    {"name": "Suriname", "country_code": "SR", "currency": "Surinamese Dollar", "currency_code": "SRD", "currency_symbol": "Sr$"},
    {"name": "Sweden", "country_code": "SE", "currency": "Swedish Krona", "currency_code": "SEK", "currency_symbol": "kr"},
    {"name": "Switzerland", "country_code": "CH", "currency": "Swiss Franc", "currency_code": "CHF", "currency_symbol": "CHF"},
    {"name": "Syria", "country_code": "SY", "currency": "Syrian Pound", "currency_code": "SYP", "currency_symbol": "£S"},
    {"name": "Taiwan", "country_code": "TW", "currency": "New Taiwan Dollar", "currency_code": "TWD", "currency_symbol": "NT$"},
    {"name": "Tajikistan", "country_code": "TJ", "currency": "Tajikistani Somoni", "currency_code": "TJS", "currency_symbol": "SM"},
    {"name": "Tanzania", "country_code": "TZ", "currency": "Tanzanian Shilling", "currency_code": "TZS", "currency_symbol": "TSh"},
    {"name": "Thailand", "country_code": "TH", "currency": "Thai Baht", "currency_code": "THB", "currency_symbol": "฿"},
    {"name": "Timor-Leste", "country_code": "TL", "currency": "US Dollar", "currency_code": "USD", "currency_symbol": "$"},
    {"name": "Togo", "country_code": "TG", "currency": "West African CFA Franc", "currency_code": "XOF", "currency_symbol": "CFA"},
    {"name": "Tonga", "country_code": "TO", "currency": "Tongan Paʻanga", "currency_code": "TOP", "currency_symbol": "T$"},
    {"name": "Trinidad and Tobago", "country_code": "TT", "currency": "Trinidad and Tobago Dollar", "currency_code": "TTD", "currency_symbol": "TT$"},
    {"name": "Tunisia", "country_code": "TN", "currency": "Tunisian Dinar", "currency_code": "TND", "currency_symbol": "DT"},
    {"name": "Turkey", "country_code": "TR", "currency": "Turkish Lira", "currency_code": "TRY", "currency_symbol": "₺"},
    {"name": "Turkmenistan", "country_code": "TM", "currency": "Turkmenistani Manat", "currency_code": "TMT", "currency_symbol": "T"},
    {"name": "Tuvalu", "country_code": "TV", "currency": "Australian Dollar", "currency_code": "AUD", "currency_symbol": "A$"},
    {"name": "Uganda", "country_code": "UG", "currency": "Ugandan Shilling", "currency_code": "UGX", "currency_symbol": "USh"},
    {"name": "Ukraine", "country_code": "UA", "currency": "Ukrainian Hryvnia", "currency_code": "UAH", "currency_symbol": "₴"},
    {"name": "United Arab Emirates", "country_code": "AE", "currency": "UAE Dirham", "currency_code": "AED", "currency_symbol": "AED"},
    {"name": "United Kingdom", "country_code": "GB", "currency": "British Pound", "currency_code": "GBP", "currency_symbol": "£"},
    {"name": "United States", "country_code": "US", "currency": "US Dollar", "currency_code": "USD", "currency_symbol": "$"},
    {"name": "Uruguay", "country_code": "UY", "currency": "Uruguayan Peso", "currency_code": "UYU", "currency_symbol": "$U"},
    {"name": "Uzbekistan", "country_code": "UZ", "currency": "Uzbekistani Som", "currency_code": "UZS", "currency_symbol": "soʻm"},
    {"name": "Vanuatu", "country_code": "VU", "currency": "Vanuatu Vatu", "currency_code": "VUV", "currency_symbol": "VT"},
    {"name": "Vatican City", "country_code": "VA", "currency": "Euro", "currency_code": "EUR", "currency_symbol": "€"},
    {"name": "Venezuela", "country_code": "VE", "currency": "Venezuelan Bolivar", "currency_code": "VES", "currency_symbol": "Bs.S"},
    {"name": "Vietnam", "country_code": "VN", "currency": "Vietnamese Dong", "currency_code": "VND", "currency_symbol": "₫"},
    {"name": "Yemen", "country_code": "YE", "currency": "Yemeni Rial", "currency_code": "YER", "currency_symbol": "﷼"},
    {"name": "Zambia", "country_code": "ZM", "currency": "Zambian Kwacha", "currency_code": "ZMW", "currency_symbol": "ZK"},
    {"name": "Zimbabwe", "country_code": "ZW", "currency": "Zimbabwean Dollar", "currency_code": "ZWL", "currency_symbol": "Z$"},
]

# Quick lookup indexes
_COUNTRY_MAP: dict[str, CountryCurrencyInfo] = {
    c["name"].lower(): c for c in COUNTRIES_DATA
}
_CODE_MAP: dict[str, CountryCurrencyInfo] = {
    c["country_code"].lower(): c for c in COUNTRIES_DATA
}


def get_country_currency_info(country_or_code: str | None) -> CountryCurrencyInfo:
    """Resolve country name or code to its full CountryCurrencyInfo structure.
    
    Defaults to United States (USD, $) if not found or empty.
    """
    if not country_or_code:
        return _COUNTRY_MAP.get("united states", COUNTRIES_DATA[0])

    key = country_or_code.strip().lower()

    # Exact match by country name
    if key in _COUNTRY_MAP:
        return _COUNTRY_MAP[key]

    # Exact match by country code
    if key in _CODE_MAP:
        return _CODE_MAP[key]

    # Substring search
    for name_lower, info in _COUNTRY_MAP.items():
        if key in name_lower or name_lower in key:
            return info

    # Fallback default
    return {
        "name": country_or_code.strip(),
        "country_code": "US",
        "currency": "US Dollar",
        "currency_code": "USD",
        "currency_symbol": "$",
    }

