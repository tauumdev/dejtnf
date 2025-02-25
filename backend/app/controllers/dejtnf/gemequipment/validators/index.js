const { validateCreateGemEquipment } = require('./validateCreateGemEquipment');
const { validateDeleteGemEquipment } = require('./validateDeleteGemEquipment');
const { validateGetGemEquipment } = require('./validateGetGemEquipment');
const { validateUpdateGemEquipment } = require('./validateUpdateGemEquipment');

module.exports = {
    validateCreateGemEquipment,
    validateDeleteGemEquipment,
    validateGetGemEquipment,
    validateUpdateGemEquipment
}