'use client'
import { Box, Button, CircularProgress, Fade, FormControl, InputLabel, MenuItem, Select, Stack, Toolbar, Typography } from '@mui/material'
import React, { useEffect, useState } from 'react'
import { useApiContext } from '../../context/apiContext';
import { Add } from '@mui/icons-material';

import { EditableEquipmentConfigTable } from './collapValidateForm';
import { ValidateConfigPropTypes, ValidateAllowToolId } from '@/src/service/types';
import { NewValidateData } from './newValidatedata'

import { AllowToolId } from './allowToolId';

const allowId_ = {
    position_1: ["00000001", "00000002"],
    position_2: ["00000004", "00000005", "00000006"],
    position_3: ["00000007", "00000008", "00000009"],
    position_4: ["00000010", "00000011", "00000012", "00000013"]
}


export default function ValidateConfig_component() {
    const { validate } = useApiContext();

    const [validateList, setValidateList] = useState<ValidateConfigPropTypes[]>([])

    const [allowId, setAllowId] = useState<ValidateAllowToolId>(allowId_)

    const fetchingData = async () => {
        const response = await validate.gets()
        // console.log(response.docs);
        setValidateList(response.docs)
        // setAllowId(validateList[0].config[0].data_with_selection_code[0].allow_tool_id)
    }

    useEffect(() => {
        fetchingData()
    }, [])



    const handleAllowToolIdSave = (updatedData: ValidateAllowToolId) => {
        // Here you would typically make API calls
        console.log('Saving data:', updatedData);
        setAllowId(updatedData);

        // Example API call:
        // api.saveToolIds(updatedData)
        //   .then(() => showSuccessMessage())
        //   .catch(error => showErrorMessage(error))
    };

    return (
        <div>
            {validate.loading ? (
                <Fade in={validate.loading} unmountOnExit>
                    <CircularProgress color="secondary" />
                </Fade>
            ) : (
                // <EditableEquipmentConfigTable data={validateList} />
                <AllowToolId initialData={allowId} onSave={handleAllowToolIdSave} />
                // <pre>{JSON.stringify(allowId, null, 2)}</pre>
            )}
        </div>
    )
}
