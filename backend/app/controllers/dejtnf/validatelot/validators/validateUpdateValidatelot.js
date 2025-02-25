const { check } = require('express-validator');
const { validateResult } = require('../../../../middleware/utils/validateResult');

const validateUpdateValidatelot = [
    check('equipment_name')
        .optional()
        .not().isEmpty().withMessage('equipment_name cannot be empty'),
    check('config')
        .optional()
        .isArray().withMessage('config must be an array'),
    (req, res, next) => {
        validateResult(req, res, next);
    }
];

module.exports = { validateUpdateValidatelot };