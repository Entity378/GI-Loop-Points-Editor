import struct

def find_signed_int_in_file(file_path, target_value):
    positions = []
    try:
        with open(file_path, 'rb') as file:
            data = file.read()
            for i in range(len(data) - 3):
                chunk = data[i:i+4]
                value = struct.unpack('<i', chunk)[0]
                if value == target_value:
                    positions.append(i)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")
    
    return positions

def remove_alternate_starting_from_first(lst):
    return [lst[i] for i in range(len(lst)) if i % 2 != 0]

def zero_bytes_in_range(file_path, offsets):
    try:
        with open(file_path, 'r+b') as file:
            for offset in offsets:
                start = offset + 4
                end = offset + 31
                length = end - start + 1
                file.seek(start)
                file.write(b'\x00' * length)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")

def write_double_at_offsets_total_length(file_path, offsets, double_value):
    try:
        with open(file_path, 'r+b') as file:
            for offset in offsets:
                target_position = offset + 32
                file.seek(target_position)
                file.write(struct.pack('<d', double_value))
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")

def write_doubles_after_hex_string(file_path, offsets, double_value):
    hex_string_to_find = b'\x48\xD6\xBB\x5B'
    
    try:
        with open(file_path, 'r+b') as file:
            for offset in offsets:
                file.seek(offset)
                found = False

                while True:
                    byte = file.read(1)
                    if not byte:
                        break
                    
                    if byte == hex_string_to_find[0:1]:
                        potential_match = byte + file.read(len(hex_string_to_find) - 1)

                        if potential_match == hex_string_to_find:
                            found = True
                            position_after_string = file.tell()
                            
                            file.seek(position_after_string)
                            file.write(struct.pack('<d', double_value))

                            position_before_string = position_after_string - len(hex_string_to_find) - 28
                            file.seek(position_before_string)
                            file.write(struct.pack('<d', double_value))
                            
                            print(f"Overwritten values ​​with offset: {position_after_string} and {position_before_string}.")
                            break
                        
                        file.seek(file.tell() - len(potential_match) + 1)
                
                if not found:
                    print(f"String 'HÖ»[' not found starting from offset {offset}.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    file_path = input("Enter the file path: ").strip()
    target_value = int(input("Enter the song ID to search for: ").strip())
    double_value = float(input("Enter the length/duration of your song (IN MILLISECONDS!!!): ").strip())
    positions = find_signed_int_in_file(file_path, target_value)  
    if positions:
        filtered_positions = remove_alternate_starting_from_first(positions)
        print(f"Offsets: {filtered_positions}")
        zero_bytes_in_range(file_path, filtered_positions)
        write_double_at_offsets_total_length(file_path, filtered_positions, double_value)
        write_doubles_after_hex_string(file_path, filtered_positions, double_value)
        print(f"Loop-points changed correctly.")
    else:
        print("Song ID not found.")