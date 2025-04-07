import React from 'react';
import { Autocomplete, TextField } from '@mui/material';

type AutocompleteInputProps = {
    id: string;
    label: string;
    options: string[];
    value: string;
    onInputChange: (value: string) => void;
    disabled?: boolean;
    maxLength?: number;
    onKeyDown?: (event: React.KeyboardEvent<HTMLDivElement>) => void;
};

const AutocompleteInput: React.FC<AutocompleteInputProps> = ({
    id,
    label,
    options,
    value,
    onInputChange,
    disabled = false,
    maxLength = 255,
    onKeyDown,
}) => {
    return (
        <Autocomplete
            id={id}
            size="small"
            freeSolo
            options={options}
            value={value}
            onInputChange={(_, newValue) => onInputChange(newValue)}
            disabled={disabled}
            renderInput={(params) => (
                <TextField
                    {...params}
                    label={label}
                    fullWidth
                    inputProps={{ ...params.inputProps, maxLength }}
                />
            )}
            onKeyDown={onKeyDown}
        />
    );
};

export default AutocompleteInput;