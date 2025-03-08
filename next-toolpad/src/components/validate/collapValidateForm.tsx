import React, { useState } from 'react';
import {
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Collapse,
    Checkbox,
    FormControlLabel,
    TextField,
    Box,
    Button,
    Grid
} from '@mui/material';
import {
    ExpandMore,
    ExpandLess,
    Edit,
    Delete,
    Add,
    Save,
    Cancel
} from '@mui/icons-material';


interface EquipmentConfig {
    _id: string;
    equipment_name: string;
    config: {
        package8digit: string;
        selection_code: string;
        data_with_selection_code: {
            options: {
                use_operation_code: boolean;
                use_on_operation: boolean;
                use_lot_hold: boolean;
            };
            package_selection_code: string;
            operation_code: string;
            on_operation: string;
            validate_type: string;
            recipe_name: string;
            product_name: string;
            allow_tool_id: {
                [key: string]: string[];
            };
        }[];
    }[];
}

interface EquipmentConfigTableProps {
    data: EquipmentConfig[];
}

export const EditableEquipmentConfigTable = ({ data: initialData }: EquipmentConfigTableProps) => {
    const [data, setData] = useState<EquipmentConfig[]>(initialData);
    const [expanded, setExpanded] = useState<{
        equipment: number | null;
        config: number | null;
        data: number | null;
    }>({ equipment: null, config: null, data: null });
    console.log(initialData);

    const [editing, setEditing] = useState<{
        equipment: number | null;
        config: number | null;
        data: number | null;
    }>({ equipment: null, config: null, data: null });

    // ฟังก์ชันจัดการการขยาย/ยุบ
    const toggleExpand = (level: 'equipment' | 'config' | 'data', index: number) => {
        setExpanded(prev => ({
            ...prev,
            [level]: prev[level] === index ? null : index,
            ...(level === 'equipment' && { config: null, data: null }),
            ...(level === 'config' && { data: null }),
        }));
    };

    // ฟังก์ชันจัดการการแก้ไข
    const handleEdit = (level: 'equipment' | 'config' | 'data', index: number) => {
        setEditing(prev => ({ ...prev, [level]: index }));
    };

    // ฟังก์ชันยกเลิกการแก้ไข
    const handleCancel = (level: 'equipment' | 'config' | 'data') => {
        setEditing(prev => ({ ...prev, [level]: null }));
        setData(initialData); // รีเซ็ตข้อมูล
    };

    // ฟังก์ชันบันทึกการเปลี่ยนแปลง
    const handleSave = (level: 'equipment' | 'config' | 'data', index: number) => {
        setEditing(prev => ({ ...prev, [level]: null }));
        // ควรเพิ่มการอัปเดตข้อมูลไปยัง API ที่นี่
    };

    // ฟังก์ชันจัดการการเปลี่ยนแปลงข้อมูล
    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
        path: {
            equipmentIndex: number;
            configIndex?: number;
            dataIndex?: number;
            field: string;
        }
    ) => {
        const { equipmentIndex, configIndex, dataIndex, field } = path;
        const value = e.target.value;

        setData(prev => {
            const newData = [...prev];
            if (dataIndex !== undefined && configIndex !== undefined) {
                // ระดับ Data
                newData[equipmentIndex].config[configIndex].data_with_selection_code[dataIndex][field] = value;
            } else if (configIndex !== undefined) {
                // ระดับ Config
                newData[equipmentIndex].config[configIndex][field] = value;
            } else {
                // ระดับ Equipment
                newData[equipmentIndex][field] = value;
            }
            return newData;
        });
    };

    // ฟังก์ชันเพิ่มข้อมูลใหม่
    const handleAdd = (level: 'equipment' | 'config' | 'data', equipmentIndex?: number, configIndex?: number) => {
        const newItem = {
            // ... กำหนดโครงสร้างข้อมูลเริ่มต้นตามระดับ
        };

        setData(prev => {
            const newData = [...prev];
            // ... logic การเพิ่มข้อมูลตามระดับ
            return newData;
        });
    };

    // ฟังก์ชันลบข้อมูล
    const handleDelete = (
        level: 'equipment' | 'config' | 'data',
        equipmentIndex: number,
        configIndex?: number,
        dataIndex?: number
    ) => {
        setData(prev => {
            const newData = [...prev];
            // ... logic การลบข้อมูลตามระดับ
            return newData;
        });
    };

    // ส่วนแสดงผลสำหรับแต่ละระดับ
    const renderEditableField = (
        value: string,
        path: {
            equipmentIndex: number;
            configIndex?: number;
            dataIndex?: number;
            field: string;
        }
    ) => {
        return (
            <TextField
                value={value}
                onChange={(e) => handleChange(e, path)}
                size="small"
                fullWidth
            />
        );
    };

    // ส่วน UI สำหรับ Equipment Level
    return (
        <TableContainer component={Paper}>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell width="5%" />
                        <TableCell>Equipment Name</TableCell>
                        <TableCell>Total Configs</TableCell>
                        <TableCell>Actions</TableCell>
                    </TableRow>
                </TableHead>

                <TableBody>
                    {data.map((equipment, equipmentIndex) => (
                        <React.Fragment key={equipment.equipment_name}>
                            {/* Equipment Level */}
                            <TableRow>
                                <TableCell>
                                    <IconButton
                                        size="small"
                                        onClick={() => toggleExpand('equipment', equipmentIndex)}
                                    >
                                        {expanded.equipment === equipmentIndex ? <ExpandLess /> : <ExpandMore />}
                                    </IconButton>
                                </TableCell>

                                <TableCell>
                                    {editing.equipment === equipmentIndex ? (
                                        renderEditableField(equipment.equipment_name, {
                                            equipmentIndex,
                                            field: 'equipment_name'
                                        })
                                    ) : (
                                        equipment.equipment_name
                                    )}
                                </TableCell>

                                <TableCell>{equipment.config.length}</TableCell>

                                <TableCell>
                                    {editing.equipment === equipmentIndex ? (
                                        <>
                                            <IconButton onClick={() => handleSave('equipment', equipmentIndex)}>
                                                <Save fontSize="small" />
                                            </IconButton>
                                            <IconButton onClick={() => handleCancel('equipment')}>
                                                <Cancel fontSize="small" />
                                            </IconButton>
                                        </>
                                    ) : (
                                        <>
                                            <IconButton onClick={() => handleEdit('equipment', equipmentIndex)}>
                                                <Edit fontSize="small" />
                                            </IconButton>
                                            <IconButton
                                                onClick={() => handleDelete('equipment', equipmentIndex)}
                                                color="error"
                                            >
                                                <Delete fontSize="small" />
                                            </IconButton>
                                        </>
                                    )}
                                </TableCell>
                            </TableRow>

                            {/* Config Level */}
                            <TableRow>
                                <TableCell colSpan={4} sx={{ py: 0 }}>
                                    <Collapse in={expanded.equipment === equipmentIndex}>
                                        <Box sx={{ ml: 3, bgcolor: 'background.paper' }}>
                                            <Button
                                                startIcon={<Add />}
                                                onClick={() => handleAdd('config', equipmentIndex)}
                                                size="small"
                                            >
                                                Add Config
                                            </Button>

                                            {/* ... (ส่วน Config และ Data Level ที่ปรับให้แก้ไขได้) */}
                                            {/* Config Level */}
                                            <TableRow>
                                                <TableCell colSpan={3} sx={{ py: 0 }}>
                                                    <Collapse in={expanded.equipment === equipmentIndex}>
                                                        <Box sx={{ ml: 3, bgcolor: 'background.paper' }}>
                                                            <Table size="small">
                                                                <TableHead>
                                                                    <TableRow>
                                                                        <TableCell width="5%" />
                                                                        <TableCell>Package</TableCell>
                                                                        <TableCell>Selection Code</TableCell>
                                                                        <TableCell>Data Entries</TableCell>
                                                                    </TableRow>
                                                                </TableHead>

                                                                <TableBody>
                                                                    {equipment.config.map((config, configIndex) => (
                                                                        <React.Fragment key={config.package8digit}>
                                                                            <TableRow>
                                                                                <TableCell>
                                                                                    <IconButton
                                                                                        size="small"
                                                                                        onClick={() => toggleExpand('config', configIndex)}
                                                                                    >
                                                                                        {expanded.config === configIndex ? <ExpandLess /> : <ExpandMore />}
                                                                                    </IconButton>
                                                                                </TableCell>
                                                                                <TableCell>{config.package8digit}</TableCell>
                                                                                <TableCell>{config.selection_code}</TableCell>
                                                                                <TableCell>{config.data_with_selection_code.length}</TableCell>
                                                                            </TableRow>

                                                                            {/* Data Level */}
                                                                            <TableRow>
                                                                                <TableCell colSpan={4} sx={{ py: 0 }}>
                                                                                    <Collapse in={expanded.config === configIndex}>
                                                                                        <Box sx={{ ml: 3, bgcolor: 'background.default' }}>
                                                                                            <Table size="small">
                                                                                                <TableHead>
                                                                                                    <TableRow>
                                                                                                        <TableCell width="5%" />
                                                                                                        <TableCell>Package Selection</TableCell>
                                                                                                        <TableCell>Operation Code</TableCell>
                                                                                                        <TableCell>Validation Type</TableCell>
                                                                                                    </TableRow>
                                                                                                </TableHead>

                                                                                                <TableBody>
                                                                                                    {config.data_with_selection_code.map((dataItem, dataIndex) => (
                                                                                                        <React.Fragment key={dataIndex}>
                                                                                                            <TableRow>
                                                                                                                <TableCell>
                                                                                                                    <IconButton
                                                                                                                        size="small"
                                                                                                                        onClick={() => toggleExpand('data', dataIndex)}
                                                                                                                    >
                                                                                                                        {expanded.data === dataIndex ? <ExpandLess /> : <ExpandMore />}
                                                                                                                    </IconButton>
                                                                                                                </TableCell>
                                                                                                                <TableCell>{dataItem.package_selection_code}</TableCell>
                                                                                                                <TableCell>{dataItem.operation_code}</TableCell>
                                                                                                                <TableCell>{dataItem.validate_type}</TableCell>
                                                                                                            </TableRow>

                                                                                                            {/* Detail Level */}
                                                                                                            <TableRow>
                                                                                                                <TableCell colSpan={4} sx={{ py: 0 }}>
                                                                                                                    <Collapse in={expanded.data === dataIndex}>
                                                                                                                        <Box sx={{ ml: 3, p: 2 }}>
                                                                                                                            {/* Options */}
                                                                                                                            <Grid container spacing={2} sx={{ mb: 2 }}>
                                                                                                                                {Object.entries(dataItem.options).map(([key, value]) => (
                                                                                                                                    <Grid item xs={4} key={key}>
                                                                                                                                        <FormControlLabel
                                                                                                                                            control={<Checkbox checked={value} disabled />}
                                                                                                                                            label={key.replace(/_/g, ' ')}
                                                                                                                                        />
                                                                                                                                    </Grid>
                                                                                                                                ))}
                                                                                                                            </Grid>

                                                                                                                            {/* Main Fields */}
                                                                                                                            <Grid container spacing={2} sx={{ mb: 2 }}>
                                                                                                                                {[
                                                                                                                                    'recipe_name',
                                                                                                                                    'product_name',
                                                                                                                                    'on_operation'
                                                                                                                                ].map((field) => (
                                                                                                                                    <Grid item xs={4} key={field}>
                                                                                                                                        <TextField
                                                                                                                                            label={field.replace(/_/g, ' ')}
                                                                                                                                            value={dataItem[field as keyof typeof dataItem]}
                                                                                                                                            fullWidth
                                                                                                                                            size="small"
                                                                                                                                            disabled
                                                                                                                                        />
                                                                                                                                    </Grid>
                                                                                                                                ))}
                                                                                                                            </Grid>

                                                                                                                            {/* Tool IDs */}
                                                                                                                            <Grid container spacing={2}>
                                                                                                                                {Object.entries(dataItem.allow_tool_id).map(([pos, tools]) => (
                                                                                                                                    <Grid item xs={3} key={pos}>
                                                                                                                                        <TextField
                                                                                                                                            label={`Position ${pos.split('_')[1]}`}
                                                                                                                                            value={tools.join(', ') || 'None'}
                                                                                                                                            fullWidth
                                                                                                                                            size="small"
                                                                                                                                            disabled
                                                                                                                                        />
                                                                                                                                    </Grid>
                                                                                                                                ))}
                                                                                                                            </Grid>
                                                                                                                        </Box>
                                                                                                                    </Collapse>
                                                                                                                </TableCell>
                                                                                                            </TableRow>
                                                                                                        </React.Fragment>
                                                                                                    ))}
                                                                                                </TableBody>
                                                                                            </Table>
                                                                                        </Box>
                                                                                    </Collapse>
                                                                                </TableCell>
                                                                            </TableRow>
                                                                        </React.Fragment>
                                                                    ))}
                                                                </TableBody>
                                                            </Table>
                                                        </Box>
                                                    </Collapse>
                                                </TableCell>
                                            </TableRow>
                                        </Box>
                                    </Collapse>
                                </TableCell>
                            </TableRow>
                        </React.Fragment>
                    ))}
                </TableBody>
            </Table>

            <Button
                startIcon={<Add />}
                onClick={() => handleAdd('equipment')}
                sx={{ mt: 2 }}
            >
                Add New Equipment
            </Button>
        </TableContainer>
    );
};