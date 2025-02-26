const mongoose = require('mongoose')
const mongoosePaginate = require('mongoose-paginate-v2')
const validator = require('validator')

const secsgemEquipmentSchema = new mongoose.Schema(
    {
        equipment_name: {
            type: String,
            required: true
        },
        equipment_model: {
            type: String,
            required: true
        },
        address: {
            type: String,
            validate: {
                validator: validator.isIP,
                message: 'ADDRESS_IS_NOT_VALID'
            },
            required: true
        },
        port: {
            type: Number,
            required: true
        },
        session_id: {
            type: Number,
            required: true
        },
        mode: {
            type: String,
            enum: ['ACTIVE', 'PASSIVE'],
            default: 'ACTIVE',
            required: true
        },
        enable: {
            type: Boolean,
            required: true
        }
    },
    {
        versionKey: false,
        timestamps: true
    }
)
secsgemEquipmentSchema.plugin(mongoosePaginate)
module.exports = mongoose.model('SecsgemEquipmentList', secsgemEquipmentSchema)