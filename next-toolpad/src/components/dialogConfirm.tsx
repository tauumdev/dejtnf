import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button, Slide } from '@mui/material';
import { TransitionProps } from '@mui/material/transitions';


const Transition = React.forwardRef(function Transition(
    props: TransitionProps & {
        children: React.ReactElement<any, any>;
    },
    ref: React.Ref<unknown>,
) {
    return <Slide direction="up" ref={ref} {...props} />;
});

export const DialogConfirm = ({
    open,
    onCancel,
    onConfirm,
    title,
    message,
    confirmText,
    confirmColor,
    cancelText,
}: {
    open: boolean;
    onCancel: () => void;
    onConfirm: () => void;
    title: string,
    message: string,
    confirmText: 'CREATE' | 'DELETE' | 'UPDATE' | 'SAVE' | 'OK',
    confirmColor: "success" | "error" | "info" | "warning" | "primary" | "secondary" | "inherit",
    cancelText: string,
}) => (
    <Dialog open={open} onClose={onCancel} TransitionComponent={Transition} keepMounted>
        <DialogTitle>{title}</DialogTitle>
        <DialogContent>
            <DialogContentText>
                {message}
            </DialogContentText>
        </DialogContent>
        <DialogActions>
            {cancelText && (
                <Button size='small' onClick={onCancel} variant='outlined' color='inherit'>
                    {cancelText}
                </Button>
            )}
            <Button size='small' onClick={onConfirm} variant='contained' color={confirmColor || 'error'} autoFocus>
                {confirmText}
            </Button>
        </DialogActions>
    </Dialog>
);