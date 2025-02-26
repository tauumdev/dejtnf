const SecsgemEquipment = require('../../../../models/dejtnf/secsgemEquipment');
const { buildErrObject } = require('../../../../middleware/utils')

/**
 * Checks if a secsgem equipment_name or address already exists in database
 * @param {string} equipment_name - name of item
 * @param {string} address - address of item
 */
const secsgemEquipmentExists = (equipment_name = '', address = '') => {
    return new Promise((resolve, reject) => {
        SecsgemEquipment.findOne(
            {
                $or: [{ equipment_name }, { address }]
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

module.exports = { secsgemEquipmentExists }