'use client'
import { Box, Button, CircularProgress, Divider, Fade, FormControl, IconButton, InputLabel, MenuItem, Paper, Select, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Toolbar, Typography } from '@mui/material'
import React, { useEffect, useState } from 'react'
import { useApiContext } from '../../context/apiContext';
import { Add, ExpandLess, ExpandMore } from '@mui/icons-material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';


import { ValidateConfigPropTypes, ValidateAllowToolId, } from '@/src/service/types';

import { AllowToolId } from './allowToolId';



export default function ValidateConfig_component() {
    const { validate } = useApiContext();
    // const [equipmentList, setequipmentList] = useState(validate.list)

    const [expanded, setExpanded] = useState<{
        equipment: number | null;
        config: number | null;
        data: number | null;
    }>({ equipment: null, config: null, data: null });

    const fetchingData = async () => {
        const response = await validate.gets()
        console.log(response.docs);

    }

    useEffect(() => {
        fetchingData()
    }, [])

    const toggleExpand = (level: 'equipment' | 'config' | 'data', index: number) => {
        setExpanded(prev => ({
            ...prev,
            [level]: prev[level] === index ? null : index,
            ...(level === 'equipment' && { config: null, data: null }),
            ...(level === 'config' && { data: null }),
        }));
    };

    return (
        <div>
            {validate.loading ? (
                <Fade in={validate.loading} unmountOnExit>
                    <CircularProgress color="secondary" />
                </Fade>
            ) : (
                // <EditableEquipmentConfigTable data={validateList} />
                <TableContainer component={Paper}>
                    <Toolbar sx={{ justifyContent: 'space-between', }}>
                        <Typography variant="h6">Validate Config</Typography>

                        <Button
                            size='small'
                            variant="outlined"
                            startIcon={<Add />}
                        // onClick={() => setCreateDialogOpen(true)}
                        // onClick={() => setAddEquipment(true)}
                        >
                            New Config
                        </Button>
                    </Toolbar>
                    <Divider />
                    {/* <pre>{JSON.stringify(validate.list, null, 2)}</pre> */}

                    {validate.list.map((equipment, equipmentIndex) => (
                        <Box key={equipment.equipment_name}>
                            <Typography>{equipment.equipment_name}</Typography>
                            <Table size="small" key={equipmentIndex}>

                                <TableBody >
                                    <React.Fragment key={equipment.equipment_name}>
                                        <TableRow>
                                            {/* <TableCell>
                                                <IconButton
                                                    size="small"
                                                    onClick={() => toggleExpand('equipment', equipmentIndex)}
                                                >
                                                    {expanded.equipment === equipmentIndex ? <ExpandLess /> : <ExpandMore />}
                                                </IconButton>
                                            </TableCell> */}
                                            {equipment.config.map((config, configIndex) => (
                                                <TableRow key={configIndex}>
                                                    <TableCell>
                                                        <IconButton
                                                            size="small"
                                                            onClick={() => toggleExpand('config', configIndex)}
                                                        >
                                                            {expanded.config === configIndex ? <ExpandLess /> : <ExpandMore />}
                                                        </IconButton>
                                                    </TableCell>
                                                    <TableCell>{config.package8digit}</TableCell>
                                                    <TableCell>{config.selection_code}</TableCell>
                                                    <TableCell>{config.data_with_selection_code.length}</TableCell>
                                                </TableRow>

                                            ))}

                                        </TableRow>
                                    </React.Fragment>

                                </TableBody>
                            </Table>
                        </Box>
                    ))}

                </TableContainer>

            )}
        </div>
    )
}
