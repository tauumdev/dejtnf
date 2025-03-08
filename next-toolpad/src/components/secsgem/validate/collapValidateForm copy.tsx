import React, { useState } from 'react';
import {
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Collapse,
    Checkbox,
    FormControlLabel,
    TextField,
    Box,
    Grid
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';

interface EquipmentConfig {
    equipment_name: string;
    config: {
        package8digit: string;
        selection_code: string;
        data_with_selection_code: {
            options: {
                use_operation_code: boolean;
                use_on_operation: boolean;
                use_lot_hold: boolean;
            };
            package_selection_code: string;
            operation_code: string;
            on_operation: string;
            validate_type: string;
            recipe_name: string;
            product_name: string;
            allow_tool_id: {
                [key: string]: string[];
            };
        }[];
    }[];
}

interface EquipmentConfigTableProps {
    data: EquipmentConfig[];
}

export const EquipmentConfigTable = ({ data }: EquipmentConfigTableProps) => {
    const [expanded, setExpanded] = useState<{
        equipment: number | null;
        config: number | null;
        data: number | null;
    }>({ equipment: null, config: null, data: null });

    const toggleExpand = (level: 'equipment' | 'config' | 'data', index: number) => {
        setExpanded(prev => ({
            ...prev,
            [level]: prev[level] === index ? null : index,
            // Reset child levels when parent collapses
            ...(level === 'equipment' && { config: null, data: null }),
            ...(level === 'config' && { data: null }),
        }));
    };

    return (
        <TableContainer component={Paper}>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell width="5%" />
                        <TableCell>Equipment Name</TableCell>
                        <TableCell>Total Configs</TableCell>
                    </TableRow>
                </TableHead>

                <TableBody>
                    {data.map((equipment, equipmentIndex) => (
                        <React.Fragment key={equipment.equipment_name}>
                            {/* Equipment Level */}
                            <TableRow>
                                <TableCell>
                                    <IconButton
                                        size="small"
                                        onClick={() => toggleExpand('equipment', equipmentIndex)}
                                    >
                                        {expanded.equipment === equipmentIndex ? <ExpandLess /> : <ExpandMore />}
                                    </IconButton>
                                </TableCell>
                                <TableCell>{equipment.equipment_name}</TableCell>
                                <TableCell>{equipment.config.length}</TableCell>
                            </TableRow>

                            {/* Config Level */}
                            <TableRow>
                                <TableCell colSpan={3} sx={{ py: 0 }}>
                                    <Collapse in={expanded.equipment === equipmentIndex}>
                                        <Box sx={{ ml: 3, bgcolor: 'background.paper' }}>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell width="5%" />
                                                        <TableCell>Package</TableCell>
                                                        <TableCell>Selection Code</TableCell>
                                                        <TableCell>Data Entries</TableCell>
                                                    </TableRow>
                                                </TableHead>

                                                <TableBody>
                                                    {equipment.config.map((config, configIndex) => (
                                                        <React.Fragment key={config.package8digit}>
                                                            <TableRow>
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

                                                            {/* Data Level */}
                                                            <TableRow>
                                                                <TableCell colSpan={4} sx={{ py: 0 }}>
                                                                    <Collapse in={expanded.config === configIndex}>
                                                                        <Box sx={{ ml: 3, bgcolor: 'background.default' }}>
                                                                            <Table size="small">
                                                                                <TableHead>
                                                                                    <TableRow>
                                                                                        <TableCell width="5%" />
                                                                                        <TableCell>Package Selection</TableCell>
                                                                                        <TableCell>Operation Code</TableCell>
                                                                                        <TableCell>Validation Type</TableCell>
                                                                                    </TableRow>
                                                                                </TableHead>

                                                                                <TableBody>
                                                                                    {config.data_with_selection_code.map((dataItem, dataIndex) => (
                                                                                        <React.Fragment key={dataIndex}>
                                                                                            <TableRow>
                                                                                                <TableCell>
                                                                                                    <IconButton
                                                                                                        size="small"
                                                                                                        onClick={() => toggleExpand('data', dataIndex)}
                                                                                                    >
                                                                                                        {expanded.data === dataIndex ? <ExpandLess /> : <ExpandMore />}
                                                                                                    </IconButton>
                                                                                                </TableCell>
                                                                                                <TableCell>{dataItem.package_selection_code}</TableCell>
                                                                                                <TableCell>{dataItem.operation_code}</TableCell>
                                                                                                <TableCell>{dataItem.validate_type}</TableCell>
                                                                                            </TableRow>

                                                                                            {/* Detail Level */}
                                                                                            <TableRow>
                                                                                                <TableCell colSpan={4} sx={{ py: 0 }}>
                                                                                                    <Collapse in={expanded.data === dataIndex}>
                                                                                                        <Box sx={{ ml: 3, p: 2 }}>
                                                                                                            {/* Options */}
                                                                                                            <Grid container spacing={2} sx={{ mb: 2 }}>
                                                                                                                {Object.entries(dataItem.options).map(([key, value]) => (
                                                                                                                    <Grid item xs={4} key={key}>
                                                                                                                        <FormControlLabel
                                                                                                                            control={<Checkbox checked={value} disabled />}
                                                                                                                            label={key.replace(/_/g, ' ')}
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                ))}
                                                                                                            </Grid>

                                                                                                            {/* Main Fields */}
                                                                                                            <Grid container spacing={2} sx={{ mb: 2 }}>
                                                                                                                {[
                                                                                                                    'recipe_name',
                                                                                                                    'product_name',
                                                                                                                    'on_operation'
                                                                                                                ].map((field) => (
                                                                                                                    <Grid item xs={4} key={field}>
                                                                                                                        <TextField
                                                                                                                            label={field.replace(/_/g, ' ')}
                                                                                                                            value={dataItem[field as keyof typeof dataItem]}
                                                                                                                            fullWidth
                                                                                                                            size="small"
                                                                                                                            disabled
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                ))}
                                                                                                            </Grid>

                                                                                                            {/* Tool IDs */}
                                                                                                            <Grid container spacing={2}>
                                                                                                                {Object.entries(dataItem.allow_tool_id).map(([pos, tools]) => (
                                                                                                                    <Grid item xs={3} key={pos}>
                                                                                                                        <TextField
                                                                                                                            label={`Position ${pos.split('_')[1]}`}
                                                                                                                            value={tools.join(', ') || 'None'}
                                                                                                                            fullWidth
                                                                                                                            size="small"
                                                                                                                            disabled
                                                                                                                        />
                                                                                                                    </Grid>
                                                                                                                ))}
                                                                                                            </Grid>
                                                                                                        </Box>
                                                                                                    </Collapse>
                                                                                                </TableCell>
                                                                                            </TableRow>
                                                                                        </React.Fragment>
                                                                                    ))}
                                                                                </TableBody>
                                                                            </Table>
                                                                        </Box>
                                                                    </Collapse>
                                                                </TableCell>
                                                            </TableRow>
                                                        </React.Fragment>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </Box>
                                    </Collapse>
                                </TableCell>
                            </TableRow>
                        </React.Fragment>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};