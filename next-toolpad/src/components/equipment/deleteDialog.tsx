import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material';

export const DeleteDialog = ({
    open,
    onClose,
    onConfirm,
    message
}: {
    open: boolean;
    onClose: () => void;
    onConfirm: () => void;
    message?: string;
}) => (
    <Dialog open={open} onClose={onClose}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
            <DialogContentText>
                {message || 'Are you sure you want to delete this item?'}
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