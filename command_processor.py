import sympy as sp
import re

class CommandProcessor:
    """
    A class to process and replace mathematical expressions in commands.

    Methods
    -------
    evaluate_expression(expression)
        Evaluates a mathematical expression and returns the result.

    replace_math_expressions(input_string)
        Replaces mathematical expressions within square brackets with their evaluated results.

    process_command(cmd)
        Processes a command by replacing specific substrings and evaluating mathematical expressions.
    """

    @staticmethod
    def evaluate_expression(expression):
        """
        Evaluates a mathematical expression and returns the result.

        Parameters
        ----------
        expression : str
            The mathematical expression to evaluate.

        Returns
        -------
        result : sympy.core.expr.Expr
            The evaluated result of the expression.
        """
        try:
            result = sp.sympify(expression)
            return result
        except sp.SympifyError:
            return None

    @staticmethod
    def replace_math_expressions(input_string):
        """
        Replaces mathematical expressions within square brackets with their evaluated results.

        Parameters
        ----------
        input_string : str
            The input string containing mathematical expressions within square brackets.

        Returns
        -------
        str
            The input string with mathematical expressions replaced by their evaluated results.
        """
        input_string = input_string.replace('$30', '255.0')
        pattern = re.compile(r'\[(.*?)\]')
        matches = pattern.findall(input_string)

        for match in matches:
            result = CommandProcessor.evaluate_expression(match)
            if result is not None:
                input_string = input_string.replace(f'[{match}]', str(result))
            else:
                input_string = input_string.replace(f'[{match}]', '[Invalid expression]')

        return input_string

    @staticmethod
    def process_command(cmd):
        """
        Processes a command by replacing specific substrings and evaluating mathematical expressions.

        Parameters
        ----------
        cmd : str
            The command to process.

        Returns
        -------
        str
            The processed command.
        """
        cmd = re.sub(r'\([^)]*\)', '', cmd) # remove comments
        if len(cmd) == 0:
            cmd=''
        elif cmd[0] == 'S':
            cmd = 'M3 ' + cmd
        elif cmd[0] in ['X', 'Y', 'F']:
            cmd = 'G1 ' + cmd
        elif '$H' in cmd:
            cmd = 'G28\r\n'
        elif '?' in cmd:
            cmd = 'M114\r\n'

        cmd = CommandProcessor.replace_math_expressions(cmd)
        return cmd

