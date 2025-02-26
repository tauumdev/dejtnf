// const mongoose = require('mongoose');
// const mongoosePaginate = require('mongoose-paginate-v2');

// const validateConfigSchema = new mongoose.Schema({
//     equipment_name: {
//         type: String,
//         required: true
//     },
//     config: [
//         {
//             package8digit: {
//                 type: String,
//                 required: true
//             },
//             selection_code: {
//                 type: String,
//                 required: true
//             },
//             data_with_selection_code: [
//                 {
//                     package_selection_code: {
//                         type: String,
//                         required: true
//                     },
//                     operation_code: {
//                         type: String,
//                         required: true
//                     },
//                     on_operation: {
//                         type: String,
//                         required: true
//                     },
//                     validate_type: {
//                         type: String,
//                         required: true
//                     },
//                     recipe_name: {
//                         type: String,
//                         required: true
//                     },
//                     product_name: {
//                         type: String,
//                         required: true
//                     },
//                     options: {
//                         use_operation_code: {
//                             type: Boolean,
//                             required: true
//                         },
//                         use_on_operation: {
//                             type: Boolean,
//                             required: true
//                         },
//                         use_lot_hold: {
//                             type: Boolean,
//                             required: true
//                         }
//                     },
//                     tool_id: {
//                         tool_1: {
//                             type: [String],
//                             required: true
//                         },
//                         tool_2: {
//                             type: [String],
//                             required: true
//                         },
//                         tool_3: {
//                             type: [String],
//                             required: true
//                         },
//                         tool_4: {
//                             type: [String],
//                             required: true
//                         }
//                     }
//                 }
//             ]
//         }
//     ]
// }, {
//     versionKey: false,
//     timestamps: true
// });

// validateConfigSchema.plugin(mongoosePaginate);

// module.exports = mongoose.model('ValidateConfig', validateConfigSchema);

const mongoose = require('mongoose')
const mongoosePaginate = require('mongoose-paginate-v2')
// const validator = require('validator')

// Tool Schema
const ToolSchema = new mongoose.Schema({
    tool_1: { type: [String], default: [] },
    tool_2: { type: [String], default: [] },
    tool_3: { type: [String], default: [] },
    tool_4: { type: [String], default: [] },
}, { _id: false });

// Data With Selection Code Schema
const DataWithSelectionCodeSchema = new mongoose.Schema({
    package_selection_code: { type: String, required: true, trim: true },
    operation_code: { type: String, required: true, trim: true },
    on_operation: { type: String, required: true, trim: true },
    validate_type: { type: String, required: true, trim: true },
    recipe_name: { type: String, required: true, trim: true },
    product_name: { type: String, required: true, trim: true },
    options: {
        use_operation_code: { type: Boolean, required: true, default: false },
        use_on_operation: { type: Boolean, required: true, default: false },
        use_lot_hold: { type: Boolean, required: true, default: false },
    },
    tool_id: ToolSchema,
}, { _id: false });

// Config Schema
const ConfigSchema = new mongoose.Schema({
    package8digit: {
        type: String,
        required: true,
        trim: true
    },
    selection_code: { type: String, required: true, trim: true },
    data_with_selection_code: [DataWithSelectionCodeSchema],
}, { _id: false });

// Main Equipment Schema
const validateConfigSchema = new mongoose.Schema({
    equipment_name: { type: String, required: true },
    config: [ConfigSchema],
}, { timestamps: true });

validateConfigSchema.plugin(mongoosePaginate);

module.exports = mongoose.model('ValidateConfig', validateConfigSchema);