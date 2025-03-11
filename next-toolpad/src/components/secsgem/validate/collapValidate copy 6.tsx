'use client'
import { Add, Cancel, Delete, Edit, ExpandLess, ExpandMore, Save } from '@mui/icons-material'
import { Box, Button, Checkbox, CircularProgress, Collapse, Divider, Fade, Grid, IconButton, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, TextField, Toolbar, Typography } from '@mui/material'
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
                                                                    <IconButton
                                                                        size="small"
                                                                        onClick={() => toggleExpand(configKey, 'package')} // เรียกใช้ toggleExpand สำหรับ package level
                                                                    >
                                                                        {isConfigExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                    </IconButton>
                                                                    {config.package8digit}
                                                                </TableCell>
                                                                <TableCell>{config.selection_code}</TableCell>
                                                            </TableRow>

                                                            {/* Level 2: Data with Selection Code */}
                                                            {/* <TableRow sx={{ '& td, & th': { border: 0 } }}> */}
                                                            <TableRow >
                                                                <TableCell colSpan={3} sx={{ p: 0, borderBottom: 0, pl: 2 }}>
                                                                    <Collapse in={isConfigExpanded}>
                                                                        {/* แสดงข้อมูลเพิ่มเติมใน Level 2 */}
                                                                        {/* <Box sx={{ width: '100%', overflowX: 'auto', backgroundColor: '-moz-initial' }}> */}
                                                                        <Box sx={{ width: '100%', overflowX: 'auto' }}>
                                                                            {config.data_with_selection_code.map((dataItem, dataItemIndex) => {
                                                                                const dataItemKey = `${data._id}-${config.package8digit}-${dataItem.package_selection_code}`; // ใช้ package_selection_code เป็น key
                                                                                const isDataItemExpanded = expanded.package_selection_code === dataItemKey; // ตรวจสอบว่า dataItem นี้ถูกขยายหรือไม่

                                                                                return (
                                                                                    <Table size='small' key={dataItemIndex} >
                                                                                        <TableBody>
                                                                                            <TableRow >
                                                                                                <TableCell >
                                                                                                    <Box sx={{ display: 'block' }}>
                                                                                                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                                                                            <IconButton
                                                                                                                size="small"
                                                                                                                onClick={() => toggleExpand(dataItemKey, 'package_selection_code')} // เรียกใช้ toggleExpand สำหรับ package level
                                                                                                            >
                                                                                                                {isDataItemExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                                                            </IconButton>
                                                                                                            <Typography variant='body2'>{dataItem.product_name}</Typography>
                                                                                                        </Box>
                                                                                                        <Collapse in={isDataItemExpanded} unmountOnExit>
                                                                                                            <Box pl={2} sx={{ mb: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', width: '100%', maxWidth: '100%', overflowX: 'auto', p: 2, backgroundColor: 'background.paper', borderRadius: 1 }}>
                                                                                                                {/* ส่วน Validate Type, Recipe Name, Operation Code, On Operation */}
                                                                                                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                                                                                                                    <TextField
                                                                                                                        label="Package Select Code"
                                                                                                                        value={dataItem.package_selection_code}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '250px' }}
                                                                                                                        disabled
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="Product Name"
                                                                                                                        value={dataItem.product_name}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '250px' }}
                                                                                                                        disabled
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="Validate Type"
                                                                                                                        value={dataItem.validate_type}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '150px' }}
                                                                                                                        disabled
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="Recipe Name"
                                                                                                                        value={dataItem.recipe_name}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '250px' }}
                                                                                                                        disabled
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="Operation Code"
                                                                                                                        value={dataItem.operation_code}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '150px' }}
                                                                                                                        disabled
                                                                                                                    />
                                                                                                                    <TextField
                                                                                                                        label="On Operation"
                                                                                                                        value={dataItem.on_operation}
                                                                                                                        size="small"
                                                                                                                        sx={{ width: '150px' }}
                                                                                                                        disabled
                                                                                                                    />
                                                                                                                </Box>

                                                                                                                {/* ส่วน Options */}
                                                                                                                <Box sx={{ pl: 2, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                                                                                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                                                                                        <Checkbox
                                                                                                                            checked={dataItem.options.use_operation_code}
                                                                                                                            size="small"
                                                                                                                            disabled
                                                                                                                        />
                                                                                                                        <Typography variant="body2" sx={{ fontSize: '0.75rem' }}>
                                                                                                                            Use Operation Code
                                                                                                                        </Typography>
                                                                                                                    </Box>
                                                                                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                                                                                        <Checkbox
                                                                                                                            checked={dataItem.options.use_on_operation}
                                                                                                                            size="small"
                                                                                                                            disabled
                                                                                                                        />
                                                                                                                        <Typography variant="body2" sx={{ fontSize: '0.75rem' }}>
                                                                                                                            Use On Operation
                                                                                                                        </Typography>
                                                                                                                    </Box>
                                                                                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                                                                                        <Checkbox
                                                                                                                            checked={dataItem.options.use_lot_hold}
                                                                                                                            size="small"
                                                                                                                            disabled
                                                                                                                        />
                                                                                                                        <Typography variant="body2" sx={{ fontSize: '0.75rem' }}>
                                                                                                                            Use Lot Hold
                                                                                                                        </Typography>
                                                                                                                    </Box>
                                                                                                                </Box>

                                                                                                                {/* ส่วน Allow Tool ID */}
                                                                                                                <Typography variant="body2" sx={{ fontWeight: 'bold', mt: 1, mb: 1, fontSize: '0.875rem' }}>
                                                                                                                    Allow Tool ID
                                                                                                                </Typography>
                                                                                                                <Grid container spacing={2} sx={{ pl: 2 }}>
                                                                                                                    {Object.entries(dataItem.allow_tool_id).map(([position, tools], index) => (
                                                                                                                        <Grid item xs={6} key={position}>
                                                                                                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                                                                                                <Typography variant="body2" sx={{ fontSize: '0.75rem', width: '100px' }}>
                                                                                                                                    {position.replace('_', ' ').toUpperCase()}:
                                                                                                                                </Typography>
                                                                                                                                <TextField
                                                                                                                                    value={tools.join(', ')}
                                                                                                                                    size="small"
                                                                                                                                    fullWidth
                                                                                                                                    disabled
                                                                                                                                />
                                                                                                                            </Box>
                                                                                                                        </Grid>
                                                                                                                    ))}
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