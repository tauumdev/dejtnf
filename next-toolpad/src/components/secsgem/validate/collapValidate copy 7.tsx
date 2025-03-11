'use client'
import { Add, Cancel, Delete, Edit, ExpandLess, ExpandMore, Save } from '@mui/icons-material'
import { Box, Button, Checkbox, CircularProgress, Collapse, Divider, Fade, FormControlLabel, Grid, Icon, IconButton, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, TextField, Toolbar, Typography } from '@mui/material'
import React, { useEffect, useState } from 'react'
import { useApiContext } from '@/src/context/apiContext';

export default function CollapValidate() {
    const { validate } = useApiContext();
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [sortBy, setSortBy] = useState('equipment_name');
    const [sortOrder, setSortOrder] = useState(1);

    const [editingKey, setEditingKey] = useState<string | null>(null); // เก็บ key ของรายการที่กำลังแก้ไข
    const [editedData, setEditedData] = useState<any>({}); // เก็บข้อมูลที่แก้ไข


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
        setExpanded((prev) => ({
            ...prev,
            [level]: prev[level] === key ? null : key, // ถ้า key เดิมถูกขยายอยู่ ให้ยุบ, ถ้ายังไม่ขยายให้ขยาย
        }));
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
                                                    const configKey = `${data._id}-${config.package8digit}`; // สร้าง key สำหรับ config level
                                                    const isConfigExpanded = expanded.package === configKey; // ตรวจสอบว่า config นี้ถูกขยายหรือไม่

                                                    return (
                                                        <React.Fragment key={configIndex}>
                                                            {/* Level 1: Config */}
                                                            <TableRow>
                                                                <TableCell>
                                                                    <FormControlLabel control={
                                                                        <IconButton
                                                                            size="small"
                                                                            onClick={() => toggleExpand(configKey, 'package')} // เรียกใช้ toggleExpand สำหรับ package level
                                                                        >
                                                                            {isConfigExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                        </IconButton>
                                                                    }
                                                                        label={<Typography variant='body2'>{config.package8digit}</Typography>}
                                                                    />

                                                                </TableCell>
                                                                <TableCell>{config.selection_code}</TableCell>
                                                            </TableRow>

                                                            {/* Level 2: Data with Selection Code */}
                                                            <TableRow >
                                                                <TableCell colSpan={3} sx={{ p: 0, borderBottom: 0, pl: 2 }}>
                                                                    <Collapse in={isConfigExpanded}>
                                                                        {/* แสดงข้อมูลเพิ่มเติมใน Level 2 */}
                                                                        {/* <Box sx={{ width: '100%', overflowX: 'auto', backgroundColor: '-moz-initial' }}> */}
                                                                        <Box sx={{ width: '100%', overflowX: 'auto' }}>
                                                                            {config.data_with_selection_code.map((dataItem, dataItemIndex) => {
                                                                                const dataItemKey = `${data._id}-${config.package8digit}-${dataItem.package_selection_code}`; // ใช้ package_selection_code เป็น key
                                                                                const isDataItemExpanded = expanded.package_selection_code === dataItemKey; // ตรวจสอบว่า dataItem นี้ถูกขยายหรือไม่

                                                                                return ( //data validate
                                                                                    <Table size='small' key={dataItemIndex} >
                                                                                        <TableBody>
                                                                                            <TableRow >
                                                                                                <TableCell >
                                                                                                    <Box sx={{ display: 'block' }}>
                                                                                                        <FormControlLabel control={
                                                                                                            <IconButton
                                                                                                                size="small"
                                                                                                                onClick={() => toggleExpand(dataItemKey, 'package_selection_code')} // เรียกใช้ toggleExpand สำหรับ package level
                                                                                                            >
                                                                                                                {isDataItemExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                                                            </IconButton>
                                                                                                        }
                                                                                                            label={<Typography variant='body2'>{config.package8digit}</Typography>}
                                                                                                        />

                                                                                                        {/* level 3 data validate */}
                                                                                                        <Collapse in={isDataItemExpanded} unmountOnExit sx={{ pt: 1 }}>
                                                                                                            <Box sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 2 }}>
                                                                                                                <Box sx={{ display: 'flex', alignContent: 'flex-start', overflow: 'auto', p: 1, gap: 1 }}>
                                                                                                                    <TextField
                                                                                                                        label="Product Name"
                                                                                                                        value={dataItem.product_name}
                                                                                                                        onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '250px' }}
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="Package Select Code"
                                                                                                                        value={dataItem.package_selection_code}
                                                                                                                        onChange={(e) => setEditedData({ ...editedData, package_selection_code: e.target.value })}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '200px' }}
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="Type Validate"
                                                                                                                        value={dataItem.validate_type}
                                                                                                                        onChange={(e) => setEditedData({ ...editedData, validate_type: e.target.value })}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '200px' }}
                                                                                                                    />
                                                                                                                </Box>
                                                                                                                <Box sx={{ display: 'flex', alignContent: 'flex-start', overflow: 'auto', p: 1, gap: 1 }}>

                                                                                                                    <TextField
                                                                                                                        label="Recipe Name"
                                                                                                                        value={dataItem.recipe_name}
                                                                                                                        onChange={(e) => setEditedData({ ...editedData, recipe_name: e.target.value })}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '250px' }}
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="Operation Code"
                                                                                                                        value={dataItem.operation_code}
                                                                                                                        onChange={(e) => setEditedData({ ...editedData, operation_code: e.target.value })}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '200px' }}
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="On Operation"
                                                                                                                        value={dataItem.on_operation}
                                                                                                                        onChange={(e) => setEditedData({ ...editedData, on_operation: e.target.value })}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '200px' }}
                                                                                                                    />
                                                                                                                </Box>
                                                                                                                <Box sx={{ display: 'flex', alignContent: 'flex-start', overflow: 'auto', p: 1, gap: 1 }}>
                                                                                                                    <FormControlLabel control={
                                                                                                                        <Checkbox
                                                                                                                            defaultChecked size='small' value={dataItem.options.use_operation_code}
                                                                                                                        />
                                                                                                                    }
                                                                                                                        label={<Typography variant='body2'>Check Operation Code</Typography>}
                                                                                                                    />
                                                                                                                    <FormControlLabel control={
                                                                                                                        <Checkbox defaultChecked size='small' value={dataItem.options.use_on_operation} />
                                                                                                                    }
                                                                                                                        label={<Typography variant='body2'>Check On Operation</Typography>}
                                                                                                                    />
                                                                                                                    <FormControlLabel control={
                                                                                                                        <Checkbox defaultChecked size='small' value={dataItem.options.use_lot_hold} />
                                                                                                                    }
                                                                                                                        label={<Typography variant='body2'>Check Lot Hold</Typography>}
                                                                                                                    />
                                                                                                                </Box>
                                                                                                                <Box sx={{ display: 'block', alignContent: 'flex-start', overflow: 'auto', p: 1, gap: 1 }}>

                                                                                                                    {/* ส่วน Allow Tool ID */}
                                                                                                                    <Typography variant="body2" sx={{ pb: 2 }}>
                                                                                                                        Allow Tool ID
                                                                                                                    </Typography>
                                                                                                                    <Grid container spacing={2} >
                                                                                                                        {Object.entries(dataItem.allow_tool_id).map(([position, tools], index) => (
                                                                                                                            <Grid item xs={6} key={position}>
                                                                                                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                                                                                                    <TextField
                                                                                                                                        label={position.replace('_', ' ').toUpperCase()}
                                                                                                                                        value={tools.join(', ')}
                                                                                                                                        size="small"
                                                                                                                                        fullWidth
                                                                                                                                    />
                                                                                                                                </Box>
                                                                                                                            </Grid>
                                                                                                                        ))}
                                                                                                                    </Grid>
                                                                                                                </Box>
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