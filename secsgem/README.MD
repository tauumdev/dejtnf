<!-- Validate -->
from data
- config
    - equipment_name
    - data
        - type as list
            - package8digit
                - selection_code
                - use_operation_code
                - use_on_operation
                - use_lot_hold
                - data_with_selection_code
                    - type as list
                        - package_code
                        - operation_code
                        - on_operation
                        - type_validate
                        - recipe_name
                        - product_name

from machine
prepare parameter

equipment_name = TNF-61
recipe_name = 48L TQFP 7x7
package15digit = LQFA048MS2GNSDM
package8digit = LQFA048M
operation_code = TNF
on_operation = TNF


i need to read data config to compare data from machine.
can you give me structure or step to compare.





cfg = {
	"data": [
		{
			"equipment_name": "TNF-61",
			"data": [
				{
					"package8digit": "LQFA048M",
					"selection_code": "1111",
					"use_operation_code": true,
					"use_on_operation": true,
					"use_lot_hold": false,
					"data_with_selection_code": [
						{
							"package_selection_code": "LQFA048MS2GNSDM",
							"operation_code": "TNF",
							"on_operation": "TNF",
							"type_validate": "recipe",
							"recipe_name": "48L TQFP 7x7",
							"product_name": "TQFP48L_7x7"
						},
						{
							"package_selection_code": "LQFA048MS2GNA0M",
							"operation_code": "TNF",
							"on_operation": "TNF",
							"type_validate": "recipe",
							"recipe_name": "48L TQFP 7x7 A0",
							"product_name": "TQFP48L_7x7_A0"
						}
					]
				},
				{
					"package8digit": "LQFP032M",
					"selection_code": "1011",
					"use_operation_code": true,
					"use_on_operation": false,
					"use_lot_hold": true,
					"data_with_selection_code": [
						{
							"package_selection_code": "LQFP032MSDM",
							"operation_code": "TNF",
							"on_operation": "TNF",
							"type_validate": "recipe",
							"recipe_name": "32L TQFP 7x7",
							"product_name": "TQFP32L_7x7"
						}
					]
				},
				{
					"package8digit": "LQFP064M",
					"selection_code": "1000",
					"use_operation_code": true,
					"use_on_operation": false,
					"use_lot_hold": true,
					"data_with_selection_code": [
						{
							"package_selection_code": "LQFP064M",
							"operation_code": "TNF",
							"on_operation": "TNF",
							"type_validate": "recipe",
							"recipe_name": "64L TQFP 7x7",
							"product_name": "TQFP64L_7x7"
						}
					]
				}
			]
		},
		{
			"equipment_name": "TNF-62",
			"data": [
				{
					"package8digit": "LQFA048M",
					"selection_code": "1111",
					"use_operation_code": true,
					"use_on_operation": true,
					"use_lot_hold": false,
					"data_with_selection_code": [
						{
							"package_selection_code": "LQFA048MS2GNSDM",
							"operation_code": "TNF",
							"on_operation": "TNF",
							"type_validate": "recipe",
							"recipe_name": "48L TQFP 7x7",
							"product_name": "TQFP48L_7x7"
						}
					]
				}
			]
		}
	]
}

validate lot

- machine data 
    - equipment_name
    - recipe_name
    - lot_id
- data_lot
    - lot_id
    - package_code15digit
    - lot_status
    - operation_code
    - on_operation

- prepare parameter
    - equipment_name
    - recipe_name
    - lot_id
    - package_code15digit
    - package_code8digit
    - lot_status
    - operation_code
    - on_operation

- read config data by equipment_name and package_code8digit
    - data
        - package8digit
            - selection_code
            - use_operation_code
            - use_on_operation
            - use_lot_hold
            - data_with_selection_code
                - type as list
                    - package_selection_code
                    - operation_code
                    - on_operation
                    - type_validate
                    - recipe_name
                    - product_name

design concept to validate


