'use client'
import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Box, Button, Card, CardContent, Checkbox, CircularProgress, Divider, FormControlLabel, Grid2, Skeleton, Stack, TextField, Typography } from '@mui/material';
import { keyframes } from '@emotion/react';
import { EMSCEarthquakeFeature, TMDEarthquakeFeature, USGSEarthquakeFeature } from './earthQuake';
import Image from 'next/image';
import { CheckBox } from '@mui/icons-material';
// import SoundAlert from './soundAlert';

const getMagnitudeColor = (mag: number) => {
    if (mag >= 7) return "#d32f2f"; // แดงเข้ม (รุนแรง)
    if (mag >= 6) return "#f57c00"; // ส้มเข้ม
    if (mag >= 5) return "#fbc02d"; // เหลือง
    return "#388e3c"; // เขียว (เบา)
};



export default function EarthQuake() {

    const [dataUSGS, setDataUSGS] = useState<USGSEarthquakeFeature[]>([]);
    const [dataEMSC, setDataEMSC] = useState<EMSCEarthquakeFeature[]>([]);
    const [dataTMD, setDataTMD] = useState<any[]>([]);
    const [loadingUSGS, setLoadingUSGS] = useState<boolean>(true);
    const [loadingEMSC, setLoadingEMSC] = useState<boolean>(true);
    const [loadingTMD, setLoadingTMD] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const previousEMSCDataRef = useRef<EMSCEarthquakeFeature[]>([]);
    const previousUSGSDataRef = useRef<USGSEarthquakeFeature[]>([]);
    const previousTMDDataRef = useRef<any[]>([]);
    const [newEarthquakeIds, setNewEarthquakeIds] = useState<Set<string>>(new Set());
    // const [magnitudeValue, setMagnitudeValue] = useState<number>(2);

    const [params, setParams] = useState<{ neighboring: boolean, minMagnitude: number, limit: number }>({
        neighboring: false,
        minMagnitude: 4,
        limit: 6
    });

    const soundAlert = useCallback((magnitude: number) => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.type = 'sine';
        gainNode.gain.value = Math.min(1, magnitude / 10);

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        const time = audioContext.currentTime;
        const duration = Math.min(6, Math.max(1, magnitude / 0.5));

        oscillator.frequency.setValueAtTime(500, time);
        oscillator.frequency.exponentialRampToValueAtTime(1500, time + 0.1);
        oscillator.frequency.exponentialRampToValueAtTime(500, time + duration - 0.1);

        gainNode.gain.setValueAtTime(0.2, time);
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.start(time);
        oscillator.stop(time + duration);
    }, []);

    const updateNewEarthquakeIds = (newData: any[], previousDataRef: React.MutableRefObject<any[]>) => {
        const newIds = new Set<string>();

        newData.forEach((quake) => {
            if (!previousDataRef.current.some((prevQuake) => prevQuake === quake)) {
                newIds.add(quake); // เพิ่ม ID ของข้อมูลใหม่
            }
        });

        setNewEarthquakeIds((prev) => {
            const updatedIds = new Set(prev);
            newIds.forEach((id) => updatedIds.add(id));
            return updatedIds;
        });
    };

    const [isDebouncing, setIsDebouncing] = useState(false); // เพื่อควบคุมการ debounce

    const paramsRef = useRef(params); // เก็บค่าของ params ปัจจุบัน
    const debounceTimer = useRef<NodeJS.Timeout | null>(null); // ใช้เก็บ timeout reference
    const refreshTimer = useRef<NodeJS.Timeout | null>(null); // ใช้เก็บ timeout reference

    useEffect(() => {
        paramsRef.current = params; // อัปเดตค่า paramsRef ทุกครั้งที่ params เปลี่ยนแปลง
    }, [params]);

    const sendNotification = async (message: string) => {
        console.log('send notify');

        try {
            await axios.post('/api/notify', { message });
            console.log("Notification sent successfully!");
        } catch (error) {
            console.error("Error sending notification:", error);
        }
    };

    useEffect(() => {
        const fetchEarthquakes = async () => {
            if (isDebouncing) return; // ถ้ากำลัง debounce อยู่ ไม่ให้ fetch ข้อมูล

            setIsDebouncing(true); // ตั้งค่า debounce เริ่มต้น

            console.log("เริ่มการดึงข้อมูลแผ่นดินไหว"); // Debug
            try {
                // ดึงข้อมูล TMD
                setLoadingTMD(true);

                const tmdResponse = await axios.get("/api/earthquakes/tmd", {
                    params: {
                        minMagnitude: paramsRef.current.minMagnitude,
                        limit: paramsRef.current.limit,
                        neighboring: paramsRef.current.neighboring
                    }
                });

                const newDataTMD: TMDEarthquakeFeature[] = tmdResponse.data;
                // console.log("New TMD data:", newDataTMD); // Debug

                // ตรวจสอบว่ามีข้อมูลใหม่เข้ามา แล้วเล่นเสียงเตือน
                if (
                    newDataTMD.length > 0 &&
                    previousTMDDataRef.current.length > 0 &&
                    newDataTMD[0]?.properties.dateTimeUTC !== previousTMDDataRef.current[0]?.properties.dateTimeUTC
                ) {
                    console.log("New TMD earthquake detected, playing alarm...");
                    updateNewEarthquakeIds([newDataTMD[0].properties.dateTimeUTC], previousTMDDataRef); // ใช้ dateTimeUTC แทน ID
                    soundAlert(newDataTMD[0]?.properties.magnitude); // ใช้ .magnitude แทน .mag ตาม type ของ TMD
                    // await sendNotification(`New TMD earthquake detected!: ${newDataTMD[0]?.properties.titleThai}`);
                    // const time = new Date(newDataTMD[0].properties.dateTimeThai).toLocaleString();
                    // const message = `${newDataTMD[0].properties.titleThai} Mag: ${newDataTMD[0].properties.magnitude} Depth: ${newDataTMD[0].properties.depth} km. ${time}`
                    // await sendNotification(message);
                }

                previousTMDDataRef.current = newDataTMD;
                setDataTMD(newDataTMD);
            } catch (error) {
                setError("Failed to fetch TMD earthquake data");
            } finally {
                setLoadingTMD(false);
            }

            try {
                // ดึงข้อมูล USGS
                setLoadingUSGS(true);
                const usgsResponse = await axios.get("/api/earthquakes/usgs", {
                    params: {
                        minMagnitude: paramsRef.current.minMagnitude,
                        limit: paramsRef.current.limit,
                        neighboring: paramsRef.current.neighboring
                    }
                });

                const newDataUSGS: USGSEarthquakeFeature[] = usgsResponse.data;

                if (
                    newDataUSGS.length > 0 &&
                    previousUSGSDataRef.current.length > 0 &&
                    newDataUSGS[0]?.id !== previousUSGSDataRef.current[0]?.id
                    // && newDataUSGS[0]?.properties.mag >= 2

                ) {
                    console.log("New USGS earthquake detected, playing alarm...");
                    updateNewEarthquakeIds([newDataUSGS[0]?.id], previousUSGSDataRef);
                    soundAlert(newDataUSGS[0]?.properties.mag);
                    // await sendNotification(`New USGS earthquake detected!: ${newDataUSGS[0]?.properties.title}`);
                    // const time = new Date(newDataUSGS[0].properties.time).toLocaleString();
                    // const message = `${newDataUSGS[0].properties.title} Mag: ${newDataUSGS[0].properties.mag} Depth: ${newDataUSGS[0].geometry.coordinates[2]} km. ${time}`
                    // await sendNotification(message);
                }

                previousUSGSDataRef.current = newDataUSGS;
                setDataUSGS(newDataUSGS);
            } catch (error) {
                setError("Failed to fetch USGS earthquake data");
            } finally {
                setLoadingUSGS(false);
            }

            try {
                // ดึงข้อมูล EMSC
                setLoadingEMSC(true);
                const emscResponse = await axios.get("/api/earthquakes/emsc", {
                    params: {
                        minMagnitude: paramsRef.current.minMagnitude,
                        limit: paramsRef.current.limit,
                        neighboring: paramsRef.current.neighboring
                    }
                });

                const newDataEMSC: EMSCEarthquakeFeature[] = emscResponse.data;
                if (
                    newDataEMSC.length > 0 &&
                    previousEMSCDataRef.current.length > 0 &&
                    newDataEMSC[0]?.id !== previousEMSCDataRef.current[0]?.id
                    // && newDataEMSC[0]?.properties.mag >= 2

                ) {
                    console.log("New EMSC earthquake detected, playing alarm...");
                    updateNewEarthquakeIds([newDataEMSC[0]?.id], previousEMSCDataRef);
                    soundAlert(newDataEMSC[0]?.properties.mag);
                    // const time = new Date(newDataEMSC[0].properties.time).toLocaleString();
                    // const message = `${newDataEMSC[0].properties.flynn_region} Mag: ${newDataEMSC[0].properties.mag} Depth: ${newDataEMSC[0].geometry.coordinates[1]} km. ${time}`
                    // await sendNotification(message);

                }

                previousEMSCDataRef.current = newDataEMSC;

                setDataEMSC(newDataEMSC);
            } catch (error) {
                setError("Failed to fetch EMSC earthquake data");
            } finally {
                setLoadingEMSC(false);
                setIsDebouncing(false); // หยุด debounce เมื่อดึงข้อมูลเสร็จ
            }
        };

        // 🔹 ถ้า params เปลี่ยน -> เริ่ม debounce ใหม่ (รอให้ผู้ใช้หยุดพิมพ์)
        if (debounceTimer.current) clearTimeout(debounceTimer.current);
        debounceTimer.current = setTimeout(fetchEarthquakes, 500);

        // 🔹 รีเฟรชข้อมูลทุก 1 นาที (ยกเลิกอันเก่า แล้วตั้งใหม่)
        if (refreshTimer.current) clearInterval(refreshTimer.current);
        refreshTimer.current = setInterval(fetchEarthquakes, 60000);

        return () => {
            if (debounceTimer.current) clearTimeout(debounceTimer.current);
            if (refreshTimer.current) clearInterval(refreshTimer.current);
        };

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [params]); // เมื่อ params เปลี่ยนแปลง จะทำการ debounce ใหม่

    useEffect(() => {
        const timer = setTimeout(() => {
            setNewEarthquakeIds(new Set()); // ล้างสถานะข้อมูลใหม่หลังจาก 20 วินาที
        }, 20000);

        return () => clearTimeout(timer);
    }, [newEarthquakeIds]);

    // ฟังก์ชันสำหรับสร้าง keyframes แบบไดนามิก
    const createBlinkAnimation = (color: string) => keyframes`
        0% { border-color: ${color}; }
        50% { border-color: transparent; }
        100% { border-color: ${color}; }
        `;

    // if (loading) return <CircularProgress />;
    if (error) return <Typography color="error">Error: {error}</Typography>;

    return (
        <Box sx={{ padding: 2 }}>
            {/* <pre>{JSON.stringify(params)}</pre> */}
            {/* <pre>{JSON.stringify(dataTMD, null, 2)}</pre> */}
            <Grid2 container spacing={2} sx={{ marginBottom: 2 }}>
                {/* <TextField size='small' type='number' onChange={(e) => setMagnitudeValue(Number(e.target.value))} value={magnitudeValue} label="Alarm Value">Magnitude</TextField>
                <Button onClick={() => soundAlert(magnitudeValue)} >Alert</Button> */}

                <Grid2 size={2.2}>
                    <TextField size='small' type='number' fullWidth
                        onChange={(e) => { setParams({ ...params, minMagnitude: Number(e.target.value) }) }}
                        value={params.minMagnitude} label="Min Magnitude"
                        InputProps={{
                            inputProps: {
                                max: 9, min: 1, step: "0.5"
                            }
                        }}
                        disabled={loadingUSGS || loadingEMSC}
                    >
                        Min Magnitude
                    </TextField>
                </Grid2>
                <Grid2 size={1.5}>
                    <TextField size='small' type='number' fullWidth
                        onChange={(e) => setParams({ ...params, limit: Number(e.target.value) })}
                        value={params.limit} label="Limit"
                        InputProps={{
                            inputProps: {
                                max: 15, min: 1, step: "1"
                            }
                        }}
                        disabled={loadingUSGS || loadingEMSC}
                    >
                        Query limit
                    </TextField>
                </Grid2>
                <Grid2>
                    <FormControlLabel control={<Checkbox
                        onChange={(e) => setParams({ ...params, neighboring: e.target.checked })}
                        checked={params.neighboring}
                        disabled={loadingUSGS || loadingEMSC}
                    />} label="Thailand and Neighbors" />
                </Grid2>

            </Grid2>

            {/* <pre>{JSON.stringify(data, null, 2)}</pre> */}
            {/* <pre>{JSON.stringify([...newEarthquakeIds], null, 2)}</pre> */}

            <Grid2 container spacing={3}>
                <Grid2 size={12} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="h6" gutterBottom>Recent Earthquakes TMD</Typography>
                    {loadingTMD && <CircularProgress size={20} />}
                </Grid2>

                {dataTMD?.map((quake: TMDEarthquakeFeature) => {
                    const quakeTime = new Date(quake.properties.dateTimeThai).toLocaleString();
                    const isNew = newEarthquakeIds.has(quake.properties.dateTimeUTC); // ตรวจสอบว่าเป็นข้อมูลใหม่หรือไม่

                    return (
                        <Grid2 size={4} key={quake.properties.dateTimeUTC}>
                            <Card
                                sx={{
                                    padding: 1,
                                    borderLeft: `5px solid ${getMagnitudeColor(quake.properties.magnitude)}`,
                                    ...(isNew && {
                                        animation: `${createBlinkAnimation(getMagnitudeColor(quake.properties.magnitude))} 1.2s infinite`,
                                    }),
                                }}
                            >
                                <CardContent>
                                    <Stack direction="row" alignItems="center" spacing={1} justifyContent="space-between">
                                        <Typography variant="h6" sx={{ color: getMagnitudeColor(quake.properties.magnitude) }}>
                                            Magnitude: {quake.properties.magnitude}
                                        </Typography>
                                        {quake.properties.flagUrl && (
                                            // eslint-disable-next-line @next/next/no-img-element
                                            <img
                                                src={quake.properties.flagUrl}
                                                alt="Country Flag"
                                                width={40}
                                                height={25}
                                                style={{ marginBottom: 8 }}
                                            />
                                        )}
                                    </Stack>
                                    <Typography variant="body1">{quake.properties.titleThai}</Typography>
                                    <Typography variant="body2" color="textSecondary">Time: {quakeTime}</Typography>
                                    <Typography variant="body2" color="textSecondary">Depth: {quake.properties.depth} km, long: {quake.properties.longitude}, lat:{quake.properties.latitude} </Typography>
                                </CardContent>
                            </Card>
                        </Grid2>
                    );
                })}
            </Grid2>
            <Divider sx={{ margin: 2 }} />
            <Grid2 container spacing={3}>
                <Grid2 size={12} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="h6" gutterBottom>Recent Earthquakes USGS</Typography>
                    {loadingUSGS && <CircularProgress size={20} />}
                </Grid2>

                {dataUSGS?.map((quake: USGSEarthquakeFeature) => {
                    const quakeTime = new Date(quake.properties.time).toLocaleString();
                    const updatedTime = new Date(quake.properties.updated).toLocaleString();
                    // const countryCode = extractCountryCode(quake.properties.place);
                    const isNew = newEarthquakeIds.has(quake.id);
                    const flagUrl = quake.properties.flagUrl;
                    return (
                        <Grid2 size={4} key={quake.id}>
                            <Card
                                sx={{
                                    padding: 1,
                                    borderLeft: `5px solid ${getMagnitudeColor(quake.properties.mag)}`,
                                    ...(isNew && {
                                        animation: `${createBlinkAnimation(getMagnitudeColor(quake.properties.mag))} 1.2s infinite`,
                                    }),
                                }}>
                                <CardContent>

                                    <Stack direction="row" alignItems="center" spacing={1} justifyContent={flagUrl ? 'space-between' : 'flex-start'}>
                                        <Typography variant="h6" sx={{ color: getMagnitudeColor(quake.properties.mag) }}>
                                            Magnitude: {quake.properties.mag}
                                        </Typography>
                                        {flagUrl && (
                                            // <Image
                                            //     src={flagUrl}
                                            //     alt="Country Flag"
                                            //     width={40}
                                            //     height={25}
                                            //     onError={(e) => (e.currentTarget.style.display = 'none')}
                                            // />

                                            // eslint-disable-next-line @next/next/no-img-element
                                            <img
                                                src={flagUrl}
                                                alt="Country Flag"
                                                width={40}
                                                height={25}
                                                style={{ marginBottom: 8 }}
                                            />
                                        )}
                                    </Stack>

                                    <Typography variant="body1">{quake.properties.place}</Typography>
                                    <Typography variant="body2" color="textSecondary">Time: {quakeTime}</Typography>
                                    <Typography variant="body2" color="textSecondary">Updated: {updatedTime}</Typography>
                                    <Typography variant="body2" color="textSecondary">Depth: {quake.geometry.coordinates[2]} km  long: {quake.geometry.coordinates[0]}, lat:{quake.geometry.coordinates[1]}</Typography>
                                    <Typography variant="body2">
                                        <a href={quake.properties.url} target="_blank" rel="noopener noreferrer">More Info</a>
                                    </Typography>
                                    {/* <Typography variant="body2">
                                        <a href={quake.properties.detail} target="_blank" rel="noopener noreferrer">More Detail Info</a>
                                    </Typography> */}
                                    {/* <pre>{JSON.stringify(quake, null, 2)}</pre> */}
                                </CardContent>
                            </Card>
                        </Grid2>
                    );
                })}
            </Grid2>

            <Divider sx={{ margin: 2 }} />
            <Grid2 container spacing={3}>
                <Grid2 size={12} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="h6" gutterBottom>Recent Earthquakes EMSC</Typography>
                    {loadingEMSC && <CircularProgress size={20} />}
                </Grid2>
                {dataEMSC?.map((quake: EMSCEarthquakeFeature) => {
                    const quakeTime = new Date(quake.properties.time).toLocaleString();
                    const updatedTime = new Date(quake.properties.lastupdate).toLocaleString();
                    // const countryCode = extractCountryCode(quake.properties.place);
                    const isNew = newEarthquakeIds.has(quake.id);
                    const flagUrl = quake.properties.flagUrl;
                    return (
                        <Grid2 size={4} key={quake.id}>
                            <Card
                                sx={{
                                    padding: 1,
                                    borderLeft: `5px solid ${getMagnitudeColor(quake.properties.mag)}`,
                                    ...(isNew && {
                                        animation: `${createBlinkAnimation(getMagnitudeColor(quake.properties.mag))} 1.2s infinite`,
                                    }),
                                }}>

                                <CardContent>

                                    <Stack direction="row" alignItems="center" spacing={1} justifyContent={flagUrl ? 'space-between' : 'flex-start'}>
                                        <Typography variant="h6" sx={{ color: getMagnitudeColor(quake.properties.mag) }}>
                                            Magnitude: {quake.properties.mag}
                                        </Typography>
                                        {flagUrl && (
                                            // <Image
                                            //     src={flagUrl}
                                            //     alt="Country Flag"
                                            //     width={40}
                                            //     height={25}
                                            //     onError={(e) => (e.currentTarget.style.display = 'none')}
                                            // />

                                            // eslint-disable-next-line @next/next/no-img-element
                                            <img
                                                src={flagUrl}
                                                alt="Country Flag"
                                                width={40}
                                                height={25}
                                                style={{ marginBottom: 8 }}
                                            />
                                        )}
                                    </Stack>

                                    <Typography variant="body1">{quake.properties.flynn_region}</Typography>
                                    <Typography variant="body2" color="textSecondary">Time: {quakeTime}</Typography>
                                    <Typography variant="body2" color="textSecondary">Updated: {updatedTime}</Typography>
                                    <Typography variant="body2" color="textSecondary">Depth: {quake.properties.depth} km,
                                        long: {quake.geometry.coordinates[0]}, lat:{quake.geometry.coordinates[1]}</Typography>
                                    {/* <Typography variant="body2">
                                        <a href={quake.properties.url} target="_blank" rel="noopener noreferrer">More Info</a>
                                    </Typography> */}
                                    {/* <pre>{JSON.stringify(quake, null, 2)}</pre> */}
                                </CardContent>
                            </Card>
                        </Grid2>
                    );
                })}
            </Grid2>
        </Box>
    );
}
