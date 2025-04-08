import { NextResponse } from 'next/server';
import axios from 'axios';
import { tmdCountryMapping, TMDEarthquakeFeature } from '@/src/app/(dashboard)/earthquake/earthQuake';
// import { countryMapping } from '../../../(dashboard)/earthquake/earthQuake';


// ตรวจหา country code
function getCountryCodeFromOriginThai(origin: string): string | undefined {
    const matchedKey = Object.keys(tmdCountryMapping).find(key =>
        origin.includes(key)
    );

    const isThailand = origin.includes("จ.") || origin.includes("อ.") || origin.includes("ต.");

    if (matchedKey) return tmdCountryMapping[matchedKey];
    if (isThailand) return "th";

    return undefined;
}

export async function GET(req: Request) {
    try {
        const { searchParams } = new URL(req.url);
        const minMagnitude = parseFloat(searchParams.get("minMagnitude") || "4");
        const limit = parseInt(searchParams.get("limit") || "3");
        // const neighboring = searchParams.get("neighboring") === "true";

        const response = await axios.get("https://data.tmd.go.th/api/DailySeismicEvent/v1/?uid=api&ukey=api12345&format=json");

        const rawList = response.data?.DailyEarthquakes || [];

        const processed: TMDEarthquakeFeature[] = await Promise.all(rawList.map(async (item: any) => {
            const countryCode = getCountryCodeFromOriginThai(item.OriginThai);

            return {
                properties: {
                    originThai: item.OriginThai,
                    dateTimeUTC: item.DateTimeUTC,
                    dateTimeThai: item.DateTimeThai,
                    depth: parseFloat(item.Depth),
                    magnitude: parseFloat(item.Magnitude),
                    latitude: parseFloat(item.Latitude),
                    longitude: parseFloat(item.Longitude),
                    titleThai: item.TitleThai,
                    flagUrl: countryCode ? `https://flagcdn.com/w40/${countryCode}.png` : undefined,
                }
            };
        }));

        // filter ตาม magnitude
        let filtered = processed.filter(q => q.properties.magnitude >= minMagnitude);

        // ถ้า neighboring === true: เอาเฉพาะแถบ SEA (มี flagUrl), ถ้า false เอาเฉพาะไทย
        // filtered = filtered.filter(q => {
        //     const isThailand = getCountryCodeFromOriginThai(q.properties.originThai) === "th";
        //     return neighboring ? true : isThailand;
        // });

        // sort by วันที่ใหม่สุดก่อน
        filtered.sort((a, b) =>
            new Date(b.properties.dateTimeThai).getTime() - new Date(a.properties.dateTimeThai).getTime()
        );

        return NextResponse.json(filtered.slice(0, limit));
    } catch (error) {
        console.error("Error fetching EMSC data:", error); // ✅ Debug Error
        return NextResponse.json({ error: "Failed to fetch earthquake data" }, { status: 500 });
    }
}
