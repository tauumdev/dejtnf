'use client'
import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import EquipmentForm from "@/src/components/EquipmentForm";
import data from "@/src/data/data.json";
import { useApiContext } from '@/src/context/apiContext'
const EditConfigPage = () => {
    const router = useRouter();
    const params = useParams();
    const { id } = params; // ดึงค่า id จาก URL
    const [equipmentData, setEquipmentData] = useState<any>(null);

    const { validate } = useApiContext();

    useEffect(() => {
        if (id) {
            const [equipmentName, package8digit] = (id as string).split(",");
            console.log(equipmentName);
            console.log(package8digit);

            const equipment = data.find((item) => item.equipment_name === equipmentName);
            if (equipment) {
                const config = equipment.config.find((item) => item.package8digit === package8digit);
                if (config) {
                    setEquipmentData(config);
                }
            }
        }
    }, [id]);

    const handleSubmit = (updatedData: any) => {
        // ส่งข้อมูลไปยัง API หรือบันทึกลงไฟล์ JSON
        console.log("Updated Data:", updatedData);
        router.push("/equipments/config"); // กลับไปที่หน้ารายการ
    };

    if (!equipmentData) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Edit Config</h1>
            <EquipmentForm initialData={equipmentData} onSubmit={handleSubmit} />
        </div>
    );
};

export default EditConfigPage;