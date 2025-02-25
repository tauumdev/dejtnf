const GemEquipment = require('../../../../models/dejtnf/gemEquipment');
const { buildErrObject } = require('../../../../middleware/utils')

/**
 * Gets all items from database
 */
const getAllItemsFromDB = () => {
  return new Promise((resolve, reject) => {
    GemEquipment.find(
      {},
      '-updatedAt -createdAt',
      {
        sort: {
          equipment_name: 1
        }
      },
      (err, items) => {
        if (err) {
          return reject(buildErrObject(422, err.message))
        }
        resolve(items)
      }
    )
  })
}

module.exports = { getAllItemsFromDB }