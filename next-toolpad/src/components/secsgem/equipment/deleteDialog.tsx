import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material';

export const DeleteDialog = ({
    open,
    onClose,
    onConfirm
}: {
    open: boolean;
    onClose: () => void;
    onConfirm: () => void;
}) => (
    <Dialog open={open} onClose={onClose}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Are you sure you want to delete this equipment? This action cannot be undone.
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