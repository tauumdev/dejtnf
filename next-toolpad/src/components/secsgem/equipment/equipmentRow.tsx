import { useState, useEffect } from 'react';
import {
    TableRow, TableCell, Typography,
    TextField, Select, MenuItem, IconButton,
    Stack
} from '@mui/material';
import { Edit, Delete, Save, Cancel } from '@mui/icons-material';
import { Equipment } from '../../../service/types';

export const EquipmentRow = ({
    eq,
    isEditing,
    onEdit,
    onSave,
    onCancel,
    onDeleteRequest
}: {
    eq: Equipment;
    isEditing: boolean;
    onEdit: () => void;
    onSave: (id: string, data: Equipment) => void;
    onCancel: () => void;
    onDeleteRequest: () => void;
}) => {
    const [editableData, setEditableData] = useState<Equipment>({ ...eq });

    useEffect(() => {
        if (isEditing) setEditableData({ ...eq });
    }, [isEditing, eq]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | { value: unknown }>, field: string) => {
        let value: any = e.target.value;
        if (field === 'enable') value = value === 'true';
        if (field === 'port') value = Number(value);
        setEditableData(prev => ({ ...prev, [field]: value }));
    };

    return (
        <TableRow>
            {/* Name */}
            <TableCell>
                {isEditing ? (
                    <TextField
                        value={editableData.equipment_name}
                        onChange={(e) => handleChange(e, 'equipment_name')}
                        size="small"
                    />
                ) : (
                    <Typography variant="body2">{eq.equipment_name}</Typography>
                )}
            </TableCell>

            {/* Model */}
            <TableCell>
                {isEditing ? (
                    <Select
                        value={editableData.equipment_model}
                        onChange={(e) => handleChange(e, 'equipment_model')}
                        size="small"
                        fullWidth
                    >
                        <MenuItem value="FCL">FCL</MenuItem>
                        <MenuItem value="FCLX">FCLX</MenuItem>
                    </Select>
                ) : (
                    <Typography variant="body2">{eq.equipment_model}</Typography>
                )}
            </TableCell>

            {/* IP Address */}
            <TableCell>
                {isEditing ? (
                    <TextField
                        value={editableData.address}
                        onChange={(e) => handleChange(e, 'address')}
                        size="small"
                    />
                ) : (
                    <Typography variant="body2">{eq.address}</Typography>
                )}
            </TableCell>

            {/* Port */}
            <TableCell>
                {isEditing ? (
                    <TextField
                        value={editableData.port}
                        onChange={(e) => handleChange(e, 'port')}
                        size="small"
                    />
                ) : (
                    <Typography variant="body2">{eq.port}</Typography>
                )}
            </TableCell>

            {/* Session ID */}
            <TableCell>
                {isEditing ? (
                    <TextField
                        value={editableData.session_id}
                        onChange={(e) => handleChange(e, 'session_id')}
                        size="small"
                    />
                ) : (
                    <Typography variant="body2">{eq.session_id}</Typography>
                )}
            </TableCell>

            {/* Mode */}
            <TableCell>
                {isEditing ? (
                    <Select
                        value={editableData.mode}
                        onChange={(e) => handleChange(e, 'mode')}
                        size="small"
                        fullWidth
                    >
                        <MenuItem value="ACTIVE">ACTIVE</MenuItem>
                        <MenuItem value="PASSIVE">PASSIVE</MenuItem>
                    </Select>
                ) : (
                    <Typography variant="body2">{eq.mode}</Typography>
                )}
            </TableCell>

            {/* Enable */}
            <TableCell>
                {isEditing ? (
                    <Select
                        value={editableData.enable ? "true" : "false"}
                        onChange={(e) => handleChange(e, 'enable')}
                        size="small"
                        fullWidth
                    >
                        <MenuItem value="true">True</MenuItem>
                        <MenuItem value="false">False</MenuItem>
                    </Select>
                ) : (
                    <Typography variant="body2">{eq.enable ? "True" : "False"}</Typography>
                )}
            </TableCell>

            {/* Actions */}
            <TableCell>
                {isEditing ? (
                    <Stack direction="row" spacing={1} alignItems="center">
                        <IconButton color="primary" onClick={() => onSave(eq._id, editableData)}>
                            <Save />
                        </IconButton>
                        <IconButton color="secondary" onClick={onCancel}>
                            <Cancel />
                        </IconButton>
                    </Stack>
                ) : (
                    <Stack direction="row" spacing={1} alignItems="center">
                        <IconButton color="primary" onClick={onEdit}>
                            <Edit />
                        </IconButton>
                        <IconButton color="error" onClick={onDeleteRequest}>
                            <Delete />
                        </IconButton>
                    </Stack>
                )}
            </TableCell>
        </TableRow>
    );
};