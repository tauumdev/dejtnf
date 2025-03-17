'use client'
import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Checkbox, Collapse, FormControlLabel, Grid2, IconButton, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, TextField, Typography } from '@mui/material';
import { Add, Delete, Edit, ExpandLess, ExpandMore } from '@mui/icons-material';
import { useApiContext } from '@/src/context/apiContext';

interface User {
    name: string;
    email: string;
    role: string;
}

function ValidateConfig(props: { user: User }) {
    const { user } = props
    const { validate } = useApiContext();

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [sortBy, setSortBy] = useState('equipment_name');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

    const [expanded, setExpanded] = useState<{
        id: string | null;
        package: string | null;
        package_selection_code: string | null;
    }>({ id: null, package: null, package_selection_code: null });

    const toggleExpand = (key: string, level: 'id' | 'package' | 'package_selection_code') => {
        // console.log(key);
        setExpanded((prev) => ({
            ...prev,
            [level]: prev[level] === key ? null : key, // ถ้า key เดิมถูกขยายอยู่ ให้ยุบ, ถ้ายังไม่ขยายให้ขยาย
        }));
    };

    // Fetch equipment data on component mount or when pagination/sorting changes
    useEffect(() => {
        validate.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder === 'asc' ? 1 : -1)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [page, rowsPerPage, sortBy, sortOrder])

    // Function to refresh data
    const refreshData = () => {
        validate.gets(
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

    // Handle edit
    const [isEditing, setIsEditing] = useState(false)
    const handleEdit = (id: string, data: any) => {
        console.log(id, data);
        setIsEditing(true)
    }

    const handleDelete = (id: string, data: any) => {
        console.log("delete");

        console.log(id, data);
    }
    return (
        <div>
            <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
                <Table size='small'>
                    <TableHead>
                        <TableRow>
                            <TableCell colSpan={user.role === 'admin' ? 8 : 7} sx={{ textAlign: 'center' }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Typography variant="h6">Validate Configuration</Typography>
                                    {user.role === 'admin' &&
                                        <Button
                                            size='small'
                                            variant="outlined"
                                            startIcon={<Add />}
                                        // onClick={() => setIsAddNew(true)}
                                        >
                                            EQUIPMENT
                                        </Button>
                                    }
                                </Box>
                            </TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        <TableRow>
                            <TableCell width={100} align='center' >
                                <Typography fontWeight="bold">Equipment</Typography>
                            </TableCell>
                            <TableCell align='center' >
                                <Typography fontWeight="bold">Data Config</Typography>
                            </TableCell>
                        </TableRow>
                        {validate.list.map((eq) => {

                            return (

                                <TableRow key={eq._id}>
                                    <TableCell sx={{ pr: 0 }}>
                                        {/* {eq.equipment_name} */}
                                        <Typography fontWeight='bold'>{eq.equipment_name}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Table size='small'>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell>
                                                        <Typography fontWeight='bold'> First Package Code 8 Digit</Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography fontWeight='bold'> Selection Code</Typography>
                                                    </TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {eq.config.map((config, configIndex) => {
                                                    const configKey = `${eq._id}-${config.package8digit}`;
                                                    return (
                                                        <React.Fragment key={configIndex}>
                                                            {/* Level 1: Config */}
                                                            <TableRow>
                                                                <TableCell>
                                                                    <Typography> {config.package8digit}</Typography>
                                                                </TableCell>
                                                                <TableCell>
                                                                    <Typography>  {config.selection_code}</Typography>
                                                                </TableCell>
                                                            </TableRow>

                                                            {/* Level 2: Data with Selection Code */}
                                                            {config.data_with_selection_code.map((data, dataIndex) => {
                                                                const dataKey = `${configKey}-${data.package_selection_code}`;
                                                                const isConfigExpanded = expanded.package === configKey;
                                                                return (
                                                                    <TableRow key={dataIndex}>
                                                                        <TableCell colSpan={2} sx={{ pl: 2 }}>
                                                                            <Button size='small' variant="text" color='primary'
                                                                                disableTouchRipple
                                                                                disableFocusRipple
                                                                                disableRipple
                                                                                sx={{ backgroundColor: 'inherit', pt: 0, pb: 0 }}
                                                                                startIcon={isConfigExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                                onClick={() => toggleExpand(configKey, 'package')}
                                                                            >
                                                                                <Typography>{data.product_name}</Typography>
                                                                            </Button>
                                                                            {/* collapse */}
                                                                            <Collapse in={isConfigExpanded} timeout="auto" unmountOnExit>
                                                                                <Box sx={{ mt: 1, p: 2, border: '1px solid #ccc', borderRadius: 1 }}>
                                                                                    <Grid2 container spacing={1}>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextField
                                                                                                size='small'
                                                                                                label="Package Selection Code"
                                                                                                value={data.package_selection_code}
                                                                                                fullWidth
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextField
                                                                                                size='small'
                                                                                                label="Product Name"
                                                                                                value={data.product_name}
                                                                                                fullWidth
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextField
                                                                                                size='small'
                                                                                                label="Recipe Name"
                                                                                                value={data.recipe_name}
                                                                                                fullWidth
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextField
                                                                                                size='small'
                                                                                                label="Validate Type"
                                                                                                value={data.validate_type}
                                                                                                fullWidth
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextField
                                                                                                size='small'
                                                                                                label="Operation Code"
                                                                                                value={data.operation_code}
                                                                                                fullWidth
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextField
                                                                                                size='small'
                                                                                                label="On Operation"
                                                                                                value={data.on_operation}
                                                                                                fullWidth
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4, sm: 4 }}>
                                                                                            <FormControlLabel
                                                                                                control={<Checkbox checked={data.options.use_on_operation} />}
                                                                                                label={
                                                                                                    <Typography variant="body2">On Operation</Typography>
                                                                                                }
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4, sm: 4 }}>
                                                                                            <FormControlLabel
                                                                                                control={<Checkbox checked={data.options.use_operation_code} />}
                                                                                                label={
                                                                                                    <Typography variant="body2">Operation Code</Typography>
                                                                                                }
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4, sm: 4 }}>
                                                                                            <FormControlLabel
                                                                                                control={<Checkbox checked={data.options.use_lot_hold} />}
                                                                                                label={
                                                                                                    <Typography variant="body2">Check Lot Hold</Typography>
                                                                                                }
                                                                                            />
                                                                                        </Grid2>

                                                                                        {/* allow tool ids */}
                                                                                        <Grid2 size={{ xs: 12, md: 12 }}>
                                                                                            <Typography>Allow Tool IDs</Typography>
                                                                                        </Grid2>

                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            <TextField
                                                                                                autoComplete='off'
                                                                                                size='small'
                                                                                                label="Position 1"
                                                                                                fullWidth
                                                                                                value={data.allow_tool_id.position_1.join(',')}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            <TextField
                                                                                                autoComplete='off'
                                                                                                size='small'
                                                                                                label="Position 2"
                                                                                                fullWidth
                                                                                                value={data.allow_tool_id.position_2.join(',')}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            <TextField
                                                                                                autoComplete='off'
                                                                                                size='small'
                                                                                                label="Position 3"
                                                                                                fullWidth
                                                                                                value={data.allow_tool_id.position_3.join(',')}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            <TextField
                                                                                                autoComplete='off'
                                                                                                size='small'
                                                                                                label="Position 4"
                                                                                                fullWidth
                                                                                                value={data.allow_tool_id.position_4.join(',')}
                                                                                            />
                                                                                        </Grid2>
                                                                                        {user.role === 'admin' &&
                                                                                            <Grid2 size={{ xs: 12, md: 12, }} display='flex' justifyContent='flex-end'>
                                                                                                {isEditing &&
                                                                                                    <div>
                                                                                                        <IconButton
                                                                                                            size='small'
                                                                                                            color='primary'
                                                                                                            onClick={
                                                                                                                () => handleEdit(eq._id, data)
                                                                                                            }
                                                                                                        >
                                                                                                            <Edit fontSize='small' />
                                                                                                        </IconButton>

                                                                                                    </div>
                                                                                                }
                                                                                                <IconButton
                                                                                                    size='small'
                                                                                                    color='error'
                                                                                                    onClick={
                                                                                                        () => handleDelete(eq._id, data)
                                                                                                    }
                                                                                                >
                                                                                                    <Delete fontSize='small' />
                                                                                                </IconButton>
                                                                                            </Grid2>
                                                                                        }

                                                                                    </Grid2>
                                                                                </Box>
                                                                            </Collapse>
                                                                        </TableCell>
                                                                    </TableRow>
                                                                );
                                                            })}
                                                        </React.Fragment>
                                                    )
                                                })
                                                }
                                            </TableBody>
                                        </Table>
                                    </TableCell>
                                </TableRow>)
                        }
                        )}
                    </TableBody>
                </Table>
                <TablePagination
                    rowsPerPageOptions={[5, 10, 25]}
                    component="div"
                    count={validate.totalCount || 0}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </TableContainer>
        </div >
    )
}


ValidateConfig.propTypes = {
    user: PropTypes.shape({
        name: PropTypes.string.isRequired,
        email: PropTypes.string.isRequired,
        role: PropTypes.string.isRequired,
    }).isRequired,
}

export default ValidateConfig
