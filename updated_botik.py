from collections import UserDict
from datetime import datetime as dtdt, timedelta
import re
import pickle

def parse_input(user_input):
    parts = user_input.strip().split()
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __eq__(self, another_value: str) -> bool:
        return self.value == another_value

class Phone(Field):
    def __init__(self, num):
        nums = re.findall(r'\d+', num)
        if nums and len(nums[0]) == 10:
            super().__init__(num)
        else:
            raise ValueError("Phone number must contain 10 digits")

    def __eq__(self, another_value: str) -> bool:
        return self.value == another_value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = dtdt.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)
        return True

    def remove_phone(self, phone):
        phone_obj = Phone(phone)
        if phone_obj in self.phones:
            self.phones.remove(phone_obj)
            return 'Removed successfully.'
        else:
            return 'This user has not such number. Nothing to delete!'

    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = Phone(old_phone)
        if old_phone_obj in self.phones:
            self.phones[self.phones.index(old_phone_obj)] = Phone(new_phone)
            return 'Number has changed.'
        else:
            return 'This user has not such number. Nothing to change!'

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = ', '.join(str(p) for p in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "No birthday set"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = dtdt.today().date()
        result = []
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)
                if today <= birthday_this_year <= today + timedelta(days=7):
                    result.append(f"{record.name.value}: {birthday_this_year.strftime('%d.%m.%Y')}")
        return result

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments provided."
        except KeyError:
            return "Contact not found."
        except AttributeError:
            return "Attribute error."
    return inner

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise IndexError("Not enough arguments provided.")
    name, phone, *_ = args
    print(f"Adding contact: {name}, phone: {phone}")  # Debug message
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        record.add_phone(phone)
        return "Contact added."
    else:
        record.add_phone(phone)
        return "Contact updated."

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        raise IndexError("Not enough arguments provided.")
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return 'No such user in address book!'
    record.add_birthday(birthday)
    return 'Birthday was added.'

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        raise IndexError("Not enough arguments provided.")
    name, *_ = args
    record = book.find(name)
    if record is None:
        return 'No such user in address book!'
    if record.birthday:
        return f"{name}'s birthday is on {record.birthday}"
    else:
        return 'Birthday not set for this contact.'

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join(upcoming_birthdays)

@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts in address book."
    return '\n'.join(str(record) for record in book.data.values())

@input_error
def show_phone(args, book: AddressBook):
    if len(args) < 1:
        raise IndexError("Not enough arguments provided.")
    name, *_ = args
    record = book.find(name)
    if record is None:
        return 'No such user in address book!'
    return ', '.join(str(phone) for phone in record.phones)

@input_error
def change_phone(args, book: AddressBook):
    if len(args) < 3:
        raise IndexError("Not enough arguments provided.")
    name, old_phone, new_phone, *_ = args
    print(f"Changing phone for: {name}, old phone: {old_phone}, new phone: {new_phone}")  # Debug message
    record = book.find(name)
    if record is None:
        return 'No such user in address book!'
    return record.edit_phone(old_phone, new_phone)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return a new address book if the file is not found

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
