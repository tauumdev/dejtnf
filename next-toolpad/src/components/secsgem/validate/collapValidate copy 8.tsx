'use client'
import { Add, Cancel, Delete, Edit, ExpandLess, ExpandMore, Save } from '@mui/icons-material'
import { Box, Button, Checkbox, CircularProgress, Collapse, Divider, Fade, FormControlLabel, Grid, Icon, IconButton, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, TextField, Toolbar, Typography } from '@mui/material'
import React, { useEffect, useRef, useState } from 'react'
import { useApiContext } from '@/src/context/apiContext';

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
        console.log("start edit original data: ", dataByEquipmentName);
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

        console.log("original data: ", dataByEquipmentName);

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

        console.log("new data: ", dataByEquipmentName);

        try {
            await validate.update(_id, dataByEquipmentName);
            setEditingKey(null);
        } catch (error) {
            console.error("Failed to save edits:", error);
        }
    };

    const handleDelete = async (key: string) => {
        const [_id, package8digit, package_selection_code] = key.split('-')
        // try {
        //     await validate.delete(_id); // เรียก API เพื่อลบข้อมูล
        //     // await validate.gets(); // Refetch ข้อมูลหลังจากลบ
        //     await validate.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder);
        // } catch (error) {
        //     console.error("Failed to delete:", error);
        // }
    };

    const cancelEditing = () => {
        setEditingKey(null); // ปิดโหมดแก้ไข
    };

    const inputRef = useRef<HTMLInputElement | null>(null);

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
                                                        <Typography variant="body1">Package Code</Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body1">Selection Code</Typography>
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        <Button startIcon={<Add />}>package</Button>
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
                                                                                                        {/* <Box sx={{ display: 'flex', alignItems: 'center' }}> */}
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
                                                                                                                        <IconButton color="error" onClick={() => handleDelete(key)}>
                                                                                                                            <Delete />
                                                                                                                        </IconButton>
                                                                                                                    </Stack>
                                                                                                                </Box>
                                                                                                                <Grid container spacing={2}>

                                                                                                                    {/* แถวที่ 1 */}
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <TextField
                                                                                                                            inputRef={inputRef}
                                                                                                                            label="Product Name"
                                                                                                                            value={isEditing ? editedData.product_name : dataItem.product_name}
                                                                                                                            onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                                                                                                            size="small"
                                                                                                                            fullWidth
                                                                                                                            disabled={!isEditing}
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <TextField
                                                                                                                            inputRef={inputRef}
                                                                                                                            label="Package Select Code"
                                                                                                                            value={isEditing ? editedData.package_selection_code : dataItem.package_selection_code}
                                                                                                                            onChange={(e) => setEditedData({ ...editedData, package_selection_code: e.target.value })}
                                                                                                                            size="small"
                                                                                                                            fullWidth
                                                                                                                            disabled={!isEditing}
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <TextField
                                                                                                                            inputRef={inputRef}
                                                                                                                            label="Type Validate"
                                                                                                                            value={isEditing ? editedData.validate_type : dataItem.validate_type}
                                                                                                                            onChange={(e) => setEditedData({ ...editedData, validate_type: e.target.value })}
                                                                                                                            size="small"
                                                                                                                            fullWidth
                                                                                                                            disabled={!isEditing}
                                                                                                                        />
                                                                                                                    </Grid>

                                                                                                                    {/* แถวที่ 2 */}
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <TextField
                                                                                                                            inputRef={inputRef}
                                                                                                                            label="Recipe Name"
                                                                                                                            value={isEditing ? editedData.recipe_name : dataItem.recipe_name}
                                                                                                                            onChange={(e) => setEditedData({ ...editedData, recipe_name: e.target.value })}
                                                                                                                            size="small"
                                                                                                                            fullWidth
                                                                                                                            disabled={!isEditing}
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <TextField
                                                                                                                            inputRef={inputRef}
                                                                                                                            label="Operation Code"
                                                                                                                            value={isEditing ? editedData.operation_code : dataItem.operation_code}
                                                                                                                            onChange={(e) => setEditedData({ ...editedData, operation_code: e.target.value })}
                                                                                                                            size="small"
                                                                                                                            fullWidth
                                                                                                                            disabled={!isEditing}
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <TextField
                                                                                                                            inputRef={inputRef}
                                                                                                                            label="On Operation"
                                                                                                                            value={isEditing ? editedData.on_operation : dataItem.on_operation}
                                                                                                                            onChange={(e) => setEditedData({ ...editedData, on_operation: e.target.value })}
                                                                                                                            size="small"
                                                                                                                            fullWidth
                                                                                                                            disabled={!isEditing}
                                                                                                                        />
                                                                                                                    </Grid>

                                                                                                                    {/* แถวที่ 3 - Checkboxes */}
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <FormControlLabel
                                                                                                                            control={
                                                                                                                                <Checkbox
                                                                                                                                    checked={isEditing ? editedData.options.use_operation_code : dataItem.options.use_operation_code}
                                                                                                                                    onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_operation_code: e.target.checked } })}
                                                                                                                                    size="small"
                                                                                                                                    disabled={!isEditing}
                                                                                                                                />
                                                                                                                            }
                                                                                                                            label={<Typography variant='body2'>Check Operation Code</Typography>}
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <FormControlLabel
                                                                                                                            control={
                                                                                                                                <Checkbox
                                                                                                                                    checked={isEditing ? editedData.options.use_on_operation : dataItem.options.use_on_operation}
                                                                                                                                    onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_on_operation: e.target.checked } })}
                                                                                                                                    size="small"
                                                                                                                                    disabled={!isEditing}
                                                                                                                                />
                                                                                                                            }
                                                                                                                            label={<Typography variant='body2'>Check On Operation</Typography>}
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                    <Grid item xs={12} sm={4}>
                                                                                                                        <FormControlLabel
                                                                                                                            control={
                                                                                                                                <Checkbox
                                                                                                                                    checked={isEditing ? editedData.options.use_lot_hold : dataItem.options.use_lot_hold}
                                                                                                                                    onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_lot_hold: e.target.checked } })}
                                                                                                                                    size="small"
                                                                                                                                    disabled={!isEditing}
                                                                                                                                />
                                                                                                                            }
                                                                                                                            label={<Typography variant='body2'>Check Lot Hold</Typography>}
                                                                                                                        />
                                                                                                                    </Grid>

                                                                                                                    {/* แถวที่ 4 - Allow Tool ID */}
                                                                                                                    <Grid item xs={12}>
                                                                                                                        <Typography variant="body2" sx={{ pb: 2 }}>
                                                                                                                            Allow Tool ID
                                                                                                                        </Typography>
                                                                                                                        <Grid container spacing={2}>
                                                                                                                            {Object.entries(dataItem.allow_tool_id).map(([position, tools], index) => (
                                                                                                                                <Grid item xs={12} sm={6} key={position}>
                                                                                                                                    <TextField
                                                                                                                                        inputRef={inputRef}
                                                                                                                                        label={position.replace('_', ' ').toUpperCase()}
                                                                                                                                        value={isEditing ? editedData.allow_tool_id[position].join(', ') : tools.join(', ')}
                                                                                                                                        onChange={(e) => setEditedData({
                                                                                                                                            ...editedData,
                                                                                                                                            allow_tool_id: {
                                                                                                                                                ...editedData.allow_tool_id,
                                                                                                                                                [position]: e.target.value.split(',').map(tool => tool.trim()).filter(tool => tool !== '').map(tool => tool.replace(/\s*,\s*/g, ','))
                                                                                                                                            }
                                                                                                                                        })}
                                                                                                                                        size="small"
                                                                                                                                        fullWidth

                                                                                                                                        disabled={!isEditing}
                                                                                                                                    />
                                                                                                                                </Grid>
                                                                                                                            ))}
                                                                                                                        </Grid>

                                                                                                                    </Grid>

                                                                                                                </Grid>
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
        </Box>
    );
}
