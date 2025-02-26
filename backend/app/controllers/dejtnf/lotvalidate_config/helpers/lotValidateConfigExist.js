const LotValidateConfig = require('../../../../models/dejtnf/lotValidateConfig');
const { buildErrObject } = require('../../../../middleware/utils')


/**
 * Checks if a lot validate config with the given equipment_name already exists in the database
 * @param {string} equipment_name - name of the equipment
 */
const lotValidateConfigExists = (equipment_name = '') => {
    return new Promise((resolve, reject) => {
        LotValidateConfig.findOne({ equipment_name }, (err, item) => {
            if (err) {
                return reject(buildErrObject(422, err.message));
            }
            if (item) {
                return resolve(true); // Item exists
            }
            resolve(false); // Item does not exist
        });
    });
};

module.exports = { lotValidateConfigExists }