const GemEquipment = require('../../../../models/dejtnf/gemEquipment');
const { buildErrObject } = require('../../../../middleware/utils')

/**
 * Checks if a gem equipment_name and equipment_ip already exists in database
 * @param {string} equipment_name - name of item
 * @param {string} equipment_ip - ip of item
 */
const gemEquipmentExists = (equipment_name = '', equipment_ip = '') => {
    return new Promise((resolve, reject) => {
        GemEquipment.findOne(
            {
                equipment_name,
                equipment_ip
            },
            (err, item) => {
                if (err) {
                    return reject(buildErrObject(422, err.message))
                }

                if (item) {
                    return reject(buildErrObject(422, 'GEM_EQUIPMENT_ALREADY_EXISTS'))
                }
                resolve(false)
            }
        )
    })
}
module.exports = { gemEquipmentExists }