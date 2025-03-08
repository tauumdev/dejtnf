import React, { useState, useEffect } from 'react';
import {
    IconButton,
    Paper,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Typography,
    Box,
    Divider,
    Toolbar
} from '@mui/material';
import { Cancel, Save, Edit, Delete, Add } from '@mui/icons-material';
import { ValidateAllowToolId } from '../../../service/types';

interface AllowToolIdProps {
    initialData: ValidateAllowToolId;
    onSave: (data: ValidateAllowToolId) => void;
}

export const AllowToolId: React.FC<AllowToolIdProps> = ({ initialData, onSave }) => {
    const [allowIds, setAllowIds] = useState<ValidateAllowToolId>(initialData);
    const [editingKey, setEditingKey] = useState<string | null>(null);
    const [editedIds, setEditedIds] = useState<string>('');

    // Sync with parent data changes
    useEffect(() => {
        setAllowIds(initialData);
    }, [initialData]);

    // Edit operations
    const startEditing = (key: string, ids: string[]) => {
        setEditingKey(key);
        setEditedIds(ids.join(', '));
    };

    const saveEdits = () => {
        if (editingKey) {
            const updatedIds = editedIds.split(',').map(id => id.trim());
            const updatedData = {
                ...allowIds,
                [editingKey]: updatedIds
            };

            setAllowIds(updatedData);
            onSave(updatedData); // Call parent save handler
            cancelEditing();
        }
    };

    const cancelEditing = () => {
        setEditingKey(null);
        setEditedIds('');
    };

    // Delete operation
    const handleDelete = (key: string) => {
        const updated = { ...allowIds };
        delete updated[key];
        setAllowIds(updated);
        onSave(updated); // Call parent save handler
    };

    return (
        <TableContainer component={Paper}>
            {/* <Box sx={{p:2 ,display:'flex',alignContent:'revert'}}><Button variant="outlined" size='small'>Add New Position</Button></Box>
            <Divider/> */}
            <Toolbar sx={{ justifyContent: 'space-between', }}>
                <Typography variant="h6">Allow IDs Tool</Typography>

                <Button
                size='small'
                    variant="outlined"
                    startIcon={<Add />}
                    // onClick={() => setCreateDialogOpen(true)}
                    // onClick={() => setAddEquipment(true)}
                >
                    New IDs TOOL
                </Button>
            </Toolbar>
            <Divider/>
            
            <Table size='small'>                
                <TableHead>
                    <TableRow>
                        <TableCell><Typography fontWeight="bold">Position</Typography></TableCell>
                        <TableCell><Typography fontWeight="bold">Allowed IDs</Typography></TableCell>
                        <TableCell><Typography fontWeight="bold">Actions</Typography></TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {Object.entries(allowIds).map(([key, ids]) => (
                        <TableRow key={key}>
                            <TableCell>{`Position ${key.split('_')[1]}`}</TableCell>
                            <TableCell>
                                {editingKey === key ? (
                                    <TextField
                                        size='small'
                                        fullWidth
                                        value={editedIds}
                                        onChange={(e) => setEditedIds(e.target.value)}
                                        placeholder="Enter comma-separated IDs"
                                    />
                                ) : (
                                    ids.join(', ') || 'None'
                                )}
                            </TableCell>
                            <TableCell align="right">
                                {editingKey === key ? (
                                    <Stack direction="row" spacing={1}>
                                        <IconButton color="primary" onClick={saveEdits}>
                                            <Save />
                                        </IconButton>
                                        <IconButton color="secondary" onClick={cancelEditing}>
                                            <Cancel />
                                        </IconButton>
                                    </Stack>
                                ) : (
                                    <Stack direction="row" spacing={1}>
                                        <IconButton
                                            color="primary"
                                            onClick={() => startEditing(key, ids)}
                                        >
                                            <Edit />
                                        </IconButton>
                                        <IconButton
                                            color="error"
                                            onClick={() => handleDelete(key)}
                                        >
                                            <Delete />
                                        </IconButton>
                                    </Stack>
                                )}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};


// // // Parent component usage example
// const ParentComponent = () => {
//     const [toolIds, setToolIds] = useState<ValidateAllowToolId>(initialData);

//     const handleSave = (updatedData: ValidateAllowToolId) => {
//         // Here you would typically make API calls
//         console.log('Saving data:', updatedData);
//         setToolIds(updatedData);
        
//         // Example API call:
//         // api.saveToolIds(updatedData)
//         //   .then(() => showSuccessMessage())
//         //   .catch(error => showErrorMessage(error))
//     };

//     return (
//         <AllowToolId 
//             initialData={toolIds}
//             onSave={handleSave}
//         />
//     );
// };