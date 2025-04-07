import { NextResponse } from 'next/server';
import axios from 'axios';
import { countryMapping } from '../../../(dashboard)/earthquake/earthQuake';
// import { countryMapping } from '@/utils/countryMapping'; // นำเข้า Mapping Country

export async function GET(req: Request) {
    try {
        const { searchParams } = new URL(req.url);
        // รับพารามิเตอร์จาก query string
        const minMagnitude = searchParams.get("minMagnitude") || "4"; // ค่าเริ่มต้น 3
        const limit = searchParams.get("limit") || "3"; // ค่าเริ่มต้น 10
        const neighboring = searchParams.get("neighboring") === "true"; // ✅ แปลงเป็น boolean ที่แท้จริง

        // console.log(searchParams); // ✅ Debug searchParams

        const params: Record<string, any> = {
            format: "geojson",
            minmagnitude: minMagnitude,
            limit: limit,
            orderby: 'time',
            ...(neighboring && { minlatitude: -10, maxlatitude: 40, minlongitude: 65, maxlongitude: 140 }) // ใส่พารามิเตอร์เฉพาะเมื่อ neighboring เป็น true
        };

        // console.log("USGS Params:", params); // ✅ Debug Params

        const response = await axios.get("https://earthquake.usgs.gov/fdsnws/event/1/query", { params });
        // console.log("USGS Response:", response.data.metadata); // ✅ Debug Response


        const earthquakes = response.data.features.map((quake: any) => {
            const place = quake.properties.place;
            const matchedCountry = Object.keys(countryMapping).find(
                key => place.toLowerCase().includes(key.toLowerCase())
            );

            const countryCode = matchedCountry ? countryMapping[matchedCountry] : null;

            return {
                ...quake,
                // countryCode,
                // flagUrl: countryCode ? `https://flagcdn.com/w40/${countryCode}.png` : null
                properties: {
                    ...quake.properties,
                    flagUrl: countryCode ? `https://flagcdn.com/w40/${countryCode}.png` : undefined
                }
            };
        });

        return NextResponse.json(earthquakes);
    } catch (error) {
        return NextResponse.json({ error: "Failed to fetch earthquake data" }, { status: 500 });
    }
}
