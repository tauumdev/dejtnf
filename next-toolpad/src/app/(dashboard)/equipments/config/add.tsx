import React, { useState } from "react";
// import EquipmentForm from "@src/components/EquipmentForm";
import { useRouter } from "next/router";
import EquipmentForm from "@/src/components/EquipmentForm";

const AddPage: React.FC = () => {
    const router = useRouter();

    const handleSubmit = (newData: any) => {
        // ส่งข้อมูลไปยัง API หรือบันทึกลงไฟล์ JSON
        console.log("New Data:", newData);
        router.push("/"); // กลับไปที่หน้าหลัก
    };

    return (
        <div>
            <h1>Add New Equipment</h1>
            <EquipmentForm onSubmit={handleSubmit} />
        </div>
    );
};

export default AddPage;