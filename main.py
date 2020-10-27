import csv
import datetime
import random as rand
from operator import itemgetter


NUMBER_OF_BOOKS = 15000
NUMBER_OF_CATEGORIES = 30
NUMBER_OF_AUTHORS = 4000
NUMBER_OF_LIBRARIES = 20
NUMBER_OF_PIECES = 50000
NUMBER_OF_RENTALS = 120000
NUMBER_OF_READERS = 15000


def save_to_csv(data, filename, header):
    with open(f"{filename}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        data = header + data
        writer.writerows(data)


def generate_rows(list_of_ids, list_of_foreign_keys, min_number_of_new_rows, max_number_of_new_rows):
    result = []
    for i in list_of_ids:
        number_of_rows_to_insert = rand.randint(min_number_of_new_rows, max_number_of_new_rows)
        unique_foreign_keys_list = rand.sample(list_of_foreign_keys, number_of_rows_to_insert)
        result = result + [[i, unique_foreign_keys_list[j]] for j in range(0, number_of_rows_to_insert)]
    return result


def generate_single_rows(list_of_ids, number_of_foreign_keys):
    return list(map(lambda x: [rand.randint(1, number_of_foreign_keys), x], list_of_ids))


def generate_sets_of_ids(first_group_percent, second_group_percent, third_group_percent, group_size):
    first_group_size = int(first_group_percent * group_size)
    second_group_size = int(second_group_percent * group_size)
    third_group_size = int(third_group_percent * group_size)

    # Create sets of ids for each group
    all_keys = rand.sample(range(1, group_size + 1), group_size)
    first_group_keys = all_keys[0:first_group_size]
    second_group_keys = all_keys[first_group_size:first_group_size + second_group_size]
    third_group_keys = \
        all_keys[first_group_size + second_group_size:first_group_size + second_group_size + third_group_size]

    return first_group_keys, second_group_keys, third_group_keys


def generate_relation(first_group_percent, first_group_min, first_group_max, first_group_foreign_key_percent,
                      second_group_percent, second_group_min, second_group_max, second_group_foreign_key_percent,
                      third_group_percent, third_group_min, third_group_max, third_group_foreign_key_percent,
                      group_size, foreign_group_size, are_all_records_related):
    """
    :param first_group_percent: Percent of total number of rows that should be in first group.
    :param first_group_min: Min number of relations to rows from first group.
    :param first_group_max: Max number of relations to rows from first group.
    :param first_group_foreign_key_percent: Percent of foreign keys allocated to this group.
    :param second_group_percent: Percent of total number of rows that should be in second group.
    :param second_group_min: Min number of relations to rows from second group.
    :param second_group_max: Max number of relations to rows from second group.
    :param second_group_foreign_key_percent: Percent of foreign keys allocated to this group.
    :param third_group_percent: Percent of total number of rows that should be in third group.
    :param third_group_min: Min number of relations to rows from third group.
    :param third_group_max: Max number of relations to rows from third group.
    :param third_group_foreign_key_percent: Percent of foreign keys allocated to this group.
    :param group_size: Number of rows in main table.
    :param foreign_group_size: Number of rows in related table.
    :param are_all_records_related:
    """
    result = []
    first_group_keys, second_group_keys, third_group_keys = \
        generate_sets_of_ids(first_group_percent, second_group_percent, third_group_percent, group_size)

    first_group_foreign_keys, second_group_foreign_keys, third_group_foreign_keys = \
        generate_sets_of_ids(first_group_foreign_key_percent, second_group_foreign_key_percent,
                             third_group_foreign_key_percent, foreign_group_size)

    # Add relation for each foreign key if needed
    if are_all_records_related:
        result += list(zip(first_group_keys[0:foreign_group_size],
                           rand.sample(list(range(1, foreign_group_size + 1)), foreign_group_size)))
        # Remove used keys
        first_group_keys = first_group_keys[foreign_group_size: int(group_size * first_group_percent)]

    # Generate rows
    result += generate_rows(first_group_keys, first_group_foreign_keys, first_group_min, first_group_max)
    result += generate_rows(second_group_keys, second_group_foreign_keys, second_group_min, second_group_max)
    result += generate_rows(third_group_keys, third_group_foreign_keys, third_group_min, third_group_max)

    return result


def generate_authors(result):
    books_with_authors = list(dict.fromkeys(list(map(lambda x: x[1], result))))
    books_without_authors = list(range(1, NUMBER_OF_BOOKS + 1))
    books_without_authors = list(set(books_without_authors) - set(books_with_authors))
    result += generate_single_rows(books_without_authors, NUMBER_OF_AUTHORS)

    return result


def generate_pieces(library_piece, book_piece):
    result = list(zip(library_piece, book_piece))
    result = list(map(lambda x: [x[0][0], x[0][1], x[1][0], x[1][1]], result))
    result = list(map(lambda x: [0, rand.randint(0, 1), rand.randint(1, 3), 'Bad', x[3], x[1]], result))

    return result


def generate_rentals(first_list, second_list):
    result = list(zip(first_list, second_list))
    result = list(map(lambda x: [x[1][1], x[0][1]], result))

    result = sorted(result, key=itemgetter(0))

    for i in range(0, len(result)):
        if i == 0 or result[i][0] != result[i - 1][4]:
            date_start = datetime.date(2010, 1, 1) + datetime.timedelta(days=rand.randint(0, 150))
        else:
            date_start = result[i - 1][1] + datetime.timedelta(days=rand.randint(0, 150))
        number_of_renewals = rand.randint(0, 3)
        deadline = date_start + datetime.timedelta(days=(number_of_renewals + 1) * 14)
        date_end = deadline + datetime.timedelta(days=rand.randint(-10, 10))
        result[i] = [date_start, date_end, deadline, number_of_renewals] + result[i]

    return result


if __name__ == '__main__':
    save_to_csv(generate_rentals(generate_relation(first_group_percent=0.1,
                                                   first_group_min=1,
                                                   first_group_max=1,
                                                   first_group_foreign_key_percent=0.4,
                                                   second_group_percent=0.5,
                                                   second_group_min=1,
                                                   second_group_max=1,
                                                   second_group_foreign_key_percent=0.4,
                                                   third_group_percent=0.4,
                                                   third_group_min=1,
                                                   third_group_max=1,
                                                   third_group_foreign_key_percent=0.2,
                                                   group_size=NUMBER_OF_RENTALS,
                                                   foreign_group_size=NUMBER_OF_READERS,
                                                   are_all_records_related=False),
                                 generate_relation(first_group_percent=0.3,
                                                   first_group_min=1,
                                                   first_group_max=1,
                                                   first_group_foreign_key_percent=0.5,
                                                   second_group_percent=0.2,
                                                   second_group_min=1,
                                                   second_group_max=1,
                                                   second_group_foreign_key_percent=0.2,
                                                   third_group_percent=0.5,
                                                   third_group_min=1,
                                                   third_group_max=1,
                                                   third_group_foreign_key_percent=0.3,
                                                   group_size=NUMBER_OF_RENTALS,
                                                   foreign_group_size=NUMBER_OF_PIECES,
                                                   are_all_records_related=False)),
                'rental', [['DATE_START', 'DATE_END', 'DATE_DEADLINE', 'NUMBER_OF_RENEWALS', 'PIECE_ID', 'READER_ID']])

    save_to_csv(generate_pieces(generate_relation(first_group_percent=0.1,
                                                  first_group_min=1,
                                                  first_group_max=1,
                                                  first_group_foreign_key_percent=0.25,
                                                  second_group_percent=0.4,
                                                  second_group_min=1,
                                                  second_group_max=1,
                                                  second_group_foreign_key_percent=0.5,
                                                  third_group_percent=0.50,
                                                  third_group_min=1,
                                                  third_group_max=1,
                                                  third_group_foreign_key_percent=0.25,
                                                  group_size=NUMBER_OF_PIECES,
                                                  foreign_group_size=NUMBER_OF_LIBRARIES,
                                                  are_all_records_related=False),
                                generate_relation(first_group_percent=0.375,
                                                  first_group_min=1,
                                                  first_group_max=1,
                                                  first_group_foreign_key_percent=0.2,
                                                  second_group_percent=0.175,
                                                  second_group_min=1,
                                                  second_group_max=1,
                                                  second_group_foreign_key_percent=0.5,
                                                  third_group_percent=0.25,
                                                  third_group_min=1,
                                                  third_group_max=1,
                                                  third_group_foreign_key_percent=0.3,
                                                  group_size=NUMBER_OF_PIECES,
                                                  foreign_group_size=NUMBER_OF_BOOKS,
                                                  are_all_records_related=True)),
                'piece', [['IS_RENTED', 'IS_HARDCOVER', 'VERSION', 'CONDITION_DESCRIPTION', 'BOOK_ID', 'LIBRARY_ID']])

    save_to_csv(generate_relation(first_group_percent=0.65,
                                  first_group_min=1,
                                  first_group_max=1,
                                  first_group_foreign_key_percent=0.4,
                                  second_group_percent=0.3,
                                  second_group_min=2,
                                  second_group_max=2,
                                  second_group_foreign_key_percent=0.3,
                                  third_group_percent=0.05,
                                  third_group_min=3,
                                  third_group_max=3,
                                  third_group_foreign_key_percent=0.3,
                                  group_size=NUMBER_OF_BOOKS,
                                  foreign_group_size=NUMBER_OF_CATEGORIES,
                                  are_all_records_related=True),
                'book_category', [['BOOK_ID', 'CATEGORY_ID']])

    save_to_csv(generate_authors(generate_relation(first_group_percent=0.35,
                                                   first_group_min=1,
                                                   first_group_max=1,
                                                   first_group_foreign_key_percent=0.1,
                                                   second_group_percent=0.4,
                                                   second_group_min=2,
                                                   second_group_max=5,
                                                   second_group_foreign_key_percent=0.4,
                                                   third_group_percent=0.25,
                                                   third_group_min=5,
                                                   third_group_max=15,
                                                   third_group_foreign_key_percent=0.5,
                                                   group_size=NUMBER_OF_AUTHORS,
                                                   foreign_group_size=NUMBER_OF_BOOKS,
                                                   are_all_records_related=True)),
                'book_author', [['AUTHOR_ID', 'BOOK_ID']])
