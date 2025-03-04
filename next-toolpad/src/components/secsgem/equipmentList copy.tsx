'use client'
import { useApiContext } from '@/src/context/apiContext';
import React, { useState, useEffect, useCallback } from 'react';
import {
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Typography, Paper, TablePagination, IconButton, TextField, Select, MenuItem,
    Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Button,
    Box, Toolbar,
    Stack,
    CircularProgress,
    Fade
} from '@mui/material';
import { Edit, Delete, Save, Cancel, Add } from '@mui/icons-material';

interface Equipment {
    _id: string;
    equipment_name: string;
    equipment_model: string;
    address: string;
    port: number;
    session_id: string;
    mode: string;
    enable: boolean;
}

// Delete Dialog Component
const DeleteDialog = ({
    open,
    onClose,
    onConfirm
}: {
    open: boolean;
    onClose: () => void;
    onConfirm: () => void;
}) => (
    <Dialog open={open} onClose={onClose}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Are you sure you want to delete this equipment? This action cannot be undone.
            </DialogContentText>
        </DialogContent>
        <DialogActions>
            <Button onClick={onClose} color="secondary">
                Cancel
            </Button>
            <Button onClick={onConfirm} color="error" autoFocus>
                Delete
            </Button>
        </DialogActions>
    </Dialog>
);

const CreateEquipmentDialog = ({
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
        session_id: '',
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
            newEquipment.session_id.trim() &&
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
            session_id: '',
            mode: 'ACTIVE',
            enable: false
        });
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Create New Equipment</DialogTitle>
            <DialogContent>
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
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="secondary">
                    Cancel
                </Button>
                <Button onClick={handleCreate} color="primary" variant="contained" disabled={!isFormValid()}>
                    Create
                </Button>
            </DialogActions>
        </Dialog>
    );
};


// Table Head Component with Sorting
const EquipmentTableHead = () => (
    <TableHead>
        <TableRow>
            <TableCell><Typography fontWeight="bold">Name</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Model</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">IP</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Port</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">ID</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Mode</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Enable</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Actions</Typography></TableCell>
        </TableRow>
    </TableHead>
);

// Equipment Row Component
const EquipmentRow = ({
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
                    <>
                        <IconButton color="primary" onClick={() => onSave(eq._id, editableData)}>
                            <Save />
                        </IconButton>
                        <IconButton color="secondary" onClick={onCancel}>
                            <Cancel />
                        </IconButton>
                    </>
                ) : (
                    <>
                        <IconButton color="primary" onClick={onEdit}>
                            <Edit />
                        </IconButton>
                        <IconButton color="error" onClick={onDeleteRequest}>
                            <Delete />
                        </IconButton>
                    </>
                )}
            </TableCell>
        </TableRow>
    );
};

// Main Component
export default function EquipmentList() {
    const { equipment } = useApiContext();
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [editRowId, setEditRowId] = useState<string | null>(null);
    const [deleteRowId, setDeleteRowId] = useState<string | null>(null);
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [sortBy, setSortBy] = useState('equipment_name');
    const [sortOrder, setSortOrder] = useState(1);

    // Data fetching with pagination and sorting
    useEffect(() => {
        equipment.gets(
            undefined,
            undefined,
            page + 1, // Convert to 1-based index
            rowsPerPage,
            sortBy,
            sortOrder
        );
    }, [page, rowsPerPage, sortBy, sortOrder]);

    const handleChangePage = (_: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(e.target.value, 10));
        setPage(0);
    };

    const refreshData = () => {
        equipment.gets(
            undefined,
            undefined,
            page + 1,
            rowsPerPage,
            sortBy,
            sortOrder
        ).catch(error => {
            console.error("Refresh data error:", error);
        });
    };

    const handleUpdate = async (id: string, data: Equipment) => {
        try {
            const response = await equipment.update(id, data);
            console.info("Response update:", response);
            refreshData();
            setEditRowId(null);

        } catch (error) {
            if (error instanceof Error) {
                console.error("Update failed:", error.message);
            } else {
                console.error("Update failed:", error);
            }
        }
    };

    const handleDelete = async () => {
        if (deleteRowId) {
            try {
                const response = await equipment.delete(deleteRowId);
                console.info("Response delete:", response);
                refreshData();
                setDeleteRowId(null);
            } catch (error) {
                if (error instanceof Error) {
                    console.error("Update failed:", error.message);
                } else {
                    console.error("Update failed:", error);
                }
            }
        }
    };

    const handleCreate = async (newEquipment: Equipment) => {
        try {
            const response = await equipment.create(newEquipment);
            console.info("Equipment created:", response);
            refreshData();
        } catch (error) {
            if (error instanceof Error) {
                console.error("Update failed:", error.message);
            } else {
                console.error("Update failed:", error);
            }
        }
    };

    return (
        <Box sx={{ width: '100%' }}>
            <Toolbar sx={{ justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Equipment List</Typography>
                {equipment.loading &&
                    <Fade in={equipment.loading} unmountOnExit>
                        <CircularProgress color="secondary" />
                    </Fade>
                }
                <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setCreateDialogOpen(true)}
                >
                    New Equipment
                </Button>
            </Toolbar>

            <TableContainer component={Paper}>
                <Table>
                    <EquipmentTableHead />
                    <TableBody>
                        {equipment.list.map((eq) => (
                            <EquipmentRow
                                key={eq._id}
                                eq={eq}
                                isEditing={editRowId === eq._id}
                                onEdit={() => setEditRowId(eq._id)}
                                onSave={handleUpdate}
                                onCancel={() => setEditRowId(null)}
                                onDeleteRequest={() => setDeleteRowId(eq._id)}
                            />
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <TablePagination
                rowsPerPageOptions={[5, 10, 25]}
                component="div"
                count={equipment.totalCount} // Use the totalCount from context
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
            />

            <DeleteDialog
                open={!!deleteRowId}
                onClose={() => setDeleteRowId(null)}
                onConfirm={handleDelete}
            />

            <CreateEquipmentDialog
                open={createDialogOpen}
                onClose={() => setCreateDialogOpen(false)}
                onCreate={handleCreate}
            />
        </Box>
    );
}