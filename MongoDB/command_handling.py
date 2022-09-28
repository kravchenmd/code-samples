from abc import ABC, abstractmethod

from MongoDB.modules import address_book as f, shared_functions, notebook as n
from MongoDB.modules.sorting.sort import sort_folder


class CmdToFuncConverter(ABC):
    @staticmethod
    @abstractmethod
    def choose_function(cmd: list) -> tuple:
        pass


class AddressBookCmdToFuncConverter(CmdToFuncConverter):
    @classmethod
    def choose_function(cls, cmd: list) -> tuple:
        """
        Commands for AddressBook mode:
        - `close`, `exit`, `goodbye` - выход из программы
        - `hello` - выводит приветствие
        - 'back' - вернуться в главное меню выбора режима работы бота
        - `add contact`, `add_contact` - добавление контакта в книгу
        - `remove contact`, `remove_contact` - удаление контакта из книги
        - `change phone`, `change_phone` - изменение номера контакта
        - `remove phone`, `remove_phone` - удаление телефона
        - `show email`, `show_email` - показать email по имени
        - `change email`, `change_email` - изменение email. Пример: 'change _name_ _old_email_ _new_email_'
        - `remove email`, `remove_email` - удаление email
        - `phones`, `show phones`, `show_phones` - показать номера контакта по имени
        - `show all`, `show_all` - вывести все контакты с пагинацией (по умолчанию 2)
        - `edit birthday`, `edit_birthday` - изменить день рождения контакта
        - `days to birthday`, `days_to_birthday` - сколько дней до дня рождения контакта
        - 'birthday in', `birthday_in` - вывести список контактов, у которых ДР через заданное кол-во дней
        - `save`, `save_contacts` - сохранить контакты в файл, с использованием модуля `shelve`.
        - `load` - загрузить контакты из файла, с использованием модуля `shelve`.
        - `find contact`, `find_contact` - поиск контакта по имени или номеру телефона
        """

        match cmd:
            case ['close'] | ['exit'] | ['goodbye']:  # compare with one of the options in '[...]' ('|' is OR)
                return shared_functions.exit_program, []
            case ['hello']:
                return shared_functions.hello, cmd[1:]
            case ['back']:
                return shared_functions.back, []
            case ['add', 'contact', *args] | ['add_contact', *args]:  # *args is a list of all the arguments after 'add'
                return f.add_contact, args
            case ['remove', 'contact', *args] | ['remove_contact', *args]:
                return f.remove_contact, args
            case ['change', 'phone', *args] | ['change_phone', *args]:  # check 'change phone' or 'change_phone'
                return f.change_phone, args
            case ['remove', 'phone', *args] | ['remove_phone', *args]:
                return f.remove_phone, args
            case ['phones', *args] | ['show', 'phones', *args] | ['show_phones', *args]:
                return f.show_phones, args
            case ['show', 'all'] | ['show_all']:
                return f.show_contacts, []
            case ['change', 'birthday', *args] | ['change_birthday', *args]:
                return f.change_birthday, args
            case ['remove', 'birthday', *args] | ['remove_birthday', *args]:
                return f.remove_birthday, args
            case ['days', 'to', 'birthday', *args] | ['days_to_birthday', *args]:
                return f.days_to_birthday, args
            case ['change', 'email', *args] | ['change_email', *args]:
                return f.change_email, args
            case ['remove', 'email', *args]:
                return f.remove_email, args
            case ['show', 'emails', *args] | ['show_emails', *args]:
                return f.show_emails, args
            case ['birthday', 'in', *args] | ['birthday in', *args]:
                return f.birthday_in, args
            case ['find', *args]:
                return f.find, args
            case ['help']:
                return None, cls.choose_function.__doc__
            case _:  # '_' corresponds to the case when no match is found
                return None, "Unknown command!"


class NotesCmdToFuncConverter(CmdToFuncConverter):
    @classmethod
    def choose_function(cls, cmd: list) -> tuple:
        """
        Commands for Notes mode:
        - `add` - добавление новой заметки в Notes
        - `find` - поиск заметки по любому фрагменту (фрагмент заметки ввести через пробел) выводит все заметки,
        в которых найден указанный фрагмент
        - `edit` - редактирование заметки (формат команды - через пробел - номер заметки - новый текст и тег заметки)
        - `delete` - удаление заметки (необходимо внести порядковый номер заметки)
        - `show` - вывести все заметки в формате: номер тег текст
        - `new tag`, `new_tag` - добавить тег к существующей заметке. Формат: номер заметки новый тег (с символом #)
        - `sort by tag`, sort_by_tag - сортировать заметки по тегам
        - 'back' - вернуться в главное меню для выбора режима работы бота
        - `exit` - выход из программы. Также, во время выхода Notes сохраняются в 'database/notes_db.bin'
        """

        match cmd:
            case ['add', 'note', *args] | ['add_note', *args]:
                return n.add_note, args
            case ['delete', 'note', *args] | ['delete_note', *args]:
                return n.delete_note, args
            case ['edit', 'text', *args] | ['edit_text', *args]:
                return n.edit_text, args
            case ['edit', 'creation', 'date', *args] | ['edit_creation_date', *args]:
                return n.edit_creation_date, args
            case ['add', 'tags', *args] | ['add_tags', *args]:
                return n.add_tags, args
            case ['show', 'all', *args] | ['show_all', *args]:
                return n.show_all, args
            case ['show', 'done', 'notes', *args] | ['show_done_notes', *args]:
                return n.show_done_notes, args
            case ['find', 'by', 'text', *args] | ['find_by_text', *args]:
                return n.find_by_text, args
            case ['find', 'by', 'tag', *args] | ['find_by_tag', *args]:
                return n.find_by_tag, args
            case ['mark', 'as', 'done', *args] | ['mark_as_done', *args]:
                return n.mark_as_done, args
            case ['unmark', 'as', 'done', *args] | ['unmark_as_done', *args]:
                return n.unmark_as_done, args
            case ['exit', *args]:
                return shared_functions.exit_program, args
            case ['back']:
                return shared_functions.back, []
            case ['help']:
                return None, cls.choose_function.__doc__
            case _:  # '_' corresponds to the case when no match is found
                return None, "Unknown command! For help type `help`"


class SortingCmdToFuncConverter(CmdToFuncConverter):
    @classmethod
    def choose_function(cls, cmd: list) -> tuple:
        """
        Commands for sorting mode:
        - 'close', 'exit', 'goodbye' - exit the program
        - 'sort folder _path_', 'sort_folder _path_': sort the contacts by name
        - 'back': return to the main menu
        """
        match cmd:
            case ['close'] | ['exit'] | ['goodbye']:
                return shared_functions.exit_program, []
            case ['help']:
                return None, cls.choose_function.__doc__
            case ['back']:
                return shared_functions.back, []
            case ['sort', 'folder', *args] | ['sort_folder', *args]:
                return sort_folder, args
            case _:
                return None, "Unknown command!"


class CommandHandler:
    @staticmethod
    def handle_command(cmd: str, command_converter: CmdToFuncConverter) -> tuple:
        cmd = cmd.strip().split(' ')

        func, args = command_converter.choose_function(cmd)

        if func is not None:
            result = func(*args)
        else:
            result = args

        return func, result
