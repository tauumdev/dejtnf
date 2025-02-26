const { createLotValidateConfig } = require('./createLotValidateConfig');
const { getLotValidateConfig } = require('./getLotValidateConfig');
const { getLotValidateConfigs } = require('./getLotValidateConfigs')
const { deleteLotValidateConfig } = require('./deleteValidateConfig');
const { updateLotValidateConfig } = require('./updateLotValidateConfig')
module.exports = {
    createLotValidateConfig,
    getLotValidateConfig,
    getLotValidateConfigs,
    deleteLotValidateConfig,
    updateLotValidateConfig
};