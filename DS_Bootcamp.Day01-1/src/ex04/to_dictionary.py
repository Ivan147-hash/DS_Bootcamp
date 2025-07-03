def to_dictionary():
  list_of_tuples = [
    ('Russia', '25'),
    ('France', '132'),
    ('Germany', '132'),
    ('Spain', '178'),
    ('Italy', '162'),
    ('Portugal', '17'),
    ('Finland', '3'),
    ('Hungary', '2'),
    ('The Netherlands', '28'),
    ('The USA', '610'),
    ('The United Kingdom', '95'),
    ('China', '83'),
    ('Iran', '76'),
    ('Turkey', '65'),
    ('Belgium', '34'),
    ('Canada', '28'),
    ('Switzerland', '26'),
    ('Brazil', '25'),
    ('Austria', '14'),
    ('Israel', '12')
  ]


  dictionary = {}
  for number, country in list_of_tuples:
    if number not in dictionary:
        dictionary[number] = []
    dictionary[number].append(country)

  for country in dictionary:
    for number in dictionary[country]:
      print(f"'{number}' : '{country}'")


if __name__ == '__main__':
	to_dictionary()