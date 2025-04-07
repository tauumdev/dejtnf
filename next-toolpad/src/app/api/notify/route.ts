// pages/api/notification.ts
import { NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(req: Request) {
    try {
        const { message } = await req.json(); // รับข้อมูลจาก body ของ request
        console.log(message);

        if (!message) {
            return NextResponse.json({ error: 'Message is required' }, { status: 400 });
        }

        // ส่วนนี้เป็นตัวอย่างการส่งข้อมูลไปยัง API ของ LINE
        // ตัวอย่างการเรียก LINE Notification API

        await axios.post('http://localhost:3000/api/notification', { message });

        console.log("Notification message sent:", message); // Debug

        return NextResponse.json({ success: true, message: "Notification sent successfully!" });
    } catch (error) {
        console.error('Error sending notification:', error);
        return NextResponse.json({ error: "Failed to send notification" }, { status: 500 });
    }
}
