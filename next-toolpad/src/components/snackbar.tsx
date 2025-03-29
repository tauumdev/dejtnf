import { Alert, Snackbar } from '@mui/material'

export const SnackbarNotify = ({
    open,
    onClose,
    message,
    snackbarSeverity
}: {
    open: boolean;
    onClose: () => void;
    onConfirm: () => void;
    message: string;
    snackbarSeverity: 'error' | 'info' | 'success' | 'warning'
}) => (
    <Snackbar open={open} autoHideDuration={6000} onClose={onClose}>
        <Alert
            onClose={onClose}
            severity={snackbarSeverity}
            variant="filled"
            sx={{ width: '100%' }}
        >
            {message}
        </Alert>
    </Snackbar>
);