const { validateResult } = require('../../../../middleware/utils')
const { check } = require('express-validator')

/**
 * Validates get item request
 */

const validateGetLotInfo = [
    check('id')
        .matches(/^[A-Z]{4,6}\d{3,5}\.\d+$/) // Ensures the format "AAAA0000.0"
        .withMessage('Invalid lot ID format'),
    (req, res, next) => {
        validateResult(req, res, next)
    }
]

module.exports = { validateGetLotInfo }