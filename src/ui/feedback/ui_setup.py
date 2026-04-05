import tkinter as tk
from tkinter import Frame, Label, ttk, BooleanVar
from PIL import Image, ImageDraw, ImageTk
from ... import constants as c
from ..widgets.rounded_button import RoundedButton
from ..widgets.markdown_renderer import MarkdownRenderer
from ..widgets.scrollable_frame import ScrollableFrame
from ..style_manager import apply_dark_theme
from ..tooltip import ToolTip
from ..info_manager import attach_info_mode
from ..assets import assets

def setup_feedback_ui(window):
    """
    Initializes the visual layout and tabbed navigation for the Feedback Dialog.
    """
    window.configure(bg=c.DARK_BG)
    apply_dark_theme(window)

    # Grid Root Configuration
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # Topmost Decoupling
    is_parent_topmost = False
    try:
        is_parent_topmost = window.parent.attributes("-topmost")
    except Exception:
        pass
    if not is_parent_topmost:
        window.transient(window.parent)

    # Accent Generation
    window._gray_accent = _create_vertical_accent(c.TEXT_SUBTLE_COLOR)
    window._cyan_accent = _create_vertical_accent("#00BCD4")
    window._blue_accent = _create_vertical_accent(c.BTN_BLUE)
    window._red_accent = _create_vertical_accent(c.WARN)
    window._green_accent = _create_vertical_accent(c.BTN_GREEN)
    window._yellow_accent = _create_vertical_accent(c.ATTENTION)

    # Main Containers
    window.main_content_frame = Frame(window, bg=c.DARK_BG, pady=20)
    window.main_content_frame.grid(row=0, column=0, sticky="nsew")
    window.main_content_frame.grid_rowconfigure(2, weight=1)
    window.main_content_frame.grid_columnconfigure(0, weight=1)

    # Header
    header_row = Frame(window.main_content_frame, bg=c.DARK_BG, padx=20)
    header_row.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    header_row.columnconfigure(0, weight=1)

    title_text = "Review Proposed Update" if window.on_apply_executor else "Review Last Update"
    Label(header_row, text=title_text, font=c.FONT_LARGE_BOLD, bg=c.DARK_BG, fg=c.TEXT_COLOR).grid(row=0, column=0, sticky="w")

    # Dynamic Alert Section
    window.alert_frame = Frame(window.main_content_frame, bg=c.DARK_BG, padx=20)

    # Notebook
    window.notebook = ttk.Notebook(window.main_content_frame)
    window.notebook.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
    window.renderers = []
    window.tab_widgets_for_info = []
    window.tab_indices = {}

    # Footer
    window.bottom_frame = Frame(window.main_content_frame, bg=c.DARK_BG, padx=20)
    window.bottom_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))

    show_val = window.app_state.config.get('show_feedback_on_paste', True) if window.app_state else True
    window.show_var = BooleanVar(value=show_val)
    window.auto_show_chk = ttk.Checkbutton(window.bottom_frame, text="Show this window automatically on paste", variable=window.show_var, style='Dark.TCheckbutton', command=window.logic.save_feedback_setting)
    window.auto_show_chk.pack(side="left")

    if window.on_apply_executor:
        window.apply_btn = RoundedButton(window.bottom_frame, text="Apply All", command=window.logic.handle_apply_all, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_BOLD, width=200, height=30, cursor="hand2")
        window.cancel_btn = RoundedButton(window.bottom_frame, text="Close", command=window.logic.handle_cancel, bg=c.BTN_GRAY_BG, fg=c.BTN_GRAY_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
        window.apply_btn.pack(side="right")
        window.cancel_btn.pack(side="right", padx=(0, 10))
    else:
        window.ok_button = RoundedButton(window.bottom_frame, text="OK", command=window.destroy, bg=c.BTN_BLUE, fg=c.BTN_BLUE_TEXT, font=c.FONT_NORMAL, width=100, height=30, cursor="hand2")
        window.ok_button.pack(side="right")

    # Info Toggle Integration
    # Must be initialized BEFORE populating tabs so that interactive rows can register help tips
    if window.app_state:
        window.info_toggle_btn = Label(window, image=assets.info_icon, bg=c.DARK_BG, cursor="hand2")
        window.info_mgr = attach_info_mode(window, window.app_state, manager_type='grid', grid_row=1, toggle_btn=window.info_toggle_btn)
    else:
        window.info_mgr = None

    # Build Tabs (now safe to register widgets with info_mgr)
    _populate_tabs(window)

def _create_vertical_accent(hex_color):
    """Generates a small vertical colored bar for tab identification."""
    size = (14, 22)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 1, 3, 20], radius=1, fill=hex_color)
    return ImageTk.PhotoImage(img)

def _populate_tabs(window):
    """Iterates through parsed segments and builds the notebook tabs."""
    plan = window.plan
    ordered_segments = plan.get('ordered_segments', [])
    has_unformatted = any(s['type'] == 'orphan' for s in ordered_segments)
    has_any_tags = plan.get('has_any_tags', False)
    has_file_blocks = bool(plan.get('updates') or plan.get('creations') or plan.get('deletions_proposed'))

    # Admonishment setup for unformatted outputs
    if has_unformatted and not has_any_tags:
        window.alert_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        Label(window.alert_frame, text="This text was not properly wrapped in the requested XML tags", fg=c.WARN, bg=c.DARK_BG, font=c.FONT_NORMAL).pack(side='left')
        window.admonish_btn = RoundedButton(window.alert_frame, text="Copy Correction Prompt", command=window.logic.copy_admonishment, bg=c.ATTENTION, fg="#FFFFFF", font=c.FONT_SMALL_BUTTON, width=200, height=26, cursor="hand2")
        window.admonish_btn.pack(side='right')
        ToolTip(window.admonish_btn, "Copy a prompt to tell the AI to follow the output format")

    changes_tab_added = False
    current_idx = 0

    for seg in ordered_segments:
        stype = seg['type']
        content = seg.get('content', "").strip()
        if not content and stype != 'file_placeholder': continue

        if stype == 'tag':
            tag_name = seg['tag']
            if tag_name == "DELETED FILES": continue

            if tag_name == "VERIFICATION" and not changes_tab_added and has_file_blocks:
                window.changes.add_interactive_changes_tab()
                changes_tab_added = True
                current_idx += 1

            title = tag_name.replace("ANSWERS TO DIRECT USER QUESTIONS", "Answers").title()
            icon = window._gray_accent
            info_key = "review_tab_placeholder"
            if "INTRO" in tag_name: info_key = "review_tab_intro"
            elif "CHANGES" in tag_name:
                icon = window._blue_accent; info_key = "review_tab_changes"
                changes_tab_added = True
            elif "ANSWERS" in tag_name: icon = window._cyan_accent; info_key = "review_tab_answers"
            elif "VERIFICATION" in tag_name: icon = window._green_accent; info_key = "review_tab_verification"
            elif "DELETED" in tag_name: icon = window._red_accent; info_key = "review_tab_delete"

            _add_standard_tab(window, title, content, icon=icon, info_key=info_key)
            if "VERIFICATION" in tag_name: window.tab_indices['verification'] = current_idx
            current_idx += 1
        elif stype == 'orphan':
            _add_unformatted_tab(window, "Unformatted output", content)
            current_idx += 1

    if not changes_tab_added and has_file_blocks:
        window.changes.add_interactive_changes_tab()

    if current_idx == 0:
        _add_standard_tab(window, "Response Summary", "The AI response contained only code blocks.", icon=window._gray_accent, info_key="review_tab_placeholder")

def _add_standard_tab(window, title, markdown_text, icon=None, info_key=None):
    if title == "Changes":
        window.changes.add_interactive_changes_tab()
        return

    frame = Frame(window.notebook, bg=c.DARK_BG)
    if icon: window.notebook.add(frame, text=title, image=icon, compound="left")
    else: window.notebook.add(frame, text=title)

    # Wrap the renderer in a ScrollableFrame to allow the entire content to be high enough
    scroll = ScrollableFrame(frame, bg=c.DARK_BG)
    scroll.pack(fill="both", expand=True)

    renderer = MarkdownRenderer(scroll.scrollable_frame, base_font_size=11, on_zoom=window.logic.adjust_font_size, auto_height=True)
    renderer.pack(fill="x", expand=True)
    renderer.set_markdown(markdown_text.strip())
    window.renderers.append(renderer)
    if info_key: window.tab_widgets_for_info.append((renderer, info_key))

def _add_unformatted_tab(window, title, raw_text):
    frame = Frame(window.notebook, bg=c.DARK_BG)
    window.notebook.add(frame, text=title, image=window._yellow_accent, compound="left")

    scroll = ScrollableFrame(frame, bg=c.DARK_BG)
    scroll.pack(fill="both", expand=True)

    renderer = MarkdownRenderer(scroll.scrollable_frame, base_font_size=11, on_zoom=window.logic.adjust_font_size, auto_height=True)
    renderer.pack(fill="x", expand=True)
    renderer.set_markdown(raw_text.strip())
    window.renderers.append(renderer)
    window.tab_widgets_for_info.append((renderer, "review_tab_unformatted"))