export interface Equipment {
    _id: string;
    address: string;
    createdAt: string;  // ใช้ `string` เพราะเป็นรูปแบบ ISO 8601
    updatedAt: string;
    enable: boolean;
    equipment_model: string;
    equipment_name: string;
    mode: "ACTIVE" | "PASSIVE"; // หรือเพิ่ม mode อื่นหากมี
    port: number;
    session_id: number;
}


export interface EquipmentResponse {
    docs: Equipment[];  // อาร์เรย์ของอุปกรณ์
    hasNextPage: boolean;
    hasPrevPage: boolean;
    limit: number;
    nextPage: number | null;
    page: number;
    pagingCounter: number;
    prevPage: number | null;
    totalDocs: number;
    totalPages: number;
}

