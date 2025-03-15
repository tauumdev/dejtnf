'use client'
import React, { Fragment, useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, CircularProgress, Fade, IconButton, MenuItem, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Typography, Grid, Backdrop, Snackbar, Alert, TablePagination } from '@mui/material';
import { useApiContext } from '@/src/context/apiContext';
import { Add, Cancel, Delete, Edit, Save } from '@mui/icons-material';
import { DeleteDialog } from './deleteDialog';

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

interface EquipmentRowProps {
    user: User;
    eq: Equipment;
    isEditing: boolean;
    editingEquipment: Equipment | null;
    editRefs: {
        name: React.RefObject<HTMLInputElement>;
        model: React.RefObject<HTMLInputElement>;
        ip: React.RefObject<HTMLInputElement>;
        port: React.RefObject<HTMLInputElement>;
        id: React.RefObject<HTMLInputElement>;
        mode: React.RefObject<HTMLInputElement>;
        enable: React.RefObject<HTMLInputElement>;
    };
    onEdit: (eq: Equipment) => void;
    onDelete: (id: string, name: string) => void;
    onSave: () => void;
    onCancel: () => void;
}

const EquipmentRow: React.FC<EquipmentRowProps> = ({
    user,
    eq,
    isEditing,
    editingEquipment,
    editRefs,
    onEdit,
    onDelete,
    onSave,
    onCancel,
}) => {
    const isEditingRow = isEditing && editingEquipment?._id === eq._id;

    return (
        <TableRow key={eq._id}>
            <TableCell>
                <EditableTextField
                    label="Name"
                    value={eq.equipment_name}
                    editing={isEditingRow}
                    inputRef={editRefs.name}
                />
            </TableCell>
            <TableCell>
                <EditableTextField
                    label="Model"
                    value={eq.equipment_model}
                    editing={isEditingRow}
                    inputRef={editRefs.model}
                    select
                >
                    <MenuItem value="FCL">FCL</MenuItem>
                    <MenuItem value="FCLX">FCLX</MenuItem>
                </EditableTextField>
            </TableCell>
            {/* Repeat for other fields */}
            {user?.role === 'admin' && (
                <TableCell>
                    {isEditingRow ? (
                        <Stack direction="row" spacing={1} alignItems="center">
                            <IconButton color="primary" onClick={onSave}>
                                <Save />
                            </IconButton>
                            <IconButton color="secondary" onClick={onCancel}>
                                <Cancel />
                            </IconButton>
                        </Stack>
                    ) : (
                        <Stack direction="row" spacing={1} alignItems="center">
                            <IconButton color="primary" onClick={() => onEdit(eq)}>
                                <Edit />
                            </IconButton>
                            <IconButton color="error" onClick={() => onDelete(eq._id, eq.equipment_name)}>
                                <Delete />
                            </IconButton>
                        </Stack>
                    )}
                </TableCell>
            )}
        </TableRow>
    );
};

function SecsGemEquipments(props: SecsGemEquipmentProps) {
    const { user } = props;
    const { equipment } = useApiContext();

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [sortBy, setSortBy] = useState('equipment_name');
    const [sortOrder, setSortOrder] = useState(1);

    const [isEditing, setIsEditing] = useState(false)
    const [editingEquipment, setEditingEquipment] = useState<Equipment | null>(null);

    const [isAddNew, setIsAddNew] = useState(false)

    // snackbar
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info' | 'warning'>('success');
    const [snackbarMessage, setSnackbarMessage] = useState('');

    // dialog delete
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [deleteEquipment, setDeleteEquipment] = useState<{ id: string, equipment_name: string }>({
        id: '',
        equipment_name: ''
    })
    const [deleteDialogMessage, setDeleteDialogMessage] = useState<string>('Are you sure you want to delete this item?')

    useEffect(() => {
        equipment.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [page, rowsPerPage, sortBy, sortOrder])

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

    const handleChangePage = (_: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(e.target.value, 10));
        setPage(0);
    };

    const handleError = (error: any, defaultMessage: string): string => {
        console.log(error); // Log the error for debugging

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

    const addNameRef = useRef<HTMLInputElement>(null);
    const addModelRef = useRef<HTMLInputElement>(null);
    const addIpRef = useRef<HTMLInputElement>(null);
    const addPortRef = useRef<HTMLInputElement>(null);
    const addIdRef = useRef<HTMLInputElement>(null);
    const addModeRef = useRef<HTMLInputElement>(null);
    const addEnableRef = useRef<HTMLInputElement>(null);

    const editNameRef = useRef<HTMLInputElement>(null);
    const editModelRef = useRef<HTMLInputElement>(null);
    const editIpRef = useRef<HTMLInputElement>(null);
    const editPortRef = useRef<HTMLInputElement>(null);
    const editIdRef = useRef<HTMLInputElement>(null);
    const editModeRef = useRef<HTMLInputElement>(null);
    const editEnableRef = useRef<HTMLInputElement>(null);

    const [editRefs, setEditRefs] = useState<{
        [key: string]: {
            name: React.RefObject<HTMLInputElement>;
            model: React.RefObject<HTMLInputElement>;
            ip: React.RefObject<HTMLInputElement>;
            port: React.RefObject<HTMLInputElement>;
            id: React.RefObject<HTMLInputElement>;
            mode: React.RefObject<HTMLInputElement>;
            enable: React.RefObject<HTMLInputElement>;
        };
    }>({});

    const handleEdit = (eq: Equipment) => {
        setEditingEquipment(eq);
        setIsEditing(true);

        // Create refs for the current row
        setEditRefs((prev) => ({
            ...prev,
            [eq._id]: {
                name: React.createRef(),
                model: React.createRef(),
                ip: React.createRef(),
                port: React.createRef(),
                id: React.createRef(),
                mode: React.createRef(),
                enable: React.createRef(),
            },
        }));
    };

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

    const handleSaveNewEquipment = async () => {
        const equipmentData = {
            _id: '', // Provide a default or generated ID
            equipment_name: addNameRef.current?.value || '',
            equipment_model: addModelRef.current?.value as 'FCL' | 'FCLX',
            address: addIpRef.current?.value || '',
            port: parseInt(addPortRef.current?.value || '0', 10),
            session_id: parseInt(addIdRef.current?.value || '0', 10),
            mode: addModeRef.current?.value as 'ACTIVE' | 'PASSIVE',
            enable: addEnableRef.current?.value === 'true',
        };

        await handleApiRequest(
            () => equipment.create(equipmentData),
            `${equipmentData.equipment_name} saved successfully`,
            'An error occurred while saving data'
        );
        setIsAddNew(false);

    };

    // handle delete
    const handleDeleteRequest = (id: string, equipment_name: string) => {
        setDeleteEquipment({ id, equipment_name });
        setDeleteDialogMessage(`Are you sure you want to delete ${equipment_name}?`);
        setDeleteDialogOpen(true);
    };

    const handleDelete = async () => {
        if (deleteEquipment.id) {
            try {
                const response = await equipment.delete(deleteEquipment.id);
                console.info("Response delete:", response);
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

    // const handleUpdateEquipment = async () => {
    //     const equipmentUpdateData = {
    //         _id: editingEquipment?._id || '', // Provide a default or generated ID
    //         equipment_name: editNameRef.current?.value || editingEquipment?.equipment_name,
    //         equipment_model: editModelRef.current?.value as 'FCL' | 'FCLX' || editingEquipment?.equipment_model,
    //         address: editIpRef.current?.value || editingEquipment?.address,
    //         port: parseInt(editPortRef.current?.value || editingEquipment?.port.toString() || '0', 10),
    //         session_id: parseInt(editIdRef.current?.value || editingEquipment?.session_id.toString() || '0', 10),
    //         mode: editModeRef.current?.value as 'ACTIVE' | 'PASSIVE' || editingEquipment?.mode,
    //         enable: editEnableRef.current?.value || editingEquipment?.enable,
    //     };

    //     await handleApiRequest(
    //         () => equipment.update(equipmentUpdateData._id, equipmentUpdateData),
    //         `${equipmentUpdateData.equipment_name} updated successfully`,
    //         'An error occurred while updated data'
    //     );
    //     setIsEditing(false);

    // };

    const handleUpdateEquipment = async () => {
        if (!editingEquipment) return;

        const equipmentUpdateData = {
            _id: editingEquipment._id,
            equipment_name: editRefs[editingEquipment._id].name.current?.value || editingEquipment.equipment_name,
            equipment_model: editRefs[editingEquipment._id].model.current?.value as 'FCL' | 'FCLX' || editingEquipment.equipment_model,
            address: editRefs[editingEquipment._id].ip.current?.value || editingEquipment.address,
            port: parseInt(editRefs[editingEquipment._id].port.current?.value || editingEquipment.port.toString()),
            session_id: parseInt(editRefs[editingEquipment._id].id.current?.value || editingEquipment.session_id.toString()),
            mode: editRefs[editingEquipment._id].mode.current?.value as 'ACTIVE' | 'PASSIVE' || editingEquipment.mode,
            enable: editRefs[editingEquipment._id].enable.current?.value === 'true' || editingEquipment.enable,
        };

        await handleApiRequest(
            () => equipment.update(equipmentUpdateData._id, equipmentUpdateData),
            `${equipmentUpdateData.equipment_name} updated successfully`,
            'An error occurred while updating data'
        );
        setIsEditing(false);
    };

    if (equipment.loading) {
        return (
            <Backdrop
                sx={(theme) => ({ color: '#fff', zIndex: theme.zIndex.drawer + 1 })}
                open={equipment.loading}
            //   onClick={handleClose}
            >
                <CircularProgress color="inherit" />
            </Backdrop>
        )

        //  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        //     <CircularProgress color="secondary" />
        // </Box>
    }

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
                                                    inputRef={addNameRef}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.5}>
                                                <TextField
                                                    size='small'
                                                    label='Model'
                                                    fullWidth
                                                    select
                                                    inputRef={addModelRef}
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
                                                    inputRef={addIpRef}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.2}>
                                                <TextField
                                                    size='small'
                                                    label='Port'
                                                    fullWidth
                                                    autoComplete='off'
                                                    type='number'
                                                    inputRef={addPortRef}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.1}>
                                                <TextField
                                                    size='small'
                                                    label='ID'
                                                    fullWidth
                                                    autoComplete='off'
                                                    type='number'
                                                    inputRef={addIdRef}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6} md={4} lg={1.4}>
                                                <TextField
                                                    size='small'
                                                    label='Mode'
                                                    fullWidth
                                                    select
                                                    inputRef={addModeRef}
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
                                                    inputRef={addEnableRef}
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

                            <EquipmentRow
                                user={user}
                                key={eq._id}
                                eq={eq}
                                isEditing={isEditing}
                                editingEquipment={editingEquipment}
                                editRefs={editRefs[eq._id]} // Pass the refs for this row
                                onEdit={handleEdit} // Use the new handleEdit function
                                onDelete={handleDeleteRequest}
                                onSave={handleUpdateEquipment}
                                onCancel={() => setIsEditing(false)}
                            />

                        ))}
                    </TableBody>
                </Table>

                <TablePagination
                    rowsPerPageOptions={[5, 10, 25]}
                    component="div"
                    count={equipment.totalCount}
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

SecsGemEquipments.propTypes = {
    user: PropTypes.shape({
        name: PropTypes.string.isRequired,
        email: PropTypes.string.isRequired,
        role: PropTypes.string.isRequired,
    }).isRequired,
}

export default SecsGemEquipments