const express = require('express');
const router = express.Router();
const trimRequest = require('trim-request')

// Existing API endpoints
router.get('/', (req, res) => {
    res.status(200).json({
        message: ["/secsgem", "/validate", "/lotinfo/:id"]
    });
});

// Import Lot info controllers
const { getLotInfo } = require('../controllers/dejtnf/lotinfo')
// Import Lot info Equipments validators
const { validateGetLotInfo } = require('../controllers/dejtnf/lotinfo/validators')

// Endpoint to get lot info
router.get('/lotinfo/:id', validateGetLotInfo, getLotInfo)

// Endpoint to secsgem
router.get('/secsgem', (req, res) => {
    res.status(200).json({
        message: ["post: /secsgem/equipment", "get: /secsgem/equipment:id", "get: /secsgem/equipments", "put: /secsgem/equipment/:id"]
    });
});

// Import Secsgem Equipments controllers
const { createSecsgemEquipment, getSecsgemEquipment, getSecsgemEquipments, deleteSecsgemEquipment, updateSecsgemEquipment } = require('../controllers/dejtnf/secsgem_equipment');
// Import Secsgem Equipments validators
const { validateCreateSecsgemEquipment, validateGetSecsgemEquipment, validateDeleteSecsgemEquipment, validateUpdateSecsgemEquipment } = require('../controllers/dejtnf/secsgem_equipment/validators')

// Endpoint to create a new Secsgem Equipment record
router.post('/secsgem/equipment', trimRequest.all, validateCreateSecsgemEquipment, createSecsgemEquipment);
// Endpoint to get Secsgem Equipment with id records
router.get('/secsgem/equipment/:id', trimRequest.all, validateGetSecsgemEquipment, getSecsgemEquipment);
// Endpoint to get all Secsgem Equipment records
router.get('/secsgem/equipments', trimRequest.all, getSecsgemEquipments);
// Endpoint to delete Secsgem Equipment with id records
router.delete('/secsgem/equipment/:id', validateDeleteSecsgemEquipment, deleteSecsgemEquipment);
// Endpoint to update Secsgem Equipment with id records
router.put('/secsgem/equipment/:id', trimRequest.all, validateUpdateSecsgemEquipment, updateSecsgemEquipment);


// Endpoint validate lot
router.get('/validate', (req, res) => {
    res.status(200).json({
        message: ["post: /validate/config", "get: /validate/config:id", "get: /validate/configs", "delete: /validate/config:id", "put: validate/config:id"]
    });
});

// Import Lot Validate Config controllers and validators
const { createLotValidateConfig, getLotValidateConfig, getLotValidateConfigs, deleteLotValidateConfig, updateLotValidateConfig } = require('../controllers/dejtnf/lotvalidate_config');
const { validateCreateLotValidateConfig, validateGetLotValidateConfig, validateDeleteLotValidateConfig, validateUpdateLotValidateConfig } = require('../controllers/dejtnf/lotvalidate_config/validators');

// Endpoint to create a new Lot Validate Config record
router.post('/validate/config', trimRequest.all, validateCreateLotValidateConfig, createLotValidateConfig);
// Endpoint to get Lot Validate Config with id records
router.get('/validate/config/:id', trimRequest.all, validateGetLotValidateConfig, getLotValidateConfig);
// Endpoint to get all Lot Validate Config records
router.get('/validate/configs', trimRequest.all, getLotValidateConfigs);
// Endpoint to delete Lot Validate Config with id records
router.delete('/validate/config/:id', trimRequest.all, validateDeleteLotValidateConfig, deleteLotValidateConfig);
// Endpoint to update Lot Validate Config with id records
router.put('/validate/config/:id', trimRequest.all, validateUpdateLotValidateConfig, updateLotValidateConfig);

module.exports = router;