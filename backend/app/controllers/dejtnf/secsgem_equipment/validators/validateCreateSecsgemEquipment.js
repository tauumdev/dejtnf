const { validateResult } = require('../../../../middleware/utils')
const { check } = require('express-validator')


const validateCreateSecsgemEquipment = [
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

module.exports = { validateCreateSecsgemEquipment }

