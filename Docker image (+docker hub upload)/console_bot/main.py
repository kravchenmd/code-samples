from console_bot.command_handling import CommandHandler
from console_bot.interface import ConsoleInterface, TerminalMode, ConsoleProgramMode, CommandInterface, \
    CommandCompleter, Container


def main():
    terminal_mode = TerminalMode()
    mode = ConsoleProgramMode()
    command_interface = CommandInterface()
    command_handler = CommandHandler()
    command_completer = CommandCompleter()
    container = Container()
    interface = ConsoleInterface(terminal_mode, mode, command_interface, command_handler, command_completer, container)

    interface.handle_request()


if __name__ == '__main__':
    main()
