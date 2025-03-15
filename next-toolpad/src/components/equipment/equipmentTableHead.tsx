import { TableHead, TableRow, TableCell, Typography } from '@mui/material';

export const EquipmentTableHead = () => (
    <TableHead>
        <TableRow>
            <TableCell><Typography fontWeight="bold">Name</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Model</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">IP</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Port</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">ID</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Mode</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Enable</Typography></TableCell>
            <TableCell><Typography fontWeight="bold">Actions</Typography></TableCell>
        </TableRow>
    </TableHead>
);