import zipfile
import io


def bytes_to_zip(zip_bytes, output_filename):
    """Save ZIP bytes to a file."""
    with open(output_filename, "wb") as f:
        f.write(zip_bytes)


def zip_to_bytes(zip_filename):
    """Read a ZIP file and return its bytes."""
    with open(zip_filename, "rb") as f:
        return f.read()


def extract_zip_from_bytes(zip_bytes, extract_to="extracted_files"):
    """Extract files from ZIP bytes."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
        zip_file.extractall(extract_to)
        return zip_file.namelist()


def create_zip_from_bytes(files, output_filename):
    """
    Create a ZIP file from a dictionary of {filename: file_bytes}.
    Example: {"test.txt": b"Hello, World!"}
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, file_bytes in files.items():
            zip_file.writestr(filename, file_bytes)

    zip_data = zip_buffer.getvalue()
    bytes_to_zip(zip_data, output_filename)  # Save to file
    return zip_data  # Return ZIP bytes

# # Example usage:
# if __name__ == "__main__":
#     # Create ZIP from bytes
#     zip_content = create_zip_from_bytes({"example.txt": b"Hello, ZIP!"}, "test.zip")

#     # Read ZIP file as bytes
#     zip_bytes = zip_to_bytes("test.zip")

#     # Extract ZIP bytes
#     extracted_files = extract_zip_from_bytes(zip_bytes)
#     print("Extracted files:", extracted_files)
