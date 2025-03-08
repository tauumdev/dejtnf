'use client'
import { Add, Cancel, ExpandLess, ExpandMore, Save } from '@mui/icons-material'
import { Box, Button, CircularProgress, Collapse, Fade, IconButton, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, Toolbar, Typography } from '@mui/material'
import React, { useEffect, useState } from 'react'
import { useApiContext } from '@/src/context/apiContext';

export default function CollapValidate() {
    const { validate } = useApiContext();
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [sortBy, setSortBy] = useState('equipment_name');
    const [sortOrder, setSortOrder] = useState(1);

    const [expanded, setExpanded] = useState<string | null>(null); // ใช้ state สำหรับเก็บค่าเฉพาะของแถวที่ถูกเปิด

    useEffect(() => {
        validate.gets(
            undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder
        )

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [page, rowsPerPage, sortBy, sortOrder])

    const handleChangePage = (_: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(e.target.value, 10));
        setPage(0);
    };

    const toggleExpand = (dataIndex: number, configIndex: number) => {
        const key = `${dataIndex}-${configIndex}`; // สร้างค่าเฉพาะจาก dataIndex และ configIndex
        setExpanded(prev => (prev === key ? null : key)); // เปิด/ปิดเฉพาะแถวที่คลิก
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
                            <TableRow
                                key={data.equipment_name}
                            >
                                <TableCell component="th" scope="row">
                                    {data.equipment_name}
                                </TableCell >
                                <TableCell>
                                    <Box>
                                        <Table size='small'>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>Package Code</TableCell>
                                                    <TableCell>Selection Code</TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {data.config.map((config, configIndex) => (
                                                    <React.Fragment key={configIndex}>
                                                        <TableRow sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                                            <TableCell>
                                                                <IconButton
                                                                    size="small"
                                                                    onClick={() => toggleExpand(dataIndex, configIndex)}
                                                                >
                                                                    {expanded === `${dataIndex}-${configIndex}` ? <ExpandLess /> : <ExpandMore />}
                                                                </IconButton>
                                                                {config.package8digit}
                                                            </TableCell>
                                                            <TableCell>{config.selection_code}</TableCell>
                                                        </TableRow>

                                                        <TableRow sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                                            <TableCell colSpan={2}>
                                                                <Collapse in={expanded === `${dataIndex}-${configIndex}`}>
                                                                    <Box sx={{ width: '100%', overflow: 'auto' }}>
                                                                        {config.data_with_selection_code.map((dataItem, dataItemIndex) => (
                                                                            <React.Fragment key={dataItemIndex}>
                                                                                <Box key={dataItem.package_selection_code} pl={2} sx={{ mb: 1, direction: 'row', display: 'flex', alignItems: 'center', whiteSpace: 10 }} >
                                                                                    {/* <Typography variant="body2">
                                                                                    {JSON.stringify(dataItem, null, 2)}
                                                                                </Typography> */}
                                                                                    <IconButton
                                                                                        size="small"
                                                                                    // onClick={() => toggleExpand(dataIndex, configIndex)} 
                                                                                    >
                                                                                        {expanded === `${dataIndex}-${configIndex}` ? <ExpandLess /> : <ExpandMore />}
                                                                                    </IconButton>
                                                                                    <Typography variant="body2">{dataItem.product_name}</Typography>


                                                                                </Box>
                                                                                <Box>
                                                                                    <Collapse in={true}>
                                                                                        {JSON.stringify(dataItem, null, 2)}
                                                                                    </Collapse>
                                                                                </Box>
                                                                            </React.Fragment>

                                                                        ))}
                                                                    </Box>
                                                                </Collapse>
                                                            </TableCell>
                                                        </TableRow>
                                                    </React.Fragment>
                                                ))}
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
                    count={validate.totalCount} // Use the totalCount from context
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </TableContainer>
            <pre>{JSON.stringify(validate.list[0], null, 2)}</pre>
        </Box>
    )
}