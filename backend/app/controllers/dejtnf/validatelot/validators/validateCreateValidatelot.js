const { check } = require('express-validator');
// Adjust the path to your validateResult middleware as needed
const { validateResult } = require('../../../../middleware/utils/validateResult');

const validateCreateValidatelot = [
    check('equipment_name')
        .exists().withMessage('MISSING')
        .not().isEmpty().withMessage('IS_EMPTY'),
    // You can add more validations for the "config" array and nested fields if needed
    (req, res, next) => {
        validateResult(req, res, next);
    }
];

module.exports = { validateCreateValidatelot };