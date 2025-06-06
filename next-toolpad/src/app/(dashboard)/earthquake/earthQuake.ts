export type USGSEarthquakeFeature = {
    type: 'Feature';
    properties: {
        mag: number; // Magnitude ของแผ่นดินไหว
        place: string; // สถานที่เกิดแผ่นดินไหว
        time: number; // เวลาที่เกิด (timestamp)
        updated: number; // เวลาที่อัปเดตล่าสุด (timestamp)
        tz: number | null; // Timezone (อาจเป็น null)
        url: string; // ลิงก์ไปยังหน้าข้อมูลแผ่นดินไหว
        detail: string; // API URL สำหรับรายละเอียดเพิ่มเติม
        felt: number | null; // จำนวนรายงานว่า "รู้สึกถึงแผ่นดินไหว" (อาจเป็น null)
        cdi: number | null; // ค่า Community Internet Intensity Map (อาจเป็น null)
        mmi: number | null; // ค่า ShakeMap MMI (อาจเป็น null)
        alert: string | null; // ระดับการเตือนภัย (อาจเป็น null)
        status: string; // สถานะ (เช่น 'reviewed')
        tsunami: number; // 1 = มีโอกาสเกิดสึนามิ, 0 = ไม่มี
        sig: number; // ค่าความสำคัญของแผ่นดินไหว
        net: string; // รหัสเครือข่ายของเซ็นเซอร์
        code: string; // รหัสเหตุการณ์ของแผ่นดินไหว
        ids: string; // รายการรหัสเหตุการณ์ที่เกี่ยวข้อง
        sources: string; // แหล่งที่มาของข้อมูล
        types: string; // ประเภทข้อมูลที่มี (เช่น dyfi, origin)
        nst: number | null; // จำนวนสถานีที่ใช้คำนวณแผ่นดินไหว (อาจเป็น null)
        dmin: number | null; // ระยะทาง (หน่วยเป็น degree) จากศูนย์กลางไปยังสถานีใกล้ที่สุด (อาจเป็น null)
        rms: number | null; // ค่า root mean square ของเวลาที่บันทึก (อาจเป็น null)
        gap: number | null; // ช่องว่างของมุมที่ใช้คำนวณแผ่นดินไหว (อาจเป็น null)
        magType: string; // ประเภทของขนาด (เช่น 'mb', 'ml', 'mw')
        type: string; // ประเภทของเหตุการณ์ (เช่น 'earthquake')
        title: string; // ชื่อเหตุการณ์
        flagUrl?: string; // URL รูปธงประเทศ (optional)
    };
    geometry: {
        type: 'Point';
        coordinates: [number, number, number]; // [longitude, latitude, depth]
    };
    id: string; // รหัสของแผ่นดินไหว
};

// Define the structure of the earthquake data from EMSC API
export type EMSCEarthquakeFeature = {
    type: "Feature";
    geometry: {
        type: "Point";
        coordinates: [number, number, number]; // [longitude, latitude, depth]
    };
    id: string;
    properties: {
        source_id: string;
        source_catalog: string;
        lastupdate: string;
        time: string;
        flynn_region: string;
        lat: number;
        lon: number;
        depth: number;
        evtype: string;
        auth: string;
        mag: number;
        magtype: string;
        unid: string;
        flagUrl?: string; // URL รูปธงประเทศ (optional)
    };
};

export type EMSCEarthquakeResponse = {
    type: "FeatureCollection";
    metadata: {
        count: number;
    };
    features: EMSCEarthquakeFeature[];
};

// {
//     "@attributes": {
//       "version": "1.0"
//     },
//     "header": {
//       "title": "Daily Seismic (Earthquake) Events in Region and global ",
//       "description": "Daily Seismic (Earthquake) Events in Region and global ",
//       "uri": "http://data.tmd.go.th/api/DailySeismicEvent/v1/index.php",
//       "lastBuildDate": "2025-04-05 07:34:18",
//       "copyRight": "Thai Meteorological Department:2558",
//       "generator": "TMDData_API Services",
//       "status": "200 OK"
//     },
//     "DailyEarthquakes": [
//       {
//         "OriginThai": "ประเทศเมียนมา (Myanmar)",
//         "DateTimeUTC": "2025-04-04 23:59:05.000",
//         "DateTimeThai": "2025-04-05 06:59:05.000",
//         "Depth": "10",
//         "Magnitude": "3.4",
//         "Latitude": "22.1300000",
//         "Longitude": "96.3170000",
//         "TitleThai": "แผ่นดินไหว ประเทศเมียนมา (Myanmar)"
//       }
//     ]
// }

export type TMDEarthquakeFeature = {
    properties: {
        originThai: string; // ประเทศที่เกิดแผ่นดินไหว
        dateTimeUTC: string; // เวลาที่เกิดแผ่นดินไหว (UTC)
        dateTimeThai: string; // เวลาที่เกิดแผ่นดินไหว (ไทย)
        depth: number; // ความลึกของแผ่นดินไหว
        magnitude: number; // ขนาดของแผ่นดินไหว
        latitude: number; // ละติจูด
        longitude: number; // ลองจิจูด
        titleThai: string; // ชื่อเหตุการณ์ (ไทย)
        flagUrl?: string; // URL รูปธงประเทศ (optional)
        country?: string;
        flag?: string
    }
}

export type TMDEarthquakeResponse = {
    DailyEarthquakes: TMDEarthquakeFeature[]; // รายการแผ่นดินไหว
}
export const countryMapping: Record<string, string> = {
    "Andorra": "ad",
    "United Arab Emirates": "ae",
    "Afghanistan": "af",
    "Antigua and Barbuda": "ag",
    "Anguilla": "ai",
    "Albania": "al",
    "Armenia": "am",
    "Angola": "ao",
    "Antarctica": "aq",
    "Argentina": "ar",
    "American Samoa": "as",
    "Austria": "at",
    "Australia": "au",
    "Aruba": "aw",
    "Åland Islands": "ax",
    "Azerbaijan": "az",
    "Bosnia and Herzegovina": "ba",
    "Barbados": "bb",
    "Bangladesh": "bd",
    "Belgium": "be",
    "Burkina Faso": "bf",
    "Bulgaria": "bg",
    "Bahrain": "bh",
    "Burundi": "bi",
    "Benin": "bj",
    "Saint Barthélemy": "bl",
    "Bermuda": "bm",
    "Brunei": "bn",
    "Bolivia": "bo",
    "Caribbean Netherlands": "bq",
    "Brazil": "br",
    "Bahamas": "bs",
    "Bhutan": "bt",
    "Bouvet Island": "bv",
    "Botswana": "bw",
    "Belarus": "by",
    "Belize": "bz",
    "Canada": "ca",
    "Cocos (Keeling) Islands": "cc",
    "DR Congo": "cd",
    "Central African Republic": "cf",
    "Republic of the Congo": "cg",
    "Switzerland": "ch",
    "Côte d'Ivoire (Ivory Coast)": "ci",
    "Cook Islands": "ck",
    "Chile": "cl",
    "Cameroon": "cm",
    "China": "cn",
    "Colombia": "co",
    "Costa Rica": "cr",
    "Cuba": "cu",
    "Cape Verde": "cv",
    "Curaçao": "cw",
    "Christmas Island": "cx",
    "Cyprus": "cy",
    "Czechia": "cz",
    "Germany": "de",
    "Djibouti": "dj",
    "Denmark": "dk",
    "Dominica": "dm",
    "Dominican Republic": "do",
    "Algeria": "dz",
    "Ecuador": "ec",
    "Estonia": "ee",
    "Egypt": "eg",
    "Western Sahara": "eh",
    "Eritrea": "er",
    "Spain": "es",
    "Ethiopia": "et",
    "European Union": "eu",
    "Finland": "fi",
    "Fiji": "fj",
    "Falkland Islands": "fk",
    "Micronesia": "fm",
    "Faroe Islands": "fo",
    "France": "fr",
    "Gabon": "ga",
    "United Kingdom": "gb",
    "England": "gb-eng",
    "Northern Ireland": "gb-nir",
    "Scotland": "gb-sct",
    "Wales": "gb-wls",
    "Grenada": "gd",
    "Georgia": "us-ga",
    "French Guiana": "gf",
    "Guernsey": "gg",
    "Ghana": "gh",
    "Gibraltar": "gi",
    "Greenland": "gl",
    "Gambia": "gm",
    "Guinea": "gn",
    "Guadeloupe": "gp",
    "Equatorial Guinea": "gq",
    "Greece": "gr",
    "South Georgia": "gs",
    "Guatemala": "gt",
    "Guam": "gu",
    "Guinea-Bissau": "gw",
    "Guyana": "gy",
    "Hong Kong": "hk",
    "Heard Island and McDonald Islands": "hm",
    "Honduras": "hn",
    "Croatia": "hr",
    "Haiti": "ht",
    "Hungary": "hu",
    "Indonesia": "id",
    "Ireland": "ie",
    "Israel": "il",
    "Isle of Man": "im",
    "India": "in",
    "British Indian Ocean Territory": "io",
    "Iraq": "iq",
    "Iran": "ir",
    "Iceland": "is",
    "Italy": "it",
    "Jersey": "je",
    "Jamaica": "jm",
    "Jordan": "jo",
    "Japan": "jp",
    "Kenya": "ke",
    "Kyrgyzstan": "kg",
    "Cambodia": "kh",
    "Kiribati": "ki",
    "Comoros": "km",
    "Saint Kitts and Nevis": "kn",
    "North Korea": "kp",
    "South Korea": "kr",
    "Kuwait": "kw",
    "Cayman Islands": "ky",
    "Kazakhstan": "kz",
    "Laos": "la",
    "Lebanon": "lb",
    "Saint Lucia": "lc",
    "Liechtenstein": "li",
    "Sri Lanka": "lk",
    "Liberia": "lr",
    "Lesotho": "ls",
    "Lithuania": "lt",
    "Luxembourg": "lu",
    "Latvia": "lv",
    "Libya": "ly",
    "Morocco": "ma",
    "Monaco": "mc",
    "Moldova": "md",
    "Montenegro": "me",
    "Saint Martin": "mf",
    "Madagascar": "mg",
    "Marshall Islands": "mh",
    "North Macedonia": "mk",
    "Mali": "ml",
    "Myanmar": "mm",
    "Mongolia": "mn",
    "Macau": "mo",
    "Northern Mariana Islands": "mp",
    "Martinique": "mq",
    "Mauritania": "mr",
    "Montserrat": "ms",
    "Malta": "mt",
    "Mauritius": "mu",
    "Maldives": "mv",
    "Malawi": "mw",
    "Mexico": "mx",
    "Malaysia": "my",
    "Mozambique": "mz",
    "Namibia": "na",
    "New Caledonia": "nc",
    "Niger": "ne",
    "Norfolk Island": "nf",
    "Nigeria": "ng",
    "Nicaragua": "ni",
    "Netherlands": "nl",
    "Norway": "no",
    "Nepal": "np",
    "Nauru": "nr",
    "Niue": "nu",
    "New Zealand": "nz",
    "Oman": "om",
    "Panama": "pa",
    "Peru": "pe",
    "French Polynesia": "pf",
    "Papua New Guinea": "pg",
    "Philippines": "ph",
    "Pakistan": "pk",
    "Poland": "pl",
    "Saint Pierre and Miquelon": "pm",
    "Pitcairn Islands": "pn",
    "Puerto Rico": "pr",
    "Palestine": "ps",
    "Portugal": "pt",
    "Palau": "pw",
    "Paraguay": "py",
    "Qatar": "qa",
    "Réunion": "re",
    "Romania": "ro",
    "Serbia": "rs",
    "Russia": "ru",
    "Rwanda": "rw",
    "Saudi Arabia": "sa",
    "Solomon Islands": "sb",
    "Seychelles": "sc",
    "Sudan": "sd",
    "Sweden": "se",
    "Singapore": "sg",
    "Saint Helena, Ascension and Tristan da Cunha": "sh",
    "Slovenia": "si",
    "Svalbard and Jan Mayen": "sj",
    "Slovakia": "sk",
    "Sierra Leone": "sl",
    "San Marino": "sm",
    "Senegal": "sn",
    "Somalia": "so",
    "Suriname": "sr",
    "South Sudan": "ss",
    "São Tomé and Príncipe": "st",
    "El Salvador": "sv",
    "Sint Maarten": "sx",
    "Syria": "sy",
    "Eswatini (Swaziland)": "sz",
    "Turks and Caicos Islands": "tc",
    "Chad": "td",
    "French Southern and Antarctic Lands": "tf",
    "Togo": "tg",
    "Thailand": "th",
    "Tajikistan": "tj",
    "Tokelau": "tk",
    "Timor Leste": "tl",
    "Turkmenistan": "tm",
    "Tunisia": "tn",
    "Tonga": "to",
    "Turkey": "tr",
    "Trinidad and Tobago": "tt",
    "Tuvalu": "tv",
    "Taiwan": "tw",
    "Tanzania": "tz",
    "Ukraine": "ua",
    "Uganda": "ug",
    "United States Minor Outlying Islands": "um",
    "United Nations": "un",
    "United States": "us",
    "Alaska": "us-ak",
    "Alabama": "us-al",
    "Arkansas": "us-ar",
    "Arizona": "us-az",
    "California": "us-ca",
    "Colorado": "us-co",
    "Connecticut": "us-ct",
    "Delaware": "us-de",
    "Florida": "us-fl",
    "Hawaii": "us-hi",
    "Iowa": "us-ia",
    "Idaho": "us-id",
    "Illinois": "us-il",
    "Indiana": "us-in",
    "Kansas": "us-ks",
    "Kentucky": "us-ky",
    "Louisiana": "us-la",
    "Massachusetts": "us-ma",
    "Maryland": "us-md",
    "Maine": "us-me",
    "Michigan": "us-mi",
    "Minnesota": "us-mn",
    "Missouri": "us-mo",
    "Mississippi": "us-ms",
    "Montana": "us-mt",
    "North Carolina": "us-nc",
    "North Dakota": "us-nd",
    "Nebraska": "us-ne",
    "New Hampshire": "us-nh",
    "New Jersey": "us-nj",
    "New Mexico": "us-nm",
    "Nevada": "us-nv",
    "New York": "us-ny",
    "Ohio": "us-oh",
    "Oklahoma": "us-ok",
    "Oregon": "us-or",
    "Pennsylvania": "us-pa",
    "Rhode Island": "us-ri",
    "South Carolina": "us-sc",
    "South Dakota": "us-sd",
    "Tennessee": "us-tn",
    "Texas": "us-tx",
    "Utah": "us-ut",
    "Virginia": "us-va",
    "Vermont": "us-vt",
    "Washington": "us-wa",
    "Wisconsin": "us-wi",
    "West Virginia": "us-wv",
    "Wyoming": "us-wy",
    "Uruguay": "uy",
    "Uzbekistan": "uz",
    "Vatican City (Holy See)": "va",
    "Saint Vincent and the Grenadines": "vc",
    "Venezuela": "ve",
    "British Virgin Islands": "vg",
    "United States Virgin Islands": "vi",
    "Vietnam": "vn",
    "Vanuatu": "vu",
    "Wallis and Futuna": "wf",
    "Samoa": "ws",
    "Kosovo": "xk",
    "Yemen": "ye",
    "Mayotte": "yt",
    "South Africa": "za",
    "Zambia": "zm",
    "Zimbabwe": "zw"
}

// เอามาใช้แปลงชื่อประเทศเป็น code
export const tmdCountryMapping: Record<string, string> = {
    "เมียนมา": "mm",
    "พม่า": "mm",
    "ลาว": "la",
    "จีน": "cn",
    "อินเดีย": "in",
    "อินโดนีเซีย": "id",
    "ญี่ปุ่น": "jp",
    "ฟิลิปปินส์": "ph",
    "มาเลเซีย": "my",
    "เวียดนาม": "vn",
    "ไทย": "th",
    "กัมพูชา": "kh",
    "บังคลาเทศ": "bd",
    "เนปาล": "np",
    "ปากีสถาน": "pk",
    "อัฟกานิสถาน": "af",
};
