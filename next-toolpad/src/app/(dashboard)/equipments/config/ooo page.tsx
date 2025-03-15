import React from "react";
import Link from "next/link";
import data from "@/src/data/data.json";

interface Equipment {
    equipment_name: string;
    config: any[];
}

const ConfigPage = () => {
    return (
        <div>
            <h1>Config List</h1>
            {data.map((equipment: Equipment, index: number) => (
                <div key={index}>
                    <h2>{equipment.equipment_name}</h2>
                    <ul>
                        {equipment.config.map((config, i) => (
                            <li key={i}>
                                <strong>Package:</strong> {config.package8digit}
                                <Link href={`/equipments/config/edit/${equipment.equipment_name}-${config.package8digit}`}>
                                    Edit
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
            <Link href="/dashboard/equipments/config/add">Add New Config</Link>
        </div>
    );
};

export default ConfigPage;