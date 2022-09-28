import sys
import typing
from abc import ABC, abstractmethod
import time
from dataclasses import dataclass
from enum import Enum

import psutil
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from MongoDB.modules import shared_functions
from MongoDB.command_handling import CommandHandler, CmdToFuncConverter, AddressBookCmdToFuncConverter, \
    NotesCmdToFuncConverter, SortingCmdToFuncConverter


class Modes(str, Enum):
    ADDRESS_BOOK = 'AddressBook'
    NOTES = 'Notes'
    SORTING = 'Sorting'


class ProgramMode(ABC):
    @abstractmethod
    def choose_mode(self, terminal_run: bool) -> None:
        pass


class ConsoleProgramMode(ProgramMode):
    def __init__(self):
        self.value: Modes | None = None

    def choose_mode(self, terminal_run: bool) -> None:
        self.value = None
        message = "*** Console bot project ***\n" \
                  "***  Team #3 - PyStars  ***\n"
        print(message)
        time.sleep(1)
        message = "Modes of the bot:\n" \
                  "\t0 - Exit\n" \
                  "\t1 - Address book mode\n" \
                  "\t2 - Note mode\n" \
                  "\t3 - Sorting of a folder\n"
        print(message)

        while not self.value:
            command = None
            if terminal_run:
                command = prompt('Input number and press Enter choose mode: ')
            while not command:
                command = input('Enter number to choose mode: ')
                if command not in ['0', '1', '2', '3']:
                    print("You need to enter only a number from 0 to 3!")
                    command = None

            match command:
                case '0':
                    print("\nGoodbye!")
                    sys.exit()  # exit program (to prevent going to the next while)
                case '1':
                    self.value = Modes.ADDRESS_BOOK
                case '2':
                    self.value = Modes.NOTES
                case '3':
                    self.value = Modes.SORTING

        message = f"{self.value.value}' mode."
        print(message)


@dataclass
class CommandCompleter:
    completer: typing.Optional[WordCompleter] = None

    def choose_command_completer(self, mode: Modes) -> None:
        if mode == Modes.ADDRESS_BOOK:
            self.completer = WordCompleter(
                ['help', 'exit', 'hello', 'add_contact', 'remove_contact', 'change_phone', 'remove_phone',
                 'show_email', 'change_email', 'remove_email', 'show_phones', 'show_all', 'edit_birthday',
                 'days_to_birthday' 'birthday_in', 'save', 'load', 'find_contacts', 'back'])
        elif mode == Modes.NOTES:
            self.completer = WordCompleter(
                ['help', 'exit', 'back', 'hello', 'add', 'find', 'edit', 'delete',
                 'show', 'new tag', 'sort by tag'])
        elif mode == Modes.SORTING:
            self.completer = WordCompleter(
                ['help', 'back', 'close', 'exit', 'goodbye', 'sort_folder'])


@dataclass
class CommandInterface:
    converter: typing.Optional[CmdToFuncConverter] = None

    def choose_command_interface(self, mode: Modes) -> None:
        if mode == Modes.ADDRESS_BOOK:
            self.converter = AddressBookCmdToFuncConverter()
        elif mode == Modes.NOTES:
            self.converter = NotesCmdToFuncConverter()
        elif mode == Modes.SORTING:
            self.converter = SortingCmdToFuncConverter()


class TerminalMode:
    terminal_run = False

    @classmethod
    def terminal_run_check(cls):
        # Check if program is running PyCharm or cmd, bash, etc. for prompt_toolkit
        shells = {"cmd.exe", "bash.exe", "powershell.exe", "WindowsTerminal.exe"}
        parents = {parent.name() for parent in psutil.Process().parents()}
        if bool(parents & shells):
            cls.terminal_run = True
        return cls.terminal_run


class UserInterface(ABC):
    @abstractmethod
    def handle_request(self):
        pass


@dataclass
class ConsoleInterface(UserInterface):
    terminal_mode: TerminalMode  # for prompt_toolkit
    mode: ConsoleProgramMode
    command_interface: CommandInterface
    command_handler: CommandHandler
    command_completer: CommandCompleter

    def __initialization(self, terminal_run: bool):
        self.mode.choose_mode(terminal_run)
        current_mode = self.mode.value

        self.command_interface.choose_command_interface(current_mode)
        if terminal_run is not None:
            self.command_completer.choose_command_completer(current_mode)

    def handle_request(self):
        terminal_run = self.terminal_mode.terminal_run_check()
        self.__initialization(terminal_run)

        while True:
            command = None
            if terminal_run:
                command = prompt('\nEnter command: ', completer=self.command_completer.completer)
            while not command:
                command = input('\nEnter command: ')

            func, result = self.command_handler.handle_command(command, self.command_interface.converter)

            if func == shared_functions.back:
                self.__initialization(terminal_run)
                continue

            print(result)
            if func == shared_functions.exit_program:
                sys.exit()
