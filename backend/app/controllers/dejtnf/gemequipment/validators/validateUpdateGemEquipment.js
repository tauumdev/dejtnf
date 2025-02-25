const { validateResult } = require('../../../../middleware/utils/validateResult')
const { check } = require('express-validator')

/**
 * Validates update item request
 */
const validateUpdateGemEquipment = [
    check('_id')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY'),
    check('equipment_name')
        .optional(),
    check('equipment_model')
        .optional(),
    check('address')
        .optional(),
    check('port')
        .optional(),
    check('session_id')
        .optional(),
    check('mode')
        .optional(),
    check('enable')
        .optional(),
    (req, res, next) => {
        validateResult(req, res, next)
    }
]

module.exports = { validateUpdateGemEquipment }