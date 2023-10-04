import regex


def get_codes_as_list():
    with open('add_codes.txt', 'r', encoding='utf-8') as f:
        data = f.read()
        # extract codes from text, the codes are 6 ascii characters after the word "كود"
        codes = regex.findall(r'كود\s(\w{6})', data)
        return codes


def append_codes_to_file(codes):
    # append codes to codes.txt file and remove duplicates
    old_codes = []
    with open('codes.txt', 'r', encoding='utf-8') as f:
        old_codes = f.readlines()
        old_codes = [code.strip().replace('\n', '') for code in old_codes]

    new_codes = old_codes
    for code in codes:
        if code in new_codes:
            continue
        new_codes.append(code)

    with open('codes.txt', 'w', encoding='utf-8') as f:
        for code in new_codes:
            f.write(code + '\n')


def main():
    codes = get_codes_as_list()
    append_codes_to_file(codes)
    print(f'{len(codes)} codes added to codes.txt file.')


if __name__ == '__main__':
    main()
    