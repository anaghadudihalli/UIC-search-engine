from spellchecker import SpellChecker


def spell_check(original_query):
    query = original_query.split()
    spell = SpellChecker()
    misspelled = spell.unknown(query)
    updated_query = ''
    for word in query:
        if word in misspelled:
            updated_query += spell.correction(word) + ' '
        else:
            updated_query += word + ' '
    return original_query, updated_query


def main():
    pass


if __name__ == '__main__':
    main()
