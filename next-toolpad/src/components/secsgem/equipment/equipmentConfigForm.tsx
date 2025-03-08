import React from 'react';
import {
    Paper,
    Typography,
    Grid,
    Checkbox,
    FormControlLabel,
    TextField
} from '@mui/material';

interface EquipmentConfigViewerProps {
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

export const EquipmentConfigViewer = ({ data }: EquipmentConfigViewerProps) => {
    return (
        <Paper sx={{ p: 3, mb: 3 }}>
            {/* Equipment Name Section */}
            <Typography variant="h6" gutterBottom>
                Equipment: {data.equipment_name}
            </Typography>

            {/* Config List */}
            {data.config.map((configItem, configIndex) => (
                <Paper key={configIndex} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                    {/* Package and Selection Code */}
                    <Grid container spacing={2}>
                        <Grid item xs={6}>
                            <Typography variant="subtitle1">
                                Package: {configItem.package8digit}
                            </Typography>
                        </Grid>
                        <Grid item xs={6}>
                            <Typography variant="subtitle1">
                                Selection Code: {configItem.selection_code}
                            </Typography>
                        </Grid>
                    </Grid>

                    {/* Data with Selection Code */}
                    {configItem.data_with_selection_code.map((dataItem, dataIndex) => (
                        <div key={dataIndex} style={{ marginTop: '1rem' }}>
                            {/* Options Section */}
                            <Paper sx={{ p: 2, mb: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Options
                                </Typography>
                                <Grid container spacing={2}>
                                    {Object.entries(dataItem.options).map(([key, value]) => (
                                        <Grid item xs={4} key={key}>
                                            <FormControlLabel
                                                control={<Checkbox checked={value} disabled />}
                                                label={key.replace(/_/g, ' ')}
                                            />
                                        </Grid>
                                    ))}
                                </Grid>
                            </Paper>

                            {/* Main Data Fields */}
                            <Grid container spacing={2} sx={{ mb: 2 }}>
                                {[
                                    'package_selection_code',
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
                                            disabled
                                        />
                                    </Grid>
                                ))}
                            </Grid>

                            {/* Allow Tool IDs */}
                            <Paper sx={{ p: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Allow Tool IDs
                                </Typography>
                                <Grid container spacing={2}>
                                    {Object.entries(dataItem.allow_tool_id).map(([position, tools]) => (
                                        <Grid item xs={3} key={position}>
                                            <TextField
                                                label={`Position ${position.split('_')[1]}`}
                                                value={tools.join(', ') || 'None'}
                                                fullWidth
                                                disabled
                                            />
                                        </Grid>
                                    ))}
                                </Grid>
                            </Paper>
                        </div>
                    ))}
                </Paper>
            ))}
        </Paper>
    );
};