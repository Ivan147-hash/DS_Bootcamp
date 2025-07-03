import sys

clients = [
  'andrew@gmail.com',
  'jessica@gmail.com',
  'ted@mosby.com',
  'john@snow.is',
  'bill_gates@live.com',
  'mark@facebook.com',
  'elon@paypal.com',
  'jessica@gmail.com'
]

participants = [
  'walter@heisenberg.com',
  'vasily@mail.ru',
  'pinkman@yo.org',
  'jessica@gmail.com',
  'elon@paypal.com',
  'pinkman@yo.org',
  'mr@robot.gov',
  'eleven@yahoo.com'
]

recipients = [
  'andrew@gmail.com',
  'jessica@gmail.com',
  'john@snow.is'
]

def call_center():
  result = list(set(clients) - set(recipients))
  return result

def potential_clients():
  result = list(set(participants) - set(clients))
  return result

def loly_program():
  result = list(set(clients) - set(recipients))
  return result

def list_for_callcenter():
  if sys.argv[1] == 'call_center': 
    return call_center()
  elif sys.argv[1] == 'potential_clients': 
    return potential_clients()
  elif sys.argv[1] == 'loly_program': 
    return loly_program()
  raise ValueError('Wrong argument')


if __name__ == '__main__':
  if len(sys.argv) == 2:
    # result = list_for_callcenter()
    print(list_for_callcenter())
  else:
    print('Invalid input')