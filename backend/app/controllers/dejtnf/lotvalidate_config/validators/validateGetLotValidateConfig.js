const { validateResult } = require('../../../../middleware/utils')
const { check } = require('express-validator')

/**
 * Validates get item request
 */
const validateGetLotValidateConfig = [
    check('id')
        .exists()
        .withMessage('MISSING')
        .not()
        .isEmpty()
        .withMessage('IS_EMPTY'),
    (req, res, next) => {
        validateResult(req, res, next)
    }
]

module.exports = { validateGetLotValidateConfig }