import time


class LayerTransition:
    def __init__(self, from_layer: str, to_layer: str):
        self.from_layer = from_layer
        self.to_layer = to_layer
        self.transition_type = self._determine_transition_type()

    def _determine_transition_type(self) -> str:
        transitions = {
            ("modern_settings_2020s", "desktop_gui_2000s"): "backwards_fade",
            ("modern_settings_2020s", "webapp_2010s"): "backwards_fade",
            ("modern_settings_2020s", "mobile_2015"): "backwards_fade",
            ("desktop_gui_2000s", "windows_95"): "backwards_fade",
            ("windows_95", "dos_config"): "boot_sequence",
            ("dos_config", "bios_setup"): "system_crash",
            ("bios_setup", "terminal"): "deeper_dive",
            ("terminal", "punch_cards"): "historical_flashback",
            ("punch_cards", "switch_panel"): "hardware_revelation",
            ("bios_setup", "quantum_interface"): "reality_glitch",
            ("quantum_interface", "metaphysical"): "transcendence",
            ("metaphysical", "recursive_meta"): "recursive_descent",
            ("recursive_meta", "final_layer"): "revelation",
        }

        key = (self.from_layer, self.to_layer)
        return transitions.get(key, "simple_fade")

    def execute(self):
        transition_method = getattr(self, f"_{self.transition_type}", None)
        if transition_method:
            transition_method()
        else:
            self._simple_fade()

    def _backwards_fade(self):
        print("\033[2J\033[H")
        time.sleep(0.3)

        messages = [
            "Reverting to earlier interface...",
            "Time rewinding...",
            "Loading previous paradigm...",
        ]

        for msg in messages:
            print(msg)
            time.sleep(0.5)

        time.sleep(0.5)
        print("\033[2J\033[H")

    def _boot_sequence(self):
        print("\033[2J\033[H\033[44;37m")

        boot_messages = [
            "Starting MS-DOS...",
            "",
            "Himem.sys loaded",
            "EMM386 loaded",
            "Loading COMMAND.COM...",
            "",
            "C:\\>",
        ]

        for msg in boot_messages:
            print(msg)
            time.sleep(0.3)

        time.sleep(1)
        print("\033[2J\033[H")

    def _system_crash(self):
        print("\033[2J\033[H\033[44;37m")

        print("\n" * 5)
        print("╔═══════════════════════════════════════════════╗".center(80))
        print("║                                               ║".center(80))
        print("║  A fatal exception 0E has occurred at        ║".center(80))
        print("║  0028:C0011E36 in VXD VMM(01) + 00010E36.    ║".center(80))
        print("║  The current application will be terminated. ║".center(80))
        print("║                                               ║".center(80))
        print("║  * Press any key to continue                ║".center(80))
        print("║                                               ║".center(80))
        print("╚═══════════════════════════════════════════════╝".center(80))

        time.sleep(2)
        print("\033[0m\033[2J\033[H")

    def _deeper_dive(self):
        print("\033[2J\033[H")

        for i in range(10):
            print("." * (i * 8))
            print(f"  Descending to lower level... {i*10}%")
            time.sleep(0.2)
            print("\033[2J\033[H")

        time.sleep(0.5)

    def _historical_flashback(self):
        print("\033[2J\033[H")

        years = [2020, 2000, 1995, 1990, 1980, 1970, 1960]
        for year in years:
            print(f"\n\n\n      Traveling to {year}...")
            time.sleep(0.3)
            print("\033[2J\033[H")

        time.sleep(0.5)

    def _hardware_revelation(self):
        print("\033[2J\033[H")

        print("\n\n")
        print("     The layers peel away...")
        time.sleep(1)
        print("     Software becomes hardware...")
        time.sleep(1)
        print("     Abstractions fade...")
        time.sleep(1)
        print("     Only switches remain.")
        time.sleep(2)

        print("\033[2J\033[H")

    def _reality_glitch(self):
        print("\033[2J\033[H")

        glitch_text = [
            "REALITY DESTABILIZING",
            "QUANTUM EFFECTS DETECTED",
            "ENTERING SUPERPOSITION",
        ]

        for _ in range(5):
            for line in glitch_text:
                print("\033[2J\033[H")
                print(line)
                time.sleep(0.3)

        print("\033[2J\033[H")

    def _transcendence(self):
        print("\033[2J\033[H")

        print("\n" * 8)
        print("          Leaving physical constraints behind...")
        time.sleep(1.5)
        print("          Entering the realm of pure concept...")
        time.sleep(1.5)
        print("          The metaphysical layer awaits.")
        time.sleep(2)

        print("\033[2J\033[H")

    def _recursive_descent(self):
        print("\033[2J\033[H")

        for depth in range(1, 6):
            indent = "  " * depth
            print(f"{indent}Settings{{")
            time.sleep(0.3)

        print()
        print("          How deep does it go?")
        time.sleep(2)

        for depth in range(5, 0, -1):
            indent = "  " * depth
            print(f"{indent}}}")
            time.sleep(0.2)

        print("\033[2J\033[H")

    def _revelation(self):
        print("\033[2J\033[H")

        print("\n" * 10)
        print("          .")
        time.sleep(1)
        print("          ..")
        time.sleep(1)
        print("          ...")
        time.sleep(1)
        print()
        print("          You made it.")
        time.sleep(2)

        print("\033[2J\033[H")

    def _simple_fade(self):
        print("\033[2J\033[H")
        print("\n\n\n          Loading...")
        time.sleep(1)
        print("\033[2J\033[H")
