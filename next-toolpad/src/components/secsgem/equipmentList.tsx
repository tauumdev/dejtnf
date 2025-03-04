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
import { EquipmentRow } from './equipment/equipmentRow';
import { EquipmentTableHead } from './equipment/equipmentTableHead';
import { DeleteDialog } from './equipment/deleteDialog';
import { CreateEquipmentDialog } from './equipment/createEquipmentDialog';

interface Equipment {
    _id: string;
    equipment_name: string;
    equipment_model: string;
    address: string;
    port: number;
    session_id: number;
    mode: 'ACTIVE' | 'PASSIVE';
    enable: boolean;
}

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
        // eslint-disable-next-line react-hooks/exhaustive-deps
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