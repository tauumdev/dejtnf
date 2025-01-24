import cmd


class config(cmd.Cmd):
    def __init__(self, equipment_manager):
        super().__init__()
        self.equipment_manager = equipment_manager
        self.prompt = "config> "

    def emptyline(self):
        pass

    def do_set(self, arg):
        """Set equipment"""
        # self.equipment_manager.set()

    def do_get(self, arg):
        """Get equipment"""
        # self.equipment_manager.get()

    def do_exit(self, arg):
        """Exit config"""
        return True


class Control(cmd.Cmd):
    def __init__(self, equipment_manager):
        super().__init__()
        self.equipment_manager = equipment_manager
        self.prompt = "control> "

    def emptyline(self):
        pass

    def do_start(self, arg):
        """Start equipment"""
        # self.equipment_manager.start()

    def do_stop(self, arg):
        """Stop equipment"""
        # self.equipment_manager.stop()

    def do_reset(self, arg):
        """Reset equipment"""
        # self.equipment_manager.reset()

    def do_exit(self, arg):
        """Exit control"""
        return True


class CommandCli(cmd.Cmd):
    def __init__(self, equipment_manager):
        super().__init__()
        self.equipment_manager = equipment_manager
        self.prompt = "dejtnf> "

    def emptyline(self):
        pass

    def do_config(self, arg):
        """Enter configuration mode"""
        config(self.equipment_manager).cmdloop()

    def do_control(self, arg):
        """Enter control mode"""
        Control(self.equipment_manager).cmdloop()

    def do_exit(self, arg):
        """Exit program"""
        return True


if __name__ == "__main__":
    print("Starting program...")
    equipment_manager = []
    cmd = CommandCli(equipment_manager)
    cmd.cmdloop()
