"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""


from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from app.console import c_info, c_success, c_warn, c_error, c_heading, c_prompt


def calculator_repl():
    try:
        calc = Calculator()
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(c_heading("Calculator started. Type 'help' for commands."))

        while True:
            try:
                command = input(c_prompt("\nEnter command: ")).lower().strip()

                if command == 'help':
                    print(c_heading("\nAvailable commands:"))
                    print(c_info("  add, subtract, multiply, divide, power, root, modulus, intdiv, percentage - Perform calculations"))
                    print(c_info("  history - Show calculation history"))
                    print(c_info("  clear   - Clear calculation history"))
                    print(c_info("  undo    - Undo the last calculation"))
                    print(c_info("  redo    - Redo the last undone calculation"))
                    print(c_info("  save    - Save calculation history to file"))
                    print(c_info("  load    - Load calculation history from file"))
                    print(c_info("  exit    - Exit the calculator"))
                    continue

                if command == 'exit':
                    try:
                        calc.save_history()
                        print(c_success("History saved successfully."))
                    except Exception as e:
                        print(c_warn(f"Warning: Could not save history: {e}"))
                    print(c_heading("Goodbye!"))
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(c_info("No calculations in history"))
                    else:
                        print(c_heading("\nCalculation History:"))
                        for i, entry in enumerate(history, 1):
                            print(c_info(f"{i}. {entry}"))
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print(c_success("History cleared"))
                    continue

                if command == 'undo':
                    if calc.undo():
                        print(c_success("Operation undone"))
                    else:
                        print(c_warn("Nothing to undo"))
                    continue

                if command == 'redo':
                    if calc.redo():
                        print(c_success("Operation redone"))
                    else:
                        print(c_warn("Nothing to redo"))
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print(c_success("History saved successfully"))
                    except Exception as e:
                        print(c_error(f"Error saving history: {e}"))
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print(c_success("History loaded successfully"))
                    except Exception as e:
                        print(c_error(f"Error loading history: {e}"))
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root', 'modulus', 'intdiv', 'percentage']:
                    try:
                        print(c_info("\nEnter numbers (or 'cancel' to abort):"))
                        a = input(c_prompt("First number: "))
                        if a.lower() == 'cancel':
                            print(c_warn("Operation cancelled"))
                            continue
                        b = input(c_prompt("Second number: "))
                        if b.lower() == 'cancel':
                            print(c_warn("Operation cancelled"))
                            continue

                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        result = calc.perform_operation(a, b)

                        # Prepare result for display
                        result_disp = result.normalize() if isinstance(result, Decimal) else result
                        if str(operation) == 'Percentage':
                            result_disp = f"{result_disp}%"

                        print(c_success(f"\nResult: {result_disp}"))
                    except (ValidationError, OperationError) as e:
                        print(c_error(f"Error: {e}"))
                    except Exception as e:
                        print(c_error(f"Unexpected error: {e}"))
                    continue

                print(c_warn(f"Unknown command: '{command}'. Type 'help' for available commands."))

            except KeyboardInterrupt:
                print(c_warn("\nOperation cancelled"))
                continue
            except EOFError:
                print(c_warn("\nInput terminated. Exiting..."))
                break
            except Exception as e:
                print(c_error(f"Error: {e}"))
                continue

    except Exception as e:
        print(c_error(f"Fatal error: {e}"))
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
