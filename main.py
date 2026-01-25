from collections import UserDict
import re
from datetime import datetime, timedelta, date


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class WrongSizeNumberError(Exception):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if len(self.value) != 10 or not self.value.isdigit():
            raise WrongSizeNumberError("Please enter a valid phone number size - 10")



class NotFoundNumber(ValueError):
    pass

class WrongBirthdayError(ValueError):
    pass

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        pattern = r"\d{2}\.\d{2}\.\d{4}"
        self.birth_time = None
        if not re.fullmatch(pattern, value):
            raise WrongBirthdayError("Invalid date format. Use DD.MM.YYYY")
        self.birth_time = datetime.strptime(value, "%d.%m.%Y").date()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        try:
            self.phones.remove(self.find_phone(phone))
        except ValueError:
            raise NotFoundNumber('This phone number: {phone} is not present in the record')

    def edit_phone(self, old_phone, new_phone):
        try:
            number = self.phones.index(self.find_phone(old_phone))
            self.phones[number] = Phone(new_phone)
        except ValueError:
            raise NotFoundNumber('This phone number: {phone} is not present in the record')

    def find_phone(self, phone):
        for phone_contact in self.phones:
            if phone_contact.value == phone:
                return phone_contact
        else:
            return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"


def date_to_string(data):
    return data.strftime("%d.%m.%Y")


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        contact = self.data.get(name)
        return contact

    def delete(self, name):
        try:
            del self.data[name]
        except KeyError:
            return f'Such record of {name} was not found'

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for contact in self.data.values():

            if contact.birthday is None:
                continue

            birthday = contact.birthday.birth_time
            birthday_this_year = birthday.replace(year=today.year)

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year += timedelta(days=7 - birthday_this_year.weekday())

                congratulation_date_str = date_to_string(birthday_this_year)

                upcoming_birthdays.append({"name": contact.name.value, "congratulation_date": congratulation_date_str})
        return upcoming_birthdays

    def __str__(self):
        list_contact = []
        for key in self.data:
            list_contact.append(self.data[key])
        return f'{'\n'.join(str(p) for p in list_contact)}'


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except WrongBirthdayError:
            return "Invalid date format. Use DD.MM.YYYY"
        except ValueError:
            return "Give me name and phone/birthday please, in case of change additional number."
        except KeyError:
            return f"Current name was not found in dictionary."
        except IndexError:
            return f"Please provide an argument"

    return inner

def parse_input(user_input):
    try:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args
    except ValueError:
        return f"Please write a command"



@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) == 2:
        return f"Please enter additional number"
    name, old_phone, new_phone = args
    if book.find(name):
        book.find(name).edit_phone(old_phone, new_phone)
        return f"The contact has been changed"
    else:
        return f"This contact does not exist."


@input_error
def what_number(args, book: AddressBook):
    name = args[0]
    if book.find(name):
        return str(book.find(name))
    else:
        return f"This contact does not exist."


@input_error
def all_contacts(book: AddressBook):
    return str(book)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record and record.birthday is None:
        record.add_birthday(birthday)
        return f"The birthday has been added"
    if record.birthday:
        return f"This contact already has a birthday date."
    else:
        return f"This contact does not exist."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    contact = book.find(name)
    if contact and contact.birthday is not None:
        return contact.birthday
    elif contact.birthday is None:
        return f"This contact does not have a birthday date."
    else:
        return f"This contact does not exist."

@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()



def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(what_number(args, book))
        elif command == "all":
            print(all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()