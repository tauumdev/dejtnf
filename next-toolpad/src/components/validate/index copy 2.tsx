'use client'
import React, { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Checkbox, Collapse, FormControlLabel, Grid2, IconButton, MenuItem, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TablePagination, TableRow, TextField, Typography } from '@mui/material';
import { Add, Cancel, Delete, Edit, ExpandLess, ExpandMore, Save } from '@mui/icons-material';
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
        console.log(key);
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

    // Define state edit
    const [editingKey, setEditingKey] = useState<string | null>(null); // เก็บ key ของรายการที่กำลังแก้ไข
    const [useOperation, setUseOperation] = useState(true);
    const [useOnOperation, setUseOnOperation] = useState(false);
    const [useLotHold, setUseLotHold] = useState(false);

    // const [editedData, setEditedData] = useState<any>({}); // เก็บข้อมูลที่แก้ไข

    const editRefs = {
        package_selection_code: useRef<HTMLInputElement>(null),
        product_name: useRef<HTMLInputElement>(null),
        recipe_name: useRef<HTMLInputElement>(null),
        validate_type: useRef<HTMLInputElement>(null),
        operation_code: useRef<HTMLInputElement>(null),
        on_operation: useRef<HTMLInputElement>(null),
        use_operation: useRef<HTMLInputElement>(null),
        use_on_operation: useRef<HTMLInputElement>(null),
        use_lot_hold: useRef<HTMLInputElement>(null),
        allowId_position_1: useRef<HTMLInputElement>(null),
        allowId_position_2: useRef<HTMLInputElement>(null),
        allowId_position_3: useRef<HTMLInputElement>(null),
        allowId_position_4: useRef<HTMLInputElement>(null),
    }

    // Handle edit
    const startEditing = (key: string) => {
        setEditingKey(key);
        // setEditedData(data);

        const [_id, package8digit, package_selection_code] = key.split(',')
        const dataByEquipmentName = validate.list.filter(item => item._id === _id);
        console.log("Data by equipment _id: ", dataByEquipmentName);

    }

    // Handle Save
    const handleSave = async (key: string) => {
        const [_id, package8digit, package_selection_code] = key.split(',')
        const dataByEquipmentName = validate.list.filter(item => item._id === _id);
        console.log("Save");
        // console.log("saveKey", key);
        // console.log("editingKey", editingKey);

        if (!dataByEquipmentName) {
            console.error("Data not found for _id:", _id);
            return;
        }

        const updateData = {
            package8digit,
            package_selection_code,
            product_name: editRefs.product_name.current?.value,
            recipe_name: editRefs.recipe_name.current?.value,
            validate_type: editRefs.validate_type.current?.value,
            operation_code: editRefs.operation_code.current?.value,
            on_operation: editRefs.on_operation.current?.value,
            options: {
                use_operation_code: useOperation,
                use_on_operation: useOnOperation,
                use_lot_hold: editRefs.use_lot_hold.current?.value === 'true',
            },
            allow_tool_id: {
                position_1: editRefs.allowId_position_1.current?.value.split(','),
                position_2: editRefs.allowId_position_2.current?.value.split(','),
                position_3: editRefs.allowId_position_3.current?.value.split(','),
                position_4: editRefs.allowId_position_4.current?.value.split(','),
            }
        }
        console.log(updateData);

        setEditingKey(null);
        // console.log(editRefs.package_selection_code.current?.value);
        // console.log(editRefs.product_name.current?.value);
    }

    // Handle delete
    const handleDelete = async (key: string) => {
        const [_id, package8digit, package_selection_code] = key.split(',')
        const dataByEquipmentName = validate.list.find(item => item._id === _id);
        console.log("Delete");
        // console.log("deleteKey", key);
        // console.log("editingKey", editingKey);

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
            // console.log('delete equipment _id:', _id);

        } else {
            await validate.update(_id, dataByEquipmentName);
            // console.log('update equipment _id:', _id);
            // console.log(dataByEquipmentName);
        }
        await validate.gets(undefined, undefined, page + 1, rowsPerPage, sortBy, sortOrder === 'asc' ? 1 : -1);
    }

    // const TextFieldData: React.FC<{
    //     isEditing: boolean,
    //     editRef: React.RefObject<HTMLInputElement>,
    //     label: string,
    //     value: any,
    //     select?: boolean,
    //     children?: React.ReactNode
    // }> = ({ isEditing, editRef, label, value, select = false, children }) => {
    //     return isEditing ? (
    //         <TextField
    //             fullWidth
    //             autoComplete='off'
    //             size='small'
    //             label={label}
    //             defaultValue={value}
    //             inputRef={editRef}
    //             select={select}
    //         >{children}</TextField>
    //     ) : (
    //         <TextField
    //             fullWidth
    //             size='small'
    //             label={label}
    //             value={value}
    //         >{children}</TextField>
    //     )
    // }

    const TextFieldData: React.FC<{
        isEditing: boolean,
        editRef: React.RefObject<HTMLInputElement>,
        label: string,
        defaultValue: any, // ใช้ defaultValue แทน value
        select?: boolean,
        children?: React.ReactNode
    }> = ({ isEditing, editRef, label, defaultValue, select = false, children }) => {
        return isEditing ? (
            <TextField
                fullWidth
                autoComplete='off'
                size='small'
                label={label}
                defaultValue={defaultValue} // ใช้ defaultValue
                inputRef={editRef}
                select={select}
            // disabled={!isEditing}
            >
                {children}
            </TextField>
        ) : (
            <TextField
                fullWidth
                // autoComplete='off'
                size='small'
                label={label}
                value={defaultValue} // ใช้ defaultValue
            // inputRef={editRef}
            // select={select}
            // disabled={!isEditing}
            >
                {children}
            </TextField>
        )
    };

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
                                        <Typography fontWeight='bold'>{eq.equipment_name}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Table size='small'>
                                            <TableHead>
                                                <TableRow>
                                                    <TableCell width={450}>
                                                        <Typography fontWeight='bold'> First Package Code 8 Digit</Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography fontWeight='bold'> Selection Code</Typography>
                                                    </TableCell>
                                                </TableRow>
                                            </TableHead>
                                            <TableBody>
                                                {eq.config.map((config, configIndex) => {
                                                    const configKey = `${eq._id},${config.package8digit}`;
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
                                                                const dataKey = `${configKey},${data.package_selection_code}`;
                                                                const isDataItemExpanded = expanded.package_selection_code === dataKey;
                                                                const isEditing = editingKey === dataKey;
                                                                return (
                                                                    <TableRow key={dataIndex}>
                                                                        <TableCell colSpan={2} sx={{ pl: 2 }}>
                                                                            <Button size='small' variant="text" color='primary'
                                                                                disableTouchRipple
                                                                                disableFocusRipple
                                                                                disableRipple
                                                                                sx={{ backgroundColor: 'inherit', pt: 0, pb: 0 }}
                                                                                startIcon={isDataItemExpanded ? <ExpandLess /> : <ExpandMore />}
                                                                                onClick={() => toggleExpand(dataKey, 'package_selection_code')}
                                                                            >
                                                                                <Typography>{data.product_name}</Typography>
                                                                            </Button>
                                                                            {/* collapse */}
                                                                            <Collapse in={isDataItemExpanded} timeout="auto" unmountOnExit>
                                                                                <Box sx={{ mt: 1, p: 2, border: '1px solid #ccc', borderRadius: 1 }}>
                                                                                    <Grid2 container spacing={1}>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.package_selection_code}
                                                                                                label="Package Selection Code"
                                                                                                defaultValue={data.package_selection_code}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.product_name}
                                                                                                label="Product Name"
                                                                                                defaultValue={data.product_name}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.recipe_name}
                                                                                                label="Recipe Name"
                                                                                                defaultValue={data.recipe_name}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.validate_type}
                                                                                                label="Validate Type"
                                                                                                defaultValue={data.validate_type}
                                                                                                select
                                                                                            >
                                                                                                <MenuItem value={'recipe'}>Recipe</MenuItem>
                                                                                                <MenuItem value={'tool_id'}>Tool ID</MenuItem>
                                                                                            </TextFieldData>

                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.operation_code}
                                                                                                label="Operation Code"
                                                                                                defaultValue={data.operation_code}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.on_operation}
                                                                                                label="On Operation"
                                                                                                defaultValue={data.on_operation}
                                                                                            />
                                                                                        </Grid2>

                                                                                        {/* options */}
                                                                                        {/* <Grid2 size={{ xs: 8, md: 4, sm: 4 }}>
                                                                                            <FormControlLabel
                                                                                                control={<Checkbox
                                                                                                    checked={isEditing ? useOperation : data.options.use_operation_code}
                                                                                                    onChange={e => {
                                                                                                        if (isEditing) {
                                                                                                            setUseOperation(e.target.checked);
                                                                                                        }
                                                                                                    }}
                                                                                                />}
                                                                                                label={
                                                                                                    <Typography variant="body2">Operation Code</Typography>
                                                                                                }
                                                                                            />
                                                                                        </Grid2>

                                                                                        <Grid2 size={{ xs: 8, md: 4, sm: 4 }}>
                                                                                            <FormControlLabel
                                                                                                control={<Checkbox
                                                                                                    checked={isEditing ? useOnOperation : data.options.use_on_operation}
                                                                                                    onChange={e => {
                                                                                                        if (isEditing) {
                                                                                                            setUseOnOperation(e.target.checked);
                                                                                                        }
                                                                                                    }}
                                                                                                />}
                                                                                                label={
                                                                                                    <Typography variant="body2">On Operation</Typography>
                                                                                                }
                                                                                            />
                                                                                        </Grid2>

                                                                                        <Grid2 size={{ xs: 8, md: 4, sm: 4 }}>
                                                                                            <FormControlLabel
                                                                                                control={<Checkbox
                                                                                                    checked={isEditing ? useLotHold : data.options.use_lot_hold}
                                                                                                    onChange={e => {
                                                                                                        setUseLotHold(e.target.checked);
                                                                                                        // if (isEditing) {
                                                                                                        //     setUseLotHold(e.target.checked);
                                                                                                        // } else {
                                                                                                        //     setUseLotHold(data.options.use_lot_hold);
                                                                                                        // }
                                                                                                    }}
                                                                                                />}
                                                                                                label={
                                                                                                    <Typography variant="body2">Check Lot Hold</Typography>
                                                                                                }
                                                                                            />
                                                                                        </Grid2> */}
                                                                                        <Grid2 size={{ xs: 8, md: 4 }}>
                                                                                            {/* <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.use_operation}
                                                                                                label="Use Operation"
                                                                                                // defaultValue={data.options.use_operation_code}
                                                                                                defaultValue="false"
                                                                                                select
                                                                                            >
                                                                                                <MenuItem value={'false'}>Yes</MenuItem>
                                                                                                <MenuItem value={'true'}>No</MenuItem>
                                                                                            </TextFieldData> */}
                                                                                            <EditableTextField label="Enable" value={eq.enable} editing={isEditing && editingEquipment?._id === eq._id} inputRef={editRefs.enable} select >
                                                                                                <MenuItem value={'true'}>Yes</MenuItem>
                                                                                                <MenuItem value={'false'}>No</MenuItem>
                                                                                            </EditableTextField>

                                                                                        </Grid2>

                                                                                        {/* allow tool ids */}
                                                                                        <Grid2 size={{ xs: 12, md: 12 }}>
                                                                                            <Typography>Allow Tool IDs</Typography>
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.allowId_position_1}
                                                                                                label="Position 1"
                                                                                                defaultValue={data.allow_tool_id.position_1.join(',')}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.allowId_position_2}
                                                                                                label="Position 2"
                                                                                                defaultValue={data.allow_tool_id.position_2.join(',')}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.allowId_position_3}
                                                                                                label="Position 3"
                                                                                                defaultValue={data.allow_tool_id.position_3.join(',')}
                                                                                            />
                                                                                        </Grid2>
                                                                                        <Grid2 size={{ xs: 12, md: 6 }}>
                                                                                            {/* <TextFieldData
                                                                                                isEditing={isEditing}
                                                                                                editRef={editRefs.allowId_position_4}
                                                                                                label="Position 4"
                                                                                                value={data.allow_tool_id.position_4.join(',')}
                                                                                            /> */}
                                                                                            {isEditing ?
                                                                                                <TextField
                                                                                                    size='small'

                                                                                                    inputRef={editRefs.allowId_position_4}
                                                                                                    label="Position 4"
                                                                                                // defaultValue={data.allow_tool_id.position_4.join(',')}
                                                                                                // value={editRefs.allowId_position_4.current?.value}


                                                                                                />
                                                                                                :
                                                                                                <TextField
                                                                                                    size='small'
                                                                                                    label="Position 4"
                                                                                                    value={data.allow_tool_id.position_4.join(',')}
                                                                                                />
                                                                                            }
                                                                                        </Grid2>
                                                                                        {user.role === 'admin' &&
                                                                                            <Grid2 size={{ xs: 12, md: 12, }} display='flex' justifyContent='flex-end'>
                                                                                                {isEditing ?
                                                                                                    (
                                                                                                        <>
                                                                                                            <IconButton
                                                                                                                size='small'
                                                                                                                color='success'
                                                                                                                onClick={() => handleSave(dataKey)}
                                                                                                            >
                                                                                                                <Save fontSize='small' />
                                                                                                            </IconButton>
                                                                                                            <IconButton
                                                                                                                size='small'
                                                                                                                color='primary'
                                                                                                                onClick={() => setEditingKey(null)}
                                                                                                            >
                                                                                                                <Cancel fontSize='small' />
                                                                                                            </IconButton></>
                                                                                                    ) : (
                                                                                                        <IconButton
                                                                                                            size='small'
                                                                                                            color='primary'
                                                                                                            onClick={
                                                                                                                () => startEditing(dataKey)
                                                                                                            }
                                                                                                        >
                                                                                                            <Edit fontSize='small' />
                                                                                                        </IconButton>
                                                                                                    )

                                                                                                }
                                                                                                <IconButton
                                                                                                    size='small'
                                                                                                    color='error'
                                                                                                    onClick={
                                                                                                        () => handleDelete(dataKey)
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
