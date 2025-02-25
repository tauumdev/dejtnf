const mongoose = require('mongoose')
const mongoosePaginate = require('mongoose-paginate-v2')
const validator = require('validator')

// {
//     "equipment_name": "TNF-70",
//     "config": [
//         {
//             "package8digit": "SOICW16U",
//             "selection_code": "1000",
//             "data_with_selection_code": [
//                 {
//                     "package_selection_code": "SOICW16U",
//                     "operation_code": "TNF",
//                     "on_operation": "TNF",
//                     "validate_type": "recipe",
//                     "recipe_name": "SOICW 16L 7x18",
//                     "product_name": "SOICW 16L 7x18",
//                     "options": {
//                         "use_operation_code": true,
//                         "use_on_operation": true,
//                         "use_lot_hold": true
//                     },
//                     "tool_id": {
//                         "tool_1": [
//                             "0001",
//                             "0002"
//                         ],
//                         "tool_2": [
//                             "0003"
//                         ],
//                         "tool_3": [
//                             "0004",
//                             "0005"
//                         ],
//                         "tool_4": [
//                             "0006",
//                             "0007",
//                             "0008"
//                         ]
//                     }
//                 }
//             ]
//         }
//     ]
// }

const validateLotSchema = new mongoose.Schema(
    {
        equipment_name: {
            type: String,
            required: true
        },
        config: [
            {
                package8digit: { type: String, required: true },
                selection_code: { type: String, required: true },
                data_with_selection_code: [
                    {
                        package_selection_code: { type: String, required: true },
                        operation_code: { type: String, required: true },
                        on_operation: { type: String, required: true },
                        validate_type: { type: String, required: true },
                        recipe_name: { type: String, required: true },
                        product_name: { type: String, required: true },
                        options: {
                            use_operation_code: { type: Boolean, required: true },
                            use_on_operation: { type: Boolean, required: true },
                            use_lot_hold: { type: Boolean, required: true }
                        },
                        tool_id: {
                            tool_1: { type: Array },
                            tool_2: { type: Array },
                            tool_3: { type: Array },
                            tool_4: { type: Array }
                        }
                    }
                ]
            }
        ],
    },
    {
        versionKey: false,
        timestamps: true
    }
)
validateLotSchema.plugin(mongoosePaginate)
module.exports = mongoose.model('ValidateLot', validateLotSchema)