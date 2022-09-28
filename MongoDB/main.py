from MongoDB.command_handling import CommandHandler
from MongoDB.interface import ConsoleInterface, TerminalMode, ConsoleProgramMode, CommandInterface, \
    CommandCompleter


def main():
    terminal_mode = TerminalMode()
    mode = ConsoleProgramMode()
    command_interface = CommandInterface()
    command_handler = CommandHandler()
    command_completer = CommandCompleter()
    interface = ConsoleInterface(terminal_mode, mode, command_interface,
                                 command_handler, command_completer)

    interface.handle_request()


if __name__ == '__main__':
    main()
