import { NextResponse } from 'next/server';
import axios from 'axios';
import { countryMapping, EMSCEarthquakeResponse, EMSCEarthquakeFeature } from '../../../(dashboard)/earthquake/earthQuake';
import { log } from 'console';

export async function GET(req: Request) {
    try {
        const { searchParams } = new URL(req.url);
        const minMagnitude = searchParams.get("minMagnitude") || "4"; // ✅ ค่าเริ่มต้น 4
        const limit = searchParams.get("limit") || "3"; // ✅ ค่าเริ่มต้น 3
        const neighboring = searchParams.get("neighboring") === "true"; // ✅ แปลงเป็น boolean ที่แท้จริง

        // console.log(searchParams); // ✅ Debug searchParams

        // console.log("neighboring:", neighboring); // ✅ Debug neighboring

        const params: Record<string, any> = {
            format: "json",
            minmag: minMagnitude,
            limit: limit,
            ...(neighboring && { minlat: -10, maxlat: 40, minlon: 65, maxlon: 140 }) // ใส่พารามิเตอร์เฉพาะเมื่อ neighboring เป็น true
        };

        // log("EMSC Params:", params); // ✅ Debug Params
        const response = await axios.get("https://www.seismicportal.eu/fdsnws/event/1/query", { params: params });

        // console.log("EMSC Response:", response.data); // ✅ Debug Response

        // ✅ ใช้ response.data.features (เพราะ response.data เป็น Object)
        const earthquakes = response.data.features.map((quake: EMSCEarthquakeFeature) => {
            const place = quake.properties.flynn_region || ""; // ป้องกัน null
            const matchedCountry = Object.keys(countryMapping).find(
                key => place.toLowerCase().includes(key.toLowerCase())
            );

            const countryCode = matchedCountry ? countryMapping[matchedCountry] : null;

            return {
                ...quake,
                properties: {
                    ...quake.properties,
                    flagUrl: countryCode ? `https://flagcdn.com/w40/${countryCode}.png` : undefined
                }
            };
        });

        return NextResponse.json(earthquakes);
    } catch (error) {
        console.error("Error fetching EMSC data:", error); // ✅ Debug Error
        return NextResponse.json({ error: "Failed to fetch earthquake data" }, { status: 500 });
    }
}
