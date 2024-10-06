#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# extract surface names for deffered mesh
# ================================


MAGIC_NUMBERS = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    30, 31, 127,
    )


def extract_surface_names_from_lxdf(file_path, chunk_size=1024):
    try:
        with open(file_path, 'rb') as file:
            content = file.read(chunk_size)
            surface_names = []
            index = content.find(b'SURF')
            while index != -1:
                name_start = index + 4  # Start after "SURF"
                name_end = name_start
                while name_end < len(content) and content[name_end] not in MAGIC_NUMBERS:
                    name_end += 1
                surface_name = content[name_start:name_end].decode('utf-8', errors='ignore').strip()
                surface_names.append(surface_name)

                index = content.find(b'SURF', index + 1)

            return surface_names
    except Exception as e:
        print(f"Error reading file: {e}")
        return []


def print_surface_names(file_path):
    surface_names = extract_surface_names_from_lxdf(file_path, chunk_size=4096)
    if surface_names:
        return (surface_names)


def main():
    file_path = r'C:\Users\alexa\OneDrive\Desktop\hmmmm.lxdf'  # Use raw string for Windows path

    list = print_surface_names(file_path)
    print(list)


if __name__ == '__main__':
    main()
