const SecsgemEquipment = require('../../../../models/dejtnf/secsgemEquipment');
const { buildErrObject } = require('../../../../middleware/utils');

/**
 * Updates an item by id and equipment_name and address excluding itself
 * @param {string} id - id of item
 * @param {Object} equipment_name - request object
 * @param {Object} address - request object
 */

const secsgemEquipmentExistsExcludingItself = (id = '', equipment_name = '', address = '') => {
    return new Promise((resolve, reject) => {
        SecsgemEquipment.findOne(
            {
                $or: [{ equipment_name }, { address }],
                _id: {
                    $ne: id
                }
            },
            (err, item) => {
                if (err) {
                    return reject(buildErrObject(422, err.message))
                }

                if (item) {
                    return reject(buildErrObject(422, 'SECSGEM_EQUIPMENT_ALREADY_EXISTS'))
                }

                resolve(false)
            }
        )
    })
}

module.exports = { secsgemEquipmentExistsExcludingItself }