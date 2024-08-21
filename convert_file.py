import sys
from command_processor import CommandProcessor

def process_file(input_file_path, output_file_path):
    """
    Processes an input file, replaces mathematical expressions in each line,
    and writes the results to an output file.

    Parameters
    ----------
    input_file_path : str
        The path to the input file.

    output_file_path : str
        The path to the output file.
    """
    with open(input_file_path, 'r') as input_file:
        content = input_file.read()

    lines = content.splitlines()
    processor = CommandProcessor()
    processed_lines = [processor.process_command(line) for line in lines]

    with open(output_file_path, 'w') as output_file:
        output_file.write("\n".join(processed_lines))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_file.py <input_file> <output_file>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    process_file(input_file_path, output_file_path)
    print(f"Processed file saved to {output_file_path}")

