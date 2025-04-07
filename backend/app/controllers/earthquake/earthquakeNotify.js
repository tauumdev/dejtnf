require('dotenv').config();
const axios = require('axios');
const line = require('@line/bot-sdk');

const client = new line.Client({
    channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN,
    channelSecret: process.env.CHANNEL_SECRET,
});

const lastNotifiedTimes = {
    TMD: null,
    USGS: null,
    EMSC: null,
};

// ✅ แปลงพิกัดเป็นชื่อประเทศและ emoji ธงชาติ
async function getCountryFlag(lat, lon) {
    try {
        const res = await axios.get('https://nominatim.openstreetmap.org/reverse', {
            params: {
                format: 'json',
                lat,
                lon,
                zoom: 3, // country level
                addressdetails: 1
            },
            headers: { 'User-Agent': 'earthquake-alert-app' }
        });

        if (res.data && res.data.address && res.data.address.country) {
            const country = res.data.address.country;
            const countryCode = res.data.address.country_code;
            const flag = getFlagEmoji(countryCode);
            return { country, flag };
        } else {
            console.error("❌ ไม่พบข้อมูลประเทศจาก Nominatim API");
            return { country: 'Unknown', flag: '' };
        }
    } catch (err) {
        console.error(`❌ reverse geocoding ล้มเหลว: ${err.message}`);
        return { country: 'Unknown', flag: '' };
    }
}

// ✅ แปลง country code เป็น flag emoji
function getFlagEmoji(countryCode) {
    const codePoints = countryCode
        .toUpperCase()
        .split('')
        .map(char => 127397 + char.charCodeAt());
    return String.fromCodePoint(...codePoints);
}

function createMapLink(lat, lon) {
    return `https://maps.google.com/?q=${lat},${lon}`;
}

async function fetchTMD() {
    const res = await axios.get('https://data.tmd.go.th/api/DailySeismicEvent/v1/?uid=api&ukey=api12345&format=json');
    const latest = res.data.DailyEarthquakes[0];
    const lat = latest.Latitude;
    const lon = latest.Longitude;

    const { country, flag } = await getCountryFlag(lat, lon);
    return {
        source: 'TMD',
        time: new Date(latest.DateTimeUTC),
        message: `
            ${flag} [TMD] แผ่นดินไหวใน ${country}
            📅 ${latest.DateTimeThai}
            📍 ${lat}, ${lon}
            📏 ${latest.Magnitude} ML
            📌 ${latest.TitleThai}
            🗺️ ${createMapLink(lat, lon)}
        `.trim()
    };
}

async function fetchUSGS() {
    const res = await axios.get('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson');
    const latest = res.data.features[0];
    const lat = latest.geometry.coordinates[1];
    const lon = latest.geometry.coordinates[0];
    const mag = parseFloat(latest.properties.mag);


    const { country, flag } = await getCountryFlag(lat, lon);
    return {
        source: 'USGS',
        time: new Date(latest.properties.time),
        message: `
${flag} [USGS] Earthquake in ${country}
📅 ${new Date(latest.properties.time).toLocaleString('th-TH')}
📍 ${lat}, ${lon}
📏 ${mag} ML
📌 ${latest.properties.place}
🗺️ ${createMapLink(lat, lon)}
        `.trim()
    };
}

async function fetchEMSC() {
    const res = await axios.get('https://www.seismicportal.eu/fdsnws/event/1/query?limit=1&format=json');
    const latest = res.data.features[0];
    const props = latest.properties;
    const coords = latest.geometry.coordinates;
    const lat = coords[1];
    const lon = coords[0];
    const mag = parseFloat(props.mag);

    const { country, flag } = await getCountryFlag(lat, lon);
    return {
        source: 'EMSC',
        time: new Date(latest.properties.time),
        message: `
${flag} [EMSC] Earthquake in ${country}
📅 ${new Date(latest.properties.time).toLocaleString('th-TH')}
📍 ${lat}, ${lon}
📏 ${mag} ML
📌 ${latest.properties.flynn_region}
🗺️ ${createMapLink(lat, lon)}
        `.trim()
    };
}

// ✅ ส่งข้อความด้วย line bot
async function sendLineBotMessage(message) {
    await client.pushMessage(process.env.CHANNEL_USERID, {
        type: 'text',
        text: message,
    });
}

let isFirstRun = true; // เพิ่มตัวแปรเช็คว่าเป็นการรันครั้งแรกหรือไม่

// ✅ ตรวจสอบและส่งข้อความ
async function checkEarthquakes() {
    try {
        const minMag = parseFloat(process.env.MIN_MAGNITUDE) || 4.5;
        const sources = [fetchTMD, fetchUSGS, fetchEMSC];

        // ข้ามการแจ้งเตือนรอบแรกสำหรับทุกแหล่งข้อมูล
        if (isFirstRun) {
            isFirstRun = false;
            console.log("🕒 ข้ามการแจ้งเตือนรอบแรกจากทุกแหล่งข้อมูล");
            return; // ไม่ให้ทำงานในรอบแรก
        }

        for (const fetchFn of sources) {
            try {
                const data = await fetchFn();
                const { source, time, message } = data;

                const matchedMag = message.match(/📏 ([\d.]+) ML/);
                const mag = matchedMag ? parseFloat(matchedMag[1]) : 0;

                if (mag >= minMag) {
                    if (!lastNotifiedTimes[source] || time > lastNotifiedTimes[source]) {
                        await sendLineBotMessage(message);
                        lastNotifiedTimes[source] = time;
                        console.log(`🔔 แจ้งเตือนใหม่จาก ${source} (mag ${mag})`);
                    } else {
                        console.log(`✅ ${source} ไม่มีเหตุการณ์ใหม่`);
                    }
                } else {
                    console.log(`⚠️ ${source} magnitude ${mag} < ${minMag} — ไม่แจ้งเตือน`);
                }
            } catch (err) {
                console.error(`❌ ดึงข้อมูล ${fetchFn.name} ล้มเหลว: ${err.message}`);
            }
        }
    } catch (error) {
        console.error('❌ เกิดข้อผิดพลาดรวม:', error.message);
    }
}

function startEarthquakeChecker(interval = 2 * 60 * 1000) {
    setInterval(checkEarthquakes, interval);
    checkEarthquakes(); // run ทันที
}

module.exports = { startEarthquakeChecker };
