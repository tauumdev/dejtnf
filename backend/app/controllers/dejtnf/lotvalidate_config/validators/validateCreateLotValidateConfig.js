const { validateResult } = require('../../../../middleware/utils')
const { check, body } = require('express-validator')

const validateCreateLotValidateConfig = [
    check('equipment_name')
        .exists().withMessage('MISSING_EQUIPMENT_NAME')
        .notEmpty().withMessage('EQUIPMENT_NAME_IS_EMPTY')
        .trim(),
    check('config')
        .exists().withMessage('MISSING_CONFIG')
        .isArray({ min: 1 }).withMessage('CONFIG_MUST_BE_AN_ARRAY'),
    body('config.*.package8digit')
        .exists().withMessage('MISSING_PACKAGE_8DIGIT')
        .isLength({ min: 8, max: 8 }).withMessage('PACKAGE_8DIGIT_MUST_BE_8_CHARACTERS')
        .trim(),
    body('config')
        .custom((config) => {
            const packageSet = new Set()
            for (const item of config) {
                if (packageSet.has(item.package8digit)) {
                    throw new Error(`DUPLICATE_PACKAGE8DIGIT: ${item.package8digit} must be unique`)
                }
                packageSet.add(item.package8digit)
            }
            return true
        }),

    body('config.*.selection_code')
        .exists().withMessage('MISSING_SELECTION_CODE')
        .isLength({ min: 4, max: 4 }).withMessage('SELECTION_CODE_MUST_BE_4_CHARACTERS')
        .matches(/^[01]{4}$/).withMessage('SELECTION_CODE_MUST_BE_4_DIGIT_BINARY')
        .trim(),

    body('config.*.data_with_selection_code')
        .exists().withMessage('MISSING_DATA_WITH_SELECTION_CODE')
        .isArray().withMessage('DATA_WITH_SELECTION_CODE_MUST_BE_AN_ARRAY'),

    body('config.*.data_with_selection_code')
        .custom((data) => {
            const packageSelectionSet = new Set()
            for (const item of data) {
                if (packageSelectionSet.has(item.package_selection_code)) {
                    throw new Error(`DUPLICATE_PACKAGE_SELECTION_CODE: ${item.package_selection_code} must be unique`)
                }
                packageSelectionSet.add(item.package_selection_code)
            }
            return true
        }),

    body('config.*.data_with_selection_code.*.package_selection_code')
        .exists().withMessage('MISSING_PACKAGE_SELECTION_CODE')
        .notEmpty().withMessage('PACKAGE_SELECTION_CODE_IS_EMPTY')
        .trim(),
    body('config.*.data_with_selection_code.*.operation_code')
        .exists().withMessage('MISSING_OPERATION_CODE')
        .notEmpty().withMessage('OPERATION_CODE_IS_EMPTY')
        .trim(),
    body('config.*.data_with_selection_code.*.on_operation')
        .exists().withMessage('MISSING_ON_OPERATION')
        .notEmpty().withMessage('ON_OPERATION_IS_EMPTY')
        .trim(),
    body('config.*.data_with_selection_code.*.validate_type')
        .exists().withMessage('MISSING_VALIDATE_TYPE')
        .isIn(['recipe', 'tool_id']).withMessage('VALIDATE_TYPE_MUST_BE_RECIPE_OR_TOOL_ID')
        .trim(),
    body('config.*.data_with_selection_code.*.recipe_name')
        .exists().withMessage('MISSING_RECIPE_NAME')
        .notEmpty().withMessage('RECIPE_NAME_IS_EMPTY')
        .trim(),
    body('config.*.data_with_selection_code.*.product_name')
        .exists().withMessage('MISSING_PRODUCT_NAME')
        .notEmpty().withMessage('PRODUCT_NAME_IS_EMPTY')
        .trim(),
    body('config.*.data_with_selection_code.*.options')
        .exists().withMessage('MISSING_OPTIONS')
        .isObject().withMessage('OPTIONS_MUST_BE_AN_OBJECT'),
    body('config.*.data_with_selection_code.*.options.use_operation_code')
        .exists().withMessage('MISSING_USE_OPERATION_CODE')
        .isBoolean().withMessage('USE_OPERATION_CODE_MUST_BE_A_BOOLEAN'),
    body('config.*.data_with_selection_code.*.options.use_on_operation')
        .exists().withMessage('MISSING_USE_ON_OPERATION')
        .isBoolean().withMessage('USE_ON_OPERATION_MUST_BE_A_BOOLEAN'),
    body('config.*.data_with_selection_code.*.options.use_lot_hold')
        .exists().withMessage('MISSING_USE_LOT_HOLD')
        .isBoolean().withMessage('USE_LOT_HOLD_MUST_BE_A_BOOLEAN'),
    body('config.*.data_with_selection_code.*.allow_tool_id')
        .exists().withMessage('MISSING_TOOL_ID')
        .isObject().withMessage('TOOL_ID_MUST_BE_AN_OBJECT'),
    (req, res, next) => {
        validateResult(req, res, next);
    }
];

module.exports = { validateCreateLotValidateConfig }
