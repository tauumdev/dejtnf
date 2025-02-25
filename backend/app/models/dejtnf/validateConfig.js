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

EquipmentSchema.plugin(mongoosePaginate);

module.exports = mongoose.model('ValidateConfig', validateConfigSchema);