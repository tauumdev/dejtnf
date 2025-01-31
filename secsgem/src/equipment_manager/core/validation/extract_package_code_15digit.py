def extract_package_code(package, selection_code: str = "1000"):
    """
    Extracts a package code based on a 15-digit code and a 4-digit selection code.
    Args:
        package: A 15-character package code.
        selection_code: A 4-character binary selection code.
    Returns:
        A package code based on the selection code.
    Binary selection code:
        - 1st digit: Use 1-8    (package)
        - 2nd digit: Use 12     (exposed pad)    
        - 3rd digit: Use 13-14  (depopulate pin)
        - 4th digit: Use 15     (plate type)
    """

    # Ensure the package code is exactly 15 characters long
    if len(package) != 15:
        return "Invalid package code length. Should be 15 characters."

    # Ensure the selection code is exactly 4 characters long
    if len(selection_code) != 4 or not set(selection_code).issubset({'0', '1'}):
        return "Invalid selection code. Should be 4 binary digits."

    # Extract the package code based on the selection code
    use_1_8 = selection_code[0] == '1'
    use_12 = selection_code[1] == '1'
    use_13_14 = selection_code[2] == '1'
    use_15 = selection_code[3] == '1'

    part_1_8 = package[:8] if use_1_8 else ""
    part_12 = package[11] if use_12 else ""
    part_13_14 = package[12:14] if use_13_14 else ""
    part_15 = package[14] if use_15 else ""

    # print("code result: ", part_1_8 + part_12 + part_13_14 + part_15)
    return part_1_8 + part_12 + part_13_14 + part_15

    # # Sample usage
    # package_code = "SOIC-08USDPNSDP"
    # selection_code = "1001"
    # result = extract_package_code(package_code, selection_code)
    # print(result)
