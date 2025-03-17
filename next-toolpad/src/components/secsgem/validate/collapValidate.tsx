'use client'
import { Add, Cancel, Delete, Edit, ExpandLess, ExpandMore, Save } from '@mui/icons-material'
import { Box, Button, Checkbox, CircularProgress, Collapse, Divider, Fade, FormControlLabel, Grid, Icon, IconButton, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, TextField, Toolbar, Typography } from '@mui/material'
import React, { useEffect, useRef, useState } from 'react'
import { useApiContext } from '@/src/context/apiContext';
import DataValidationForm from './CollapsibleDataItem';
import { DeleteDialog } from './deleteDialog';
import { DialogAddValidateDataForm } from './addValidateDataForm';

export default function CollapValidate() {
    const { validate } = useApiContext();
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [sortBy, setSortBy] = useState('equipment_name');
    const [sortOrder, setSortOrder] = useState(1);


    useEffect(() => {
        validate.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder);
    }, [page, rowsPerPage, sortBy, sortOrder]);

    const handleChangePage = (_: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(e.target.value, 10));
        setPage(0);
    };

    const [expanded, setExpanded] = useState<{
        id: string | null;
        package: string | null;
        package_selection_code: string | null;
    }>({ id: null, package: null, package_selection_code: null });

    const toggleExpand = (key: string, level: 'id' | 'package' | 'package_selection_code') => {
        console.log(key);

        setExpanded((prev) => ({
            ...prev,
            [level]: prev[level] === key ? null : key, // ถ้า key เดิมถูกขยายอยู่ ให้ยุบ, ถ้ายังไม่ขยายให้ขยาย
        }));
    };


    // const [editId, setEditId] = useState('');
    const [editingKey, setEditingKey] = useState<string | null>(null); // เก็บ key ของรายการที่กำลังแก้ไข
    const [editedData, setEditedData] = useState<any>({}); // เก็บข้อมูลที่แก้ไข

    const startEditing = (key: string, data: any) => {

        setEditingKey(key);
        setEditedData(data);

        const [_id, package8digit, package_selection_code] = key.split('-')
        const dataByEquipmentName = validate.list.filter(item => item._id === _id);
        // console.log("start edit original data: ", dataByEquipmentName);
    };

    const saveEdits = async () => {
        if (!editingKey || !editedData) return;
        const [_id, package8digit, package_selection_code] = editingKey.split('-');

        // ใช้ find แทน filter
        const dataByEquipmentName = validate.list.find(item => item._id === _id);

        if (!dataByEquipmentName) {
            console.error("Data not found for _id:", _id);
            return;
        }

        // console.log("original data: ", dataByEquipmentName);

        dataByEquipmentName.config.forEach(item => {
            if (item.package8digit === package8digit) {
                item.data_with_selection_code = item.data_with_selection_code.map(value => {
                    if (value.package_selection_code === package_selection_code) {
                        return { ...value, ...editedData }; // อัปเดตค่าที่แก้ไข
                    }
                    return value;
                });
            }
        });

        console.log("new edit data: ", dataByEquipmentName);

        try {
            const responseEdit = await validate.update(_id, dataByEquipmentName);
            setEditingKey(null);
            console.log('Edits saved successfully!', responseEdit);

        } catch (error) {
            console.error("Failed to save edits:", error);
        }
    };

    const handleDeleteConfig = async (_id: string, package8digit: string) => {
        const dataByEquipmentName = validate.list.find(item => item._id === _id);

        if (!dataByEquipmentName) {
            console.error("Data not found for _id:", _id);
            return;
        }

        // Remove the config with the matching package8digit
        dataByEquipmentName.config = dataByEquipmentName.config.filter(
            (config) => config.package8digit !== package8digit
        );

        // If no configs remain, delete the entire equipment
        if (dataByEquipmentName.config.length === 0) {
            await validate.delete(_id);
        } else {
            await validate.update(_id, dataByEquipmentName);
        }

        // Refetch data
        await validate.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder);
    };

    const handleDeleteDataItem = async (_id: string, package8digit: string, package_selection_code: string) => {
        const dataByEquipmentName = validate.list.find(item => item._id === _id);

        if (!dataByEquipmentName) {
            console.error("Data not found for _id:", _id);
            return;
        }

        // Find the config with the matching package8digit
        const configIndex = dataByEquipmentName.config.findIndex(
            (config) => config.package8digit === package8digit
        );

        if (configIndex === -1) {
            console.error("Config not found for package8digit:", package8digit);
            return;
        }

        // Remove the data_with_selection_code with the matching package_selection_code
        dataByEquipmentName.config[configIndex].data_with_selection_code =
            dataByEquipmentName.config[configIndex].data_with_selection_code.filter(
                (data) => data.package_selection_code !== package_selection_code
            );

        // If no data_with_selection_code remains, remove the config
        if (dataByEquipmentName.config[configIndex].data_with_selection_code.length === 0) {
            dataByEquipmentName.config.splice(configIndex, 1);
        }

        // If no configs remain, delete the entire equipment
        if (dataByEquipmentName.config.length === 0) {
            await validate.delete(_id);
        } else {
            await validate.update(_id, dataByEquipmentName);
        }

        // Refetch data
        await validate.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder);
    };

    const handleDelete = async (key: string) => {
        const [_id, package8digit, package_selection_code] = key.split('-');

        if (package_selection_code) {
            await handleDeleteDataItem(_id, package8digit, package_selection_code);
        } else {
            await handleDeleteConfig(_id, package8digit);
        }
    };
    const cancelEditing = () => {
        setEditingKey(null); // ปิดโหมดแก้ไข
    };

    // delete dialog
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedKey, setSelectedKey] = useState<string | null>(null);
    const [deleteLevel, setDeleteLevel] = useState<string | null>(null);

    const handleOpenDialog = (key: string, level: string) => {
        setSelectedKey(key);
        setDeleteLevel(level);
        setOpenDialog(true);
    };

    const handleConfirmDelete = () => {
        if (selectedKey) {
            handleDelete(selectedKey); // เรียกใช้ฟังก์ชันลบ
        }
        setOpenDialog(false); // ปิด Dialog
        setSelectedKey(null);
    };

    // add equipment
    const [openAddEquipment, setOpenAddEquipment] = useState(false)

    const openDialogAddEquipment = () => {
        setOpenAddEquipment(true)
        console.log('Open add dialog');
    };

    const cancelDialogAddEquipment = () => {
        setOpenAddEquipment(false)
    };

    const saveDialogAddEquipment = (data) => {
        setOpenAddEquipment(false)
        console.log("data save: ", data);
    };

    return (
        <Box sx={{ width: '100%' }}>
            <TableContainer component={Paper}>
                <Toolbar sx={{ justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="h6">Lot Validate Config</Typography>
                    {validate.loading &&
                        <Fade in={validate.loading} unmountOnExit>
                            <CircularProgress color="secondary" />
                        </Fade>
                    }
                    <Button
                        variant="outlined"
                        startIcon={<Add />}
                        sx={{ width: 150 }}
                        // onClick={openDialogAddEquipment}
                        onClick={openDialogAddEquipment}
                    >
                        equipment
                    </Button>
                </Toolbar>

                <Table size='small'>
                    <TableHead>
                        <TableRow>
                            <TableCell width={120} >
                                <Typography fontWeight="bold">Equipment</Typography>
                            </TableCell>
                            <TableCell align='center' >
                                <Typography fontWeight="bold">Data Config</Typography>
                            </TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {validate.list.map((data, dataIndex) => (
                            <TableRow key={data._id}>
                                <TableCell component="th" scope="row">
                                    <Typography fontWeight="bold">{data.equipment_name}</Typography>
                                </TableCell>
                                <TableCell>
                                    <Box>
                                        <Table size="small">

                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>
                                                        <Typography variant="body1">First Package Code 8 Digit</Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body1">Selection Code</Typography>
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        <Button startIcon={<Add />}>PACKAGE</Button>
                                                    </TableCell>
                                                </TableRow>
                                            </TableHead>

                                            <TableBody>
                                                {data.config.map((config, configIndex) => {
                                                    const configKey = `${data._id}-${config.package8digit}`;
                                                    const isConfigExpanded = expanded.package === configKey;
                                                    return (
                                                        <React.Fragment key={configIndex}>

                                                            {/* Level 1: Config */}
                                                            <TableRow>
                                                                <TableCell sx={{ width: 300 }}>
                                                                    <Button size='small' variant="text"
                                                                        color='inherit'

                                                                        startIcon={isConfigExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                        onClick={() => toggleExpand(configKey, 'package')}
                                                                        disableTouchRipple
                                                                        disableFocusRipple
                                                                        disableRipple
                                                                        sx={{ backgroundColor: 'inherit' }}
                                                                    >{config.package8digit}</Button>
                                                                </TableCell>
                                                                <TableCell>{config.selection_code}</TableCell>

                                                                <TableCell>
                                                                    <IconButton
                                                                        color="error"
                                                                        onClick={() => handleOpenDialog(configKey, `all base package code: ${config.package8digit}`)}
                                                                    >
                                                                        <Delete />
                                                                    </IconButton>
                                                                </TableCell>
                                                            </TableRow>

                                                            {/* Level 2: Data with Selection Code */}
                                                            <TableRow >
                                                                <TableCell colSpan={3} sx={{ p: 0, borderBottom: 0, pl: 2 }}>
                                                                    <Collapse in={isConfigExpanded}>

                                                                        <Box sx={{ width: '100%', overflowX: 'auto' }}>
                                                                            {config.data_with_selection_code.map((dataItem, dataItemIndex) => {
                                                                                const dataItemKey = `${data._id}-${config.package8digit}-${dataItem.package_selection_code}`; // ใช้ package_selection_code เป็น key
                                                                                const isDataItemExpanded = expanded.package_selection_code === dataItemKey; // ตรวจสอบว่า dataItem นี้ถูกขยายหรือไม่

                                                                                const key = `${data._id}-${config.package8digit}-${dataItem.package_selection_code}`;
                                                                                const isEditing = editingKey === key;

                                                                                return (
                                                                                    <Table size='small' key={dataItemIndex} >
                                                                                        <TableBody>
                                                                                            <TableRow >
                                                                                                <TableCell >
                                                                                                    <Box sx={{ display: 'block', overflow: 'auto' }}>

                                                                                                        <Button size='small' variant="text"
                                                                                                            color='inherit'
                                                                                                            startIcon={isDataItemExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                                                            onClick={() => toggleExpand(dataItemKey, 'package_selection_code')}
                                                                                                            disableTouchRipple
                                                                                                            disableFocusRipple
                                                                                                            disableRipple
                                                                                                            sx={{ backgroundColor: 'inherit' }}
                                                                                                        >
                                                                                                            {dataItem.product_name}
                                                                                                        </Button>

                                                                                                        {/* level 3 data validate */}
                                                                                                        <Collapse in={isDataItemExpanded} unmountOnExit sx={{ pt: 1 }}>
                                                                                                            <Box sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 2, pt: 1 }}>
                                                                                                                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                                                                                                                    <Stack direction="row" spacing={1} sx={{ marginLeft: 'auto' }} >
                                                                                                                        {isEditing ? (
                                                                                                                            <>
                                                                                                                                <IconButton color="primary" onClick={saveEdits}>
                                                                                                                                    <Save />
                                                                                                                                </IconButton>
                                                                                                                                <IconButton color="secondary" onClick={cancelEditing}>
                                                                                                                                    <Cancel />
                                                                                                                                </IconButton>
                                                                                                                            </>
                                                                                                                        ) : (
                                                                                                                            <IconButton color="primary" onClick={() => startEditing(key, dataItem)}>
                                                                                                                                <Edit />
                                                                                                                            </IconButton>
                                                                                                                        )}
                                                                                                                        <IconButton
                                                                                                                            color="error"
                                                                                                                            onClick={() => handleOpenDialog(key, `validate data: ${dataItem.package_selection_code}`)}
                                                                                                                        >
                                                                                                                            <Delete />
                                                                                                                        </IconButton>
                                                                                                                    </Stack>
                                                                                                                </Box>

                                                                                                                {/* From data validate */}
                                                                                                                <DataValidationForm
                                                                                                                    dataItem={dataItem}
                                                                                                                    editedData={editedData}
                                                                                                                    setEditedData={setEditedData}
                                                                                                                    isEditing={isEditing}
                                                                                                                />

                                                                                                            </Box>

                                                                                                        </Collapse>
                                                                                                    </Box>
                                                                                                </TableCell>

                                                                                            </TableRow>
                                                                                        </TableBody>
                                                                                    </Table>
                                                                                );
                                                                            })}
                                                                        </Box>
                                                                    </Collapse>
                                                                </TableCell>
                                                            </TableRow>
                                                        </React.Fragment>
                                                    );
                                                })}
                                            </TableBody>
                                        </Table>
                                    </Box>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>

                <TablePagination
                    rowsPerPageOptions={[5, 10, 25]}
                    component="div"
                    count={validate.totalCount}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </TableContainer>

            <DeleteDialog
                level={deleteLevel || ""}
                open={openDialog}
                onClose={() => setOpenDialog(false)}
                onConfirm={handleConfirmDelete}
            />

            <DialogAddValidateDataForm
                open={openAddEquipment}
                handleClose={cancelDialogAddEquipment}
                onSave={saveDialogAddEquipment}
            />
        </Box>
    );
}
