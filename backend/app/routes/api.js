const express = require('express');
const router = express.Router();
const trimRequest = require('trim-request')

// Existing API endpoints
router.get('/', (req, res) => {
    res.status(200).json({
        message: ['/secsgem']
    });
});

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


router.get('/lotvalidate', (req, res) => {
    res.status(200).json({
        message: ["post: /validate/config"]
    });
});
// Import Lot Validate Config controllers and validators
const { createLotValidateConfig, getLotValidateConfig, getLotValidateConfigs, deleteLotValidateConfig, updateLotValidateConfig } = require('../controllers/dejtnf/lotvalidate_config');
const { validateCreateLotValidateConfig, validateGetLotValidateConfig, validateDeleteLotValidateConfig, validateUpdateLotValidateConfig } = require('../controllers/dejtnf/lotvalidate_config/validators');

// Endpoint to create a new Lot Validate Config record
router.post('/lotvalidate/config', trimRequest.all, validateCreateLotValidateConfig, createLotValidateConfig);
// Endpoint to get Lot Validate Config with id records
router.get('/lotvalidate/config/:id', trimRequest.all, validateGetLotValidateConfig, getLotValidateConfig);
// Endpoint to get all Lot Validate Config records
router.get('/lotvalidate/configs', trimRequest.all, getLotValidateConfigs);
// Endpoint to delete Lot Validate Config with id records
router.delete('/lotvalidate/config/:id', trimRequest.all, validateDeleteLotValidateConfig, deleteLotValidateConfig);
// Endpoint to update Lot Validate Config with id records
router.put('/lotvalidate/config/:id', trimRequest.all, validateUpdateLotValidateConfig, updateLotValidateConfig);

module.exports = router;