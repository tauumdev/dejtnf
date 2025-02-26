const LotValidateConfig = require('../../../models/dejtnf/lotValidateConfig');
const { createItem } = require('../../../middleware/db');
const { handleError } = require('../../../middleware/utils');
const { matchedData } = require('express-validator');
const { lotValidateConfigExists } = require('./helpers');

/**
 * Create item function called by route
 * @param {Object} req - request object
 * @param {Object} res - response object
 */
const createLotValidateConfig = async (req, res) => {
    try {
        // console.log('Request received:', req.body); // Add logging
        req = matchedData(req);
        const doesLotValidateConfigExists = await lotValidateConfigExists(req.equipment_name);
        if (!doesLotValidateConfigExists) {
            // const newItem = await createItem(req, LotValidateConfig);
            // console.log('New item created:', newItem); // Add logging
            res.status(201).json(await createItem(req, LotValidateConfig));
        } else {
            // console.log('Item already exists'); // Add logging
            res.status(409).json({ message: 'Item already exists' });
        }
    } catch (error) {
        // console.error('Error creating item:', error); // Add logging
        handleError(res, error);
    }
};

module.exports = { createLotValidateConfig };

// const createLotValidateConfig = async (req, res) => {
//     try {
//         req = matchedData(req);
//         const doesLotValidateConfigExists = await lotValidateConfigExists(req.equipment_name);
//         if (!doesLotValidateConfigExists) {
//             res.status(201).json(await createItem(req, LotValidateConfig));
//         }
//     } catch (error) {
//         handleError(res, error);
//     }
// };
