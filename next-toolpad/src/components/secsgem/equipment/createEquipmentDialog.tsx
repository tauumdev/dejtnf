import { useState } from 'react';
import {
    Dialog, DialogTitle, DialogContent, DialogActions, Button,
    Box, TextField, Select, MenuItem
} from '@mui/material';
import { Equipment } from '../../../service/types';

export const CreateEquipmentDialog = ({
    open,
    onClose,
    onCreate
}: {
    open: boolean;
    onClose: () => void;
    onCreate: (data: Equipment) => Promise<void>;
}) => {
    const [newEquipment, setNewEquipment] = useState<Omit<Equipment, '_id'>>({
        equipment_name: '',
        equipment_model: 'FCL',
        address: '',
        port: 5000,
        session_id: 0,
        mode: 'ACTIVE',
        enable: false
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | { value: unknown }>, field: string) => {
        let value: any = e.target.value;
        if (field === 'enable') value = value === 'true';
        if (field === 'port') value = Number(value);
        setNewEquipment(prev => ({ ...prev, [field]: value }));
    };

    const isFormValid = () => {
        return (
            newEquipment.equipment_name.trim() &&
            newEquipment.address.trim() &&
            newEquipment.session_id &&
            newEquipment.port > 0
        );
    };

    const handleCreate = async () => {
        await onCreate({ ...newEquipment, _id: '' });
        onClose();
        setNewEquipment({
            equipment_name: '',
            equipment_model: 'FCL',
            address: '',
            port: 5000,
            session_id: 0,
            mode: 'ACTIVE',
            enable: false
        });
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Create New Equipment</DialogTitle>
            <DialogContent>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                    {/* ... rest of the form ... */}
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                        <TextField
                            label="Equipment Name"
                            value={newEquipment.equipment_name}
                            onChange={(e) => handleChange(e, 'equipment_name')}
                            fullWidth
                            required
                        />
                        <Select
                            value={newEquipment.equipment_model}
                            onChange={(e) => handleChange(e, 'equipment_model')}
                            fullWidth
                        >
                            <MenuItem value="FCL">FCL</MenuItem>
                            <MenuItem value="FCLX">FCLX</MenuItem>
                        </Select>
                        <TextField
                            label="IP Address"
                            value={newEquipment.address}
                            onChange={(e) => handleChange(e, 'address')}
                            fullWidth
                            required
                        />
                        <TextField
                            label="Port"
                            type="number"
                            value={newEquipment.port}
                            onChange={(e) => handleChange(e, 'port')}
                            fullWidth
                            required
                        />
                        <TextField
                            label="Session ID"
                            value={newEquipment.session_id}
                            onChange={(e) => handleChange(e, 'session_id')}
                            fullWidth
                            required
                        />
                        <Select
                            value={newEquipment.mode}
                            onChange={(e) => handleChange(e, 'mode')}
                            fullWidth
                        >
                            <MenuItem value="ACTIVE">ACTIVE</MenuItem>
                            <MenuItem value="PASSIVE">PASSIVE</MenuItem>
                        </Select>
                        <Select
                            value={newEquipment.enable ? "true" : "false"}
                            onChange={(e) => handleChange(e, 'enable')}
                            fullWidth
                        >
                            <MenuItem value="false">False</MenuItem>
                            <MenuItem value="true">True</MenuItem>
                        </Select>
                    </Box>
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="secondary">Cancel</Button>
                <Button onClick={handleCreate} color="primary" variant="contained" disabled={!isFormValid()}>
                    Create
                </Button>
            </DialogActions>
        </Dialog>
    );
};