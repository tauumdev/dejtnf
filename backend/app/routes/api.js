const express = require('express');
const router = express.Router();

// Existing API endpoints
router.get('/', (req, res) => {
    res.status(200).json({
        message: 'Dejtnf API v1.0'
    });
});

router.get('/help', (req, res) => {
    res.status(200).json({
        message: 'Help for the Dejtnf API! You can find the documentation at [link].'
    });
});

// Import Gem Equipments controllers and validators
const { createGemEquipment } = require('../controllers/dejtnf/gemEquipment/createGemEquipment');
const { getGemEquipment } = require('../controllers/dejtnf/gemEquipment/getGemEquipment');
const { getGemEquipments } = require('../controllers/dejtnf/gemEquipment/getGemEquipments');
const { updateGemEquipment } = require('../controllers/dejtnf/gemEquipment/updateGemEquipment');
const { validateCreateGemEquipment } = require('../controllers/dejtnf/gemEquipment/validators/validateCreateGemEquipment');
const { validateUpdateGemEquipment } = require('../controllers/dejtnf/gemEquipment/validators/validateUpdateGemEquipment');

// Endpoint to create a new Gem Equipment record
router.post('/gemequipment', validateCreateGemEquipment, createGemEquipment);

// Endpoint to retrieve a Gem Equipment record
router.get('/gemequipment/:id', getGemEquipment);

// Endpoint to retrieve Gem Equipment records with pagination
router.get('/gemequipments', getGemEquipments);

// Endpoint to update a Gem Equipment record
router.put('/gemequipment/:id', validateUpdateGemEquipment, updateGemEquipment);



// Import ValidateLot controllers and validators
const { createValidatelot } = require('../controllers/dejtnf/validatelot/createValidatelot');
const { getValidatelots } = require('../controllers/dejtnf/validatelot/getValidatelots');
const { updateValidatelot } = require('../controllers/dejtnf/validatelot/updateValidatelot');
const { validateCreateValidatelot } = require('../controllers/dejtnf/validatelot/validators/validateCreateValidatelot');
const { validateUpdateValidatelot } = require('../controllers/dejtnf/validatelot/validators/validateUpdateValidatelot');

// Endpoint to create a new ValidateLot record
router.post('/validatelot', validateCreateValidatelot, createValidatelot);

// Endpoint to retrieve ValidateLot records with pagination
router.get('/validatelots', getValidatelots);

// Endpoint to update a ValidateLot record
router.put('/validatelot/:id', validateUpdateValidatelot, updateValidatelot);

module.exports = router;