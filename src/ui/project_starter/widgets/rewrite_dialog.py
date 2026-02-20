import tkinter as tk
from tkinter import Frame, Label, messagebox, Toplevel
from .... import constants as c
from ...widgets.rounded_button import RoundedButton
from ...widgets.scrollable_text import ScrollableText
from ...window_utils import position_window
from ..segment_manager import SegmentManager
from ...tooltip import ToolTip

class RewriteUnsignedDialog(Toplevel):
    """
    A dialog that allows the user to input a specific instruction to rewrite
    all unsigned segments, generates the prompt, and accepts the result.
    """
    def __init__(self, parent, segment_context_data, on_apply_callback):
        super().__init__(parent)
        self.parent = parent
        self.segment_context = segment_context_data # Dict containing keys, names, data, signoffs
        self.on_apply_callback = on_apply_callback
        self.withdraw()

        self.title("Rewrite Unsigned Segments")
        self.configure(bg=c.DARK_BG)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

        self.geometry("700x750")
        self.minsize(600, 600)
        position_window(self)
        self.deiconify()

    def _build_ui(self):
        main_frame = Frame(self, bg=c.DARK_BG, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_rowconfigure(5, weight=1) # Paste area expands
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        Label(main_frame, text="Rewrite Unsigned Segments", font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 5))
        Label(main_frame, text="Provide an instruction to modify all unsigned segments at once.", bg=c.DARK_BG, fg=c.TEXT_SUBTLE_COLOR).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # --- Section 1: User Instruction ---
        Label(main_frame, text="1. Your Instruction", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.instruction_text = ScrollableText(main_frame, height=4, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.instruction_text.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.instruction_text.text_widget.bind("<KeyRelease>", self._update_copy_button_state)

        # Copy Button Container
        copy_frame = Frame(main_frame, bg=c.DARK_BG)
        copy_frame.grid(row=4, column=0, sticky="e", pady=(0, 20))

        self.copy_btn = RoundedButton(copy_frame, text="Generate & Copy Prompt", command=self._generate_and_copy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_SMALL_BUTTON, width=200, height=28, radius=4, cursor="hand2")
        self.copy_btn.pack(side="right")
        self.copy_btn.set_state("disabled") # Initially disabled
        ToolTip(self.copy_btn, "Create and copy a prompt to modify all unlocked drafts based on your instruction", delay=500)

        # --- Section 2: Paste Response ---
        Label(main_frame, text="2. Paste LLM Response", font=c.FONT_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=5, column=0, sticky="nw", pady=(0, 5))

        self.response_text = ScrollableText(main_frame, bg=c.TEXT_INPUT_BG, fg=c.TEXT_COLOR, insertbackground=c.TEXT_COLOR, font=c.FONT_NORMAL)
        self.response_text.grid(row=6, column=0, sticky="nsew", pady=(0, 15))

        # --- Footer Actions ---
        btn_frame = Frame(main_frame, bg=c.DARK_BG)
        btn_frame.grid(row=7, column=0, sticky="e")

        btn_cancel = RoundedButton(btn_frame, text="Cancel", command=self.destroy, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=90, height=30, cursor="hand2")
        btn_cancel.pack(side="left", padx=(0, 10))

        btn_apply = RoundedButton(btn_frame, text="Apply Changes", command=self._on_apply, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=120, height=30, cursor="hand2")
        btn_apply.pack(side="left")
        ToolTip(btn_apply, "Update the project drafts with the pasted response", delay=500)

    def _update_copy_button_state(self, event=None):
        content = self.instruction_text.get("1.0", "end-1c").strip()
        if content:
            self.copy_btn.set_state("normal")
            self.copy_btn.config(bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT)
        else:
            self.copy_btn.set_state("disabled")
            self.copy_btn.config(bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT)

    def _generate_and_copy(self):
        instruction = self.instruction_text.get("1.0", "end-1c").strip()
        if not instruction: return

        # Unpack context
        keys = self.segment_context['keys']
        names = self.segment_context['names']
        data = self.segment_context['data']
        signoffs = self.segment_context['signoffs']

        targets = []
        references = []

        for k in keys:
            if signoffs[k]:
                references.append(k)
            else:
                targets.append(k)

        if not targets:
            messagebox.showinfo("Info", "All segments are signed off. Nothing to rewrite.")
            return

        # Build Prompt Blocks
        target_blocks = []
        for t in targets:
            name = names.get(t, t)
            content = data.get(t, "")
            target_blocks.append(f"--- Draft: {name} ---\n{content}\n")

        reference_blocks = []
        for r in references:
            name = names.get(r, r)
            content = data.get(r, "")
            reference_blocks.append(f"--- Locked Section: {name} ---\n{content}\n")

        friendly_map = {k: names.get(k, k) for k in targets}
        target_instructions = SegmentManager.build_prompt_instructions(targets, friendly_map)

        # Template from Constants
        prompt = c.WIZARD_REWRITE_PROMPT_TEMPLATE.format(
            instruction=instruction,
            references=''.join(reference_blocks) if reference_blocks else '(None)',
            targets=''.join(target_blocks),
            target_instructions=target_instructions
        )

        try:
            self.clipboard_clear()
            self.clipboard_append(prompt)
            self.copy_btn.config(text="Copied!", bg=c.BTN_GREEN, fg=c.BTN_GREEN_TEXT)
            self.after(2000, lambda: self._update_copy_button_state())
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.", parent=self)

    def _on_apply(self):
        content = self.response_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Input Required", "Please paste the LLM response first.", parent=self)
            return

        self.on_apply_callback(content)
        self.destroy()