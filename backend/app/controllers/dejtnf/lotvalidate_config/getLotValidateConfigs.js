const LotValidateConfig = require('../../../models/dejtnf/lotValidateConfig');
const { checkQueryString, getItems } = require('../../../middleware/db');
const { handleError } = require('../../../middleware/utils');

/**
 * Get items function called by route
 * @param {Object} req - request object
 * @param {Object} res - response object
 */
const getLotValidateConfigs = async (req, res) => {
    try {
        const query = await checkQueryString(req.query);
        res.status(200).json(await getItems(req, LotValidateConfig, query));
    } catch (error) {
        handleError(res, error);
    }
}

module.exports = { getLotValidateConfigs };