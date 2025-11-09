import random
from src.core.enums import SettingState
from src.ui.renderers.base import EraRenderer


class QuantumRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("⟨" + "═" * (self.width - 2) + "⟩")
        output.append("│ QUANTUM CONFIGURATION │ " + menu_node.category.ljust(self.width - 28) + "│")
        output.append("⟨" + "═" * (self.width - 2) + "⟩")
        output.append("")

        for setting in settings[:self.height - 8]:
            state_symbol = self._quantum_state(setting.state)
            probability = random.randint(30, 100)
            line = f" {state_symbol} {setting.label[:45]:45s} P={probability}%"
            output.append(line[:self.width])

        output.append("")
        output.append("⟨OBSERVE TO COLLAPSE WAVEFUNCTION⟩")

        return "\n".join(output)

    def _quantum_state(self, state: SettingState) -> str:
        if state == SettingState.ENABLED:
            return "|1⟩"
        else:
            return "|0⟩"

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("╔═══════════════════════════════════╗")
        output.append("║ QUANTUM STATE MANIPULATION        ║")
        output.append("╠═══════════════════════════════════╣")
        output.append("║ " + setting.label[:33].ljust(33) + " ║")
        output.append("║                                   ║")
        output.append("║ α|0⟩ + β|1⟩                       ║")
        output.append("║                                   ║")
        output.append("║ [ENTANGLE]  [SUPERPOSE]  [MEASURE]║")
        output.append("╚═══════════════════════════════════╝")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("⟨═══════════════════════════════════⟩")
        output.append("│ QUANTUM ANOMALY DETECTED          │")
        output.append("⟨═══════════════════════════════════⟩")
        output.append("│ " + message[:33].ljust(33) + " │")
        output.append("│                                   │")
        output.append("│      [ACKNOWLEDGE]                │")
        output.append("⟨═══════════════════════════════════⟩")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        states = ["⟨0|", "⟨ψ|", "|ψ⟩", "|1⟩"]
        state_index = min(int(progress * len(states)), len(states) - 1)
        return f"Decoherence: {states[state_index]} {int(progress * 100)}%"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[48;2;10;0;50m",
            "text": "\033[38;2;0;255;255m",
            "quantum": "\033[38;2;255;0;255m",
            "reset": "\033[0m",
        }
