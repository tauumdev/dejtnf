const LotValidateConfig = require('../../../models/dejtnf/lotValidateConfig');
const { updateItem } = require('../../../middleware/db');
const { isIDGood, handleError } = require('../../../middleware/utils');
const { matchedData } = require('express-validator');
const { lotValidateConfigExistExcludingItself } = require('./helpers')

/**
 * Update item function called by route
 * @param {Object} req - request object
 * @param {Object} res - response object
 */

const updateLotValidateConfig = async (req, res) => {
    try {
        req = matchedData(req);
        console.log("receive request:", req);

        const id = await isIDGood(req.id);
        const doesLotValidateConfigExistExcludingItself = await lotValidateConfigExistExcludingItself(id, req.equipment_name)
        if (!doesLotValidateConfigExistExcludingItself) {
            res.status(200).json(await updateItem(id, LotValidateConfig, req));
        }
    } catch (error) {
        handleError(res, error)
    }
}



module.exports = { updateLotValidateConfig }