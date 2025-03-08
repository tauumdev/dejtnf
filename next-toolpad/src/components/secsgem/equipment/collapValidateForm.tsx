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

interface EquipmentConfigTableProps {
    data: {
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
    };
}

export const EquipmentConfigTable = ({ data }: EquipmentConfigTableProps) => {
    const [expandedConfigIndex, setExpandedConfigIndex] = useState<number | null>(null);
    const [expandedDataIndex, setExpandedDataIndex] = useState<number | null>(null);

    const toggleConfig = (index: number) => {
        setExpandedConfigIndex(expandedConfigIndex === index ? null : index);
        setExpandedDataIndex(null);
    };

    const toggleData = (index: number) => {
        setExpandedDataIndex(expandedDataIndex === index ? null : index);
    };

    return (
        <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
                Equipment: {data.equipment_name}
            </Typography>

            <TableContainer>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell width="5%" />
                            <TableCell>Package</TableCell>
                            <TableCell>Selection Code</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {data.config.map((configItem, configIndex) => (
                            <React.Fragment key={configIndex}>
                                {/* Config Row */}
                                <TableRow>
                                    <TableCell>
                                        <IconButton
                                            size="small"
                                            onClick={() => toggleConfig(configIndex)}
                                        >
                                            {expandedConfigIndex === configIndex ? <ExpandLess /> : <ExpandMore />}
                                        </IconButton>
                                    </TableCell>
                                    <TableCell>{configItem.package8digit}</TableCell>
                                    <TableCell>{configItem.selection_code}</TableCell>
                                    <TableCell>
                                        {/* Add action buttons here if needed */}
                                    </TableCell>
                                </TableRow>

                                {/* Data with Selection Code Collapse */}
                                <TableRow>
                                    <TableCell colSpan={4} sx={{ py: 0 }}>
                                        <Collapse in={expandedConfigIndex === configIndex}>
                                            <Table size="small" sx={{ bgcolor: 'background.default' }}>
                                                <TableBody>
                                                    {configItem.data_with_selection_code.map((dataItem, dataIndex) => (
                                                        <React.Fragment key={dataIndex}>
                                                            <TableRow>
                                                                <TableCell width="5%">
                                                                    <IconButton
                                                                        size="small"
                                                                        onClick={() => toggleData(dataIndex)}
                                                                    >
                                                                        {expandedDataIndex === dataIndex ? <ExpandLess /> : <ExpandMore />}
                                                                    </IconButton>
                                                                </TableCell>
                                                                <TableCell colSpan={3}>
                                                                    {dataItem.package_selection_code}
                                                                </TableCell>
                                                            </TableRow>

                                                            <TableRow>
                                                                <TableCell colSpan={4} sx={{ py: 0 }}>
                                                                    <Collapse in={expandedDataIndex === dataIndex}>
                                                                        <Box sx={{ p: 2 }}>
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
                                                                                    'operation_code',
                                                                                    'on_operation',
                                                                                    'validate_type',
                                                                                    'recipe_name',
                                                                                    'product_name',
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

                                                                            {/* Allow Tool IDs */}
                                                                            <Grid container spacing={2}>
                                                                                {Object.entries(dataItem.allow_tool_id).map(([position, tools]) => (
                                                                                    <Grid item xs={3} key={position}>
                                                                                        <TextField
                                                                                            label={`Position ${position.split('_')[1]}`}
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
                                        </Collapse>
                                    </TableCell>
                                </TableRow>
                            </React.Fragment>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
};