import React, { Fragment } from 'react';
import { Box, Table, TableBody, TableCell, TableRow, Typography } from '@mui/material';
import MemoizedAccordionItem from './memoizedAccordionItem';
import { ValidateConfig, DataWithSelectionCode } from './configManager';

type ConfigTableProps = {
    filteredEquipment: ValidateConfig[];
    userRole: string;
    editKeys: Set<string>;
    expandedAccordions: Set<string>;
    onToggleAccordion: (itemKey: string) => void;
    onEdit: (itemKey: string) => void;
    onSave: (itemKey: string, updatedData: DataWithSelectionCode) => void;
    onCancel: (itemKey: string) => void;
    onDelete: (itemKey: string) => void;
};

const ConfigTable: React.FC<ConfigTableProps> = ({
    filteredEquipment,
    userRole,
    editKeys,
    expandedAccordions,
    onToggleAccordion,
    onEdit,
    onSave,
    onCancel,
    onDelete,
}) => {
    return (
        <TableBody>
            {filteredEquipment.map((eq) => (
                <TableRow key={eq._id}>
                    <TableCell component="th" scope="row">
                        <Typography fontWeight="bold">{eq.equipment_name}</Typography>
                    </TableCell>
                    <TableCell>
                        <Box>
                            <Table size="small">
                                <TableBody>
                                    {eq.config.map((config) => (
                                        <Fragment key={config.package8digit}>
                                            <TableRow>
                                                <TableCell sx={{ width: 300 }}>
                                                    <Typography variant="body1">{config.package8digit}</Typography>
                                                </TableCell>
                                                <TableCell sx={{ width: 300 }}>
                                                    <Typography variant="body1">{config.selection_code}</Typography>
                                                </TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell colSpan={3} sx={{ p: 1 }}>
                                                    {config.data_with_selection_code.map((data) => {
                                                        const itemKey = `${eq._id}|${config.package8digit}|${data.package_selection_code}`;
                                                        return (
                                                            <MemoizedAccordionItem
                                                                key={data.package_selection_code}
                                                                userRole={userRole}
                                                                item={data}
                                                                isEditing={editKeys.has(itemKey)}
                                                                isExpanded={expandedAccordions.has(itemKey)}
                                                                onToggle={() => onToggleAccordion(itemKey)}
                                                                onEdit={() => onEdit(itemKey)}
                                                                onSave={(updatedData) => onSave(itemKey, updatedData)}
                                                                onCancel={() => onCancel(itemKey)}
                                                                onDelete={() => onDelete(itemKey)}
                                                            />
                                                        );
                                                    })}
                                                </TableCell>
                                            </TableRow>
                                        </Fragment>
                                    ))}
                                </TableBody>
                            </Table>
                        </Box>
                    </TableCell>
                </TableRow>
            ))}
        </TableBody>
    );
};

export default ConfigTable;