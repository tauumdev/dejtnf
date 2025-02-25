const { gemEquipmentExists } = require('./gemEquipmentExists');
const { gemExistsExcludingItself } = require('./gemEquipmentExcludingItself')
const { getAllItemsFromDB } = require('./getAllItemsFromDB');

module.exports = {
    gemEquipmentExists,
    gemExistsExcludingItself,
    getAllItemsFromDB
}