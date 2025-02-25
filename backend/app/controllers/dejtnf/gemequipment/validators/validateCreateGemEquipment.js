const { validateResult } = require('../../../../middleware/utils')
const { check } = require('express-validator')

/**
 * Validates create new item request
 */

// {
//     "equipment_name": "TNF-61", string
//     "equipment_model": "FCL", string
//     "address": "192.168.226.161", ip address
//     "port": 5000, number
//     "session_id": 61, number
//     "mode": "ACTIVE", string enum ['ACTIVE', 'PASSIVE']
//     "enable": true boolean
// },

const validateCreateGemEquipment = [
    check('equipment_name')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY')
        .trim(),
    check('equipment_model')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY')
        .trim(),
    check('address')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY')
        .trim(),
    check('port')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY')
        .isNumeric()
        .withMessage('NOT_A_NUMBER'),
    check('session_id')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY')
        .isNumeric()
        .withMessage('NOT_A_NUMBER'),
    check('mode')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY')
        .isIn(['ACTIVE', 'PASSIVE'])
        .withMessage('IS_INVALID'),
    check('enable')
        .exists()
        .withMessage('MISSING')
        .isBoolean()
        .withMessage('NOT_A_BOOLEAN'),
    (req, res, next) => {
        validateResult(req, res, next)
    }
]

module.exports = { validateCreateGemEquipment }