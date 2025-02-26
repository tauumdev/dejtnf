const LotValidateConfig = require('../../../../models/dejtnf/lotValidateConfig');
const { buildErrObject } = require('../../../../middleware/utils');

/**
 * Updates an item by id and equipment_name excluding itself 
 * @param {string} id - id of item
 * @param {Object} equipment_name - request object
 */

const lotValidateConfigExistExcludingItself = (id = '', equipment_name = '') => {
    return new Promise((resolve, reject) => {
        LotValidateConfig.findOne(
            {
                equipment_name,
                _id: {
                    $ne: id
                }
            },
            (err, item) => {
                if (err) {
                    return reject(buildErrObject(422, err.message))
                }

                if (item) {
                    return reject(buildErrObject(422, 'LOT_VALIDATE_CONFIG_ALREADY_EXISTS'))
                }

                resolve(false)
            }
        )
    })
}

module.exports = { lotValidateConfigExistExcludingItself }