import React from "react";
import Link from "next/link";

interface Equipment {
    equipment_name: string;
    config: any[];
}

interface EquipmentListProps {
    equipmentList: Equipment[];
}

const EquipmentList: React.FC<EquipmentListProps> = ({ equipmentList }) => {
    return (
        <div>
            {equipmentList.map((equipment, index) => (
                <div key={index}>
                    <h2>{equipment.equipment_name}</h2>
                    <ul>
                        {equipment.config.map((config, i) => (
                            <li key={i}>
                                <strong>Package:</strong> {config.package8digit}
                                <Link href={`config/edit/${equipment.equipment_name}-${config.package8digit}`}>
                                    Edit
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
};

export default EquipmentList;