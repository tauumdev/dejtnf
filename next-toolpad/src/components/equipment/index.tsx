'use client'
import React, { Fragment, useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, CircularProgress, Fade, IconButton, MenuItem, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Typography, Grid, Backdrop, Snackbar, Alert, TablePagination } from '@mui/material';
import { useApiContext } from '@/src/context/apiContext';
import { Add, Cancel, Delete, Edit, Key, Save } from '@mui/icons-material';
import { DeleteDialog } from './deleteDialog';

// Define interfaces for User and Equipment
interface User {
    name: string;
    email: string;
    role: string;
}

interface SecsGemEquipmentProps {
    user: User;
}

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

interface EditableTextFieldProps {
    label: string;
    value: string | number | boolean;
    editing: boolean;
    inputRef: React.RefObject<HTMLInputElement>;
    type?: 'text' | 'number';
    select?: boolean;
    children?: React.ReactNode;
}

// Component for editable text field
const EditableTextField: React.FC<EditableTextFieldProps> = ({
    label,
    value,
    editing,
    inputRef,
    type = 'text',
    select = false,
    children,
}) => {
    const defaultValue = typeof value === 'boolean' ? value.toString() : value;
    return editing ? (
        <TextField
            size="small"
            label={label}
            fullWidth
            autoComplete="off"
            defaultValue={defaultValue}
            inputRef={inputRef}
            type={type}
            select={select}
        >
            {children}
        </TextField>
    ) : (
        <Typography>{typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value}</Typography>
    );
};

// Main component for SECS/GEM Equipments
function SecsGemEquipments(props: SecsGemEquipmentProps) {
    const { user } = props;
    const { equipment } = useApiContext();

    // State variables for pagination, sorting, and editing
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [sortBy, setSortBy] = useState('equipment_name');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

    const [isEditing, setIsEditing] = useState(false)
    const [editingEquipment, setEditingEquipment] = useState<Equipment | null>(null);

    const [isAddNew, setIsAddNew] = useState(false)

    // State variables for Snackbar
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info' | 'warning'>('success');
    const [snackbarMessage, setSnackbarMessage] = useState('');

    // State variables for Delete Dialog
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [deleteEquipment, setDeleteEquipment] = useState<{ id: string, equipment_name: string }>({
        id: '',
        equipment_name: ''
    })
    const [deleteDialogMessage, setDeleteDialogMessage] = useState<string>('Are you sure you want to delete this item?')

    // Fetch equipment data on component mount or when pagination/sorting changes
    useEffect(() => {
        equipment.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder === 'asc' ? 1 : -1)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [page, rowsPerPage, sortBy, sortOrder])

    // Function to refresh data
    const refreshData = () => {
        equipment.gets(
            undefined,
            undefined,
            page + 1,
            rowsPerPage,
            sortBy,
            sortOrder === 'asc' ? 1 : -1
        ).catch(error => {
            console.error("Refresh data error:", error);
        });
    };

    // Handle page change
    const handleChangePage = (_: unknown, newPage: number) => {
        setPage(newPage);
    };

    // Handle rows per page change
    const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(e.target.value, 10));
        setPage(0);
    };

    // Handle errors from API requests
    const handleError = (error: any, defaultMessage: string): string => {
        // console.log(error); // Log the error for debugging

        // Handle array of errors (e.g., validation errors)
        if (Array.isArray(error)) {
            return error
                .map((err: any) => {
                    const fieldName = err.param || 'field';
                    const errorMsg = err.msg || 'Invalid value';
                    return `${fieldName}: ${errorMsg}`;
                })
                .join(', ');
        }

        // Handle error objects (e.g., Axios error responses)
        if (typeof error === 'object' && error !== null) {
            // Check for server validation errors
            if (error.response?.data?.errors) {
                return error.response.data.errors.msg || defaultMessage;
            }
            // Check for generic error messages
            if (error.message) {
                return error.message;
            }
            // Fallback to string representation
            return error.toString();
        }

        // Handle string errors
        if (typeof error === 'string') {
            return error;
        }

        // Return the default message if the error type is unknown
        return defaultMessage;
    };

    // Refs for add new equipment form fields
    const addRefs = {
        name: useRef<HTMLInputElement>(null),
        model: useRef<HTMLInputElement>(null),
        ip: useRef<HTMLInputElement>(null),
        port: useRef<HTMLInputElement>(null),
        id: useRef<HTMLInputElement>(null),
        mode: useRef<HTMLInputElement>(null),
        enable: useRef<HTMLInputElement>(null),
    }

    // Refs for edit equipment form fields
    const editRefs = {
        name: useRef<HTMLInputElement>(null),
        model: useRef<HTMLInputElement>(null),
        ip: useRef<HTMLInputElement>(null),
        port: useRef<HTMLInputElement>(null),
        id: useRef<HTMLInputElement>(null),
        mode: useRef<HTMLInputElement>(null),
        enable: useRef<HTMLInputElement>(null),
    }

    // Function to handle API requests with success and error handling
    const handleApiRequest = async (requestFn: () => Promise<any>, successMessage: string, errorMessage: string) => {
        try {
            const response = await requestFn();
            setSnackbarSeverity('success');
            setSnackbarMessage(successMessage);
            setOpenSnackbar(true);
            refreshData();
            return response;
        } catch (error) {
            const messages = handleError(error, errorMessage);
            setSnackbarSeverity('error');
            setSnackbarMessage(messages);
            setOpenSnackbar(true);
            throw error;
        }
    };

    // Function to save new equipment
    const handleSaveNewEquipment = async () => {

        if (!addRefs.name.current?.value || !addRefs.model.current?.value) {
            setSnackbarSeverity('error');
            setSnackbarMessage('Please fill in all required fields.');
            setOpenSnackbar(true);
            return;
        }

        const equipmentData: Equipment = {
            _id: '', // Provide a default or generated ID
            equipment_name: addRefs.name.current?.value || '',
            equipment_model: addRefs.model.current?.value as 'FCL' | 'FCLX',
            address: addRefs.ip.current?.value || '',
            port: parseInt(addRefs.port.current?.value || '0', 10),
            session_id: parseInt(addRefs.id.current?.value || '0', 10),
            mode: addRefs.mode.current?.value as 'ACTIVE' | 'PASSIVE',
            enable: addRefs.enable.current?.value === 'true',
        };

        await handleApiRequest(
            () => equipment.create(equipmentData),
            `${equipmentData.equipment_name} saved successfully`,
            'An error occurred while saving data'
        );
        setIsAddNew(false);

    };

    // Function to handle delete request
    const handleDeleteRequest = (id: string, equipment_name: string) => {
        setDeleteEquipment({ id, equipment_name });
        setDeleteDialogMessage(`Are you sure you want to delete ${equipment_name}?`);
        setDeleteDialogOpen(true);
    };

    // Function to handle delete confirmation
    const handleDelete = async () => {
        if (!deleteEquipment.id) {
            setSnackbarSeverity('error');
            setSnackbarMessage('No equipment selected for deletion.');
            setOpenSnackbar(true);
            return;
        }
        if (deleteEquipment.id) {
            try {
                const response = await equipment.delete(deleteEquipment.id);
                setSnackbarSeverity('success');
                setSnackbarMessage(`${deleteEquipment.equipment_name}  ${response.msg}`);
                setOpenSnackbar(true);

                refreshData();
                setDeleteEquipment({ id: '', equipment_name: '' })
                setDeleteDialogOpen(false);
            } catch (error) {
                const errorMessage = handleError(error, 'An error occurred while delete data');
                setSnackbarSeverity('error');
                setSnackbarMessage(errorMessage);
                setOpenSnackbar(true);
            }
        }
    };


    // Function to update equipment
    const handleUpdateEquipment = async () => {
        const equipmentUpdateData = {
            _id: editingEquipment?._id || '', // Provide a default or generated ID
            equipment_name: editRefs.name.current?.value || editingEquipment?.equipment_name,
            equipment_model: editRefs.model.current?.value as 'FCL' | 'FCLX' || editingEquipment?.equipment_model,
            address: editRefs.ip.current?.value || editingEquipment?.address,
            port: parseInt(editRefs.port.current?.value || editingEquipment?.port.toString() || '0', 10),
            session_id: parseInt(editRefs.id.current?.value || editingEquipment?.session_id.toString() || '0', 10),
            mode: editRefs.mode.current?.value as 'ACTIVE' | 'PASSIVE' || editingEquipment?.mode,
            enable: editRefs.enable.current?.value || editingEquipment?.enable,
        };

        await handleApiRequest(
            () => equipment.update(equipmentUpdateData._id, equipmentUpdateData),
            `${equipmentUpdateData.equipment_name} updated successfully`,
            'An error occurred while updated data'
        );
        setIsEditing(false);

    };

    // Show loading spinner if data is being fetched
    // if (equipment.loading) {
    //     return (
    //         <Backdrop
    //             sx={(theme) => ({ color: '#fff', zIndex: theme.zIndex.drawer + 1 })}
    //             open={equipment.loading}
    //         >
    //             <CircularProgress color="inherit" />
    //         </Backdrop>
    //     )
    // }

    // Main render
    return (
        <div>
            <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
                <Table size='small'>
                    <TableHead>
                        <TableRow>
                            <TableCell colSpan={user.role === 'admin' ? 8 : 7} sx={{ textAlign: 'center' }}>
                                <Fragment>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <Typography variant="h6">SECS/GEM Equipments</Typography>

                                        {equipment.loading &&
                                            <Fade in={equipment.loading} unmountOnExit>
                                                <CircularProgress size='small' color="secondary" />
                                            </Fade>
                                        }

                                        {user.role === 'admin' &&
                                            <Button
                                                size='small'
                                                variant="outlined"
                                                startIcon={<Add />}
                                                onClick={() => setIsAddNew(true)}
                                            >
                                                EQUIPMENT
                                            </Button>
                                        }
                                    </Box>
                                    {isAddNew &&
                                        <Grid container spacing={1} sx={{ pt: 2 }}>
                                            <Grid item xs={12} sm={6} md={4} lg={2}>
                                                <TextField
                                                    size='small'
                                                    label='Name'
                                                    fullWidth
                                                    autoComplete='off'
                                                    inputRef={addRefs.name}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.5}>
                                                <TextField
                                                    size='small'
                                                    label='Model'
                                                    fullWidth
                                                    select
                                                    inputRef={addRefs.model}
                                                    defaultValue="FCL"
                                                >
                                                    <MenuItem value={'FCL'}>FCL</MenuItem>
                                                    <MenuItem value={'FCLX'}>FCLX</MenuItem>
                                                </TextField>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={2}>
                                                <TextField
                                                    size='small'
                                                    label='IP'
                                                    fullWidth
                                                    autoComplete='off'
                                                    inputRef={addRefs.ip}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.2}>
                                                <TextField
                                                    size='small'
                                                    label='Port'
                                                    fullWidth
                                                    autoComplete='off'
                                                    type='number'
                                                    inputRef={addRefs.port}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.1}>
                                                <TextField
                                                    size='small'
                                                    label='ID'
                                                    fullWidth
                                                    autoComplete='off'
                                                    type='number'
                                                    inputRef={addRefs.id}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.4}>
                                                <TextField
                                                    size='small'
                                                    label='Mode'
                                                    fullWidth
                                                    select
                                                    inputRef={addRefs.mode}
                                                    defaultValue="ACTIVE"
                                                >
                                                    <MenuItem value={'ACTIVE'}>Active</MenuItem>
                                                    <MenuItem value={'PASSIVE'}>Passive</MenuItem>
                                                </TextField>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.2}>
                                                <TextField
                                                    size='small'
                                                    label='Enable'
                                                    fullWidth
                                                    select
                                                    inputRef={addRefs.enable}
                                                    defaultValue="false"
                                                >
                                                    <MenuItem value={'true'}>Yes</MenuItem>
                                                    <MenuItem value={'false'}>No</MenuItem>
                                                </TextField>
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.2}>
                                                <IconButton color="primary" onClick={handleSaveNewEquipment}>
                                                    <Save />
                                                </IconButton>
                                                <IconButton color="secondary" onClick={() => setIsAddNew(false)}>
                                                    <Cancel />
                                                </IconButton>
                                            </Grid>
                                        </Grid>
                                    }
                                </Fragment>
                            </TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell><Typography fontWeight="bold">Name</Typography></TableCell>
                            <TableCell><Typography fontWeight="bold">Model</Typography></TableCell>
                            <TableCell><Typography fontWeight="bold">IP</Typography></TableCell>
                            <TableCell><Typography fontWeight="bold">Port</Typography></TableCell>
                            <TableCell><Typography fontWeight="bold">ID</Typography></TableCell>
                            <TableCell><Typography fontWeight="bold">Mode</Typography></TableCell>
                            <TableCell><Typography fontWeight="bold">Enable</Typography></TableCell>
                            {user?.role === 'admin' &&
                                <TableCell><Typography fontWeight="bold">Action</Typography></TableCell>
                            }
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {equipment.list.map((eq) => (
                            <TableRow key={eq._id}>
                                <TableCell sx={{ pr: 0 }}>
                                    <EditableTextField label="Name" value={eq.equipment_name} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.name} />
                                </TableCell>
                                <TableCell sx={{ pr: 0 }}>
                                    <EditableTextField label="Model" value={eq.equipment_model} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.model} select >
                                        <MenuItem value="FCL">FCL</MenuItem>
                                        <MenuItem value="FCLX">FCLX</MenuItem>
                                    </EditableTextField>
                                </TableCell>
                                <TableCell sx={{ pr: 0 }}>
                                    <EditableTextField label="Ip" value={eq.address} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.ip} />
                                </TableCell>
                                <TableCell sx={{ pr: 0 }}>
                                    <EditableTextField label="Port" value={eq.port} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.port} type='number' />
                                </TableCell>
                                <TableCell sx={{ pr: 0 }}>
                                    <EditableTextField label="Id" value={eq.session_id} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.id} type='number' />
                                </TableCell>
                                <TableCell sx={{ pr: 0 }}>
                                    <EditableTextField label="Mode" value={eq.mode} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.mode} select >
                                        <MenuItem value="ACTIVE">ACTIVE</MenuItem>
                                        <MenuItem value="PASSIVE">PASSIVE</MenuItem>
                                    </EditableTextField>
                                </TableCell>
                                <TableCell sx={{ pr: 0 }}>
                                    <EditableTextField label="Enable" value={eq.enable} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.enable} select >
                                        <MenuItem value={'true'}>Yes</MenuItem>
                                        <MenuItem value={'false'}>No</MenuItem>
                                    </EditableTextField>
                                </TableCell>

                                {user?.role === 'admin' &&
                                    <TableCell sx={{ pr: 0 }}>
                                        {isEditing && editingEquipment?._id === eq._id ? (
                                            <Stack direction="row" spacing={1} alignItems="center">
                                                <IconButton color="primary" onClick={handleUpdateEquipment}>
                                                    <Save />
                                                </IconButton>
                                                <IconButton color="secondary" onClick={() => { setIsEditing(false) }}>
                                                    <Cancel />
                                                </IconButton>
                                            </Stack>
                                        ) : (
                                            <Stack direction="row" spacing={1} alignItems="center">
                                                <IconButton color="primary" onClick={() => { setEditingEquipment(eq); setIsEditing(true); }}>
                                                    <Edit />
                                                </IconButton>
                                                <IconButton color="error" onClick={() => handleDeleteRequest(eq._id, eq.equipment_name)}>
                                                    <Delete />
                                                </IconButton>
                                            </Stack>
                                        )}
                                    </TableCell>}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>

                <TablePagination
                    rowsPerPageOptions={[5, 10, 25]}
                    component="div"
                    count={equipment.totalCount || 0}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />

            </TableContainer>
            <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={() => setOpenSnackbar(false)}>
                <Alert
                    onClose={() => setOpenSnackbar(false)}
                    severity={snackbarSeverity}
                    variant="filled"
                    sx={{ width: '100%' }}
                >
                    {snackbarMessage}
                </Alert>
            </Snackbar>
            <DeleteDialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} onConfirm={handleDelete}
                message={deleteDialogMessage} />
        </div >
    )
}

// Prop types validation
SecsGemEquipments.propTypes = {
    user: PropTypes.shape({
        name: PropTypes.string.isRequired,
        email: PropTypes.string.isRequired,
        role: PropTypes.string.isRequired,
    }).isRequired,
}

export default SecsGemEquipments