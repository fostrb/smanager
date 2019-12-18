import readline
import ast


class SServ(object):
    def __init__(self):
        self.cmds = {}
        self.toplv_cmds = []
        self.init_cmds()

    def parse_command(self, cmd_string):
        """
        accepts a string, tokenizes, and matches to a command, passing args.
        
        :param cmd_string: Command received as a string.
        """
        if cmd_string.strip() is "":
            return ""
        try:
            args = cmd_string.strip().split(' ')
            command = args[0]
            args.pop(0)

            evaled = []
            for arg in args:
                try:
                    evaled.append(ast.literal_eval(arg))
                except Exception as ie:
                    evaled.append(str(arg))

            if command.lower() in self.cmds.keys():
                r = self.cmds[command.lower()](*args)
                return r
            else:
                raise KeyError("Command \"" + command + "\" not found.")
        except Exception as e:
            print(e)
            return e

    def init_cmds(self):
        self.cmds = {}
        for method in dir(self):
            if method.startswith("toplevel_cmd"):
                command = method[13:]
                m = getattr(self, method)
                self.cmds[command] = m
                self.toplv_cmds.append(command)
            elif method.startswith("cmd_"):
                command = method[4:]
                m = getattr(self, method)
                self.cmds[command] = m

    def cmd_help(self):
        '''
        Print the help dialogue for this service
        '''
        returnstring = "-"*40 + '\n'
        returnstring += self.__class__.__name__ + '\n'
        returnstring += '-'*40+'\n'
        for cmd, boundmeth in self.cmds.items():
            if boundmeth.__doc__ is not None:
                returnstring += (cmd + ": " + boundmeth.__doc__ + '\n')
            else:
                returnstring += (cmd + '\n')
        return returnstring

    def restart(self):
        """
        Overload method to return a new instance of self with contextual data of running stuff
        """
        return None

    def cleanup(self):
        pass

    def disconnect_notification(self, address=None):
        pass
