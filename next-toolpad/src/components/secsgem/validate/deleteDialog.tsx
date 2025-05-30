import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button, Box, Typography } from '@mui/material';

export const DeleteDialog = ({
    level,
    open,
    onClose,
    onConfirm

}: {
    level: string;
    open: boolean;
    onClose: () => void;
    onConfirm: () => void;
}) => (
    <Dialog open={open} onClose={onClose}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
            <DialogContentText>
                <Box sx={{ display: 'block' }}>
                    <Typography>Are you sure you want to delete</Typography>
                    <Typography variant='body1'>{level} ?</Typography>
                    <Typography>This action cannot be undone.</Typography>
                </Box>
            </DialogContentText>
        </DialogContent>
        <DialogActions>
            <Button onClick={onClose} color="secondary">
                Cancel
            </Button>
            <Button onClick={onConfirm} color="error" autoFocus>
                Delete
            </Button>
        </DialogActions>
    </Dialog>
);