#!/usr/bin/env python3
"""
Minimal FastHTML application demonstrating AppImage packaging with DaisyUI and Tailwind CSS.
"""

from fasthtml.common import *
import os
import sys
import subprocess
import platform
import socket
import webbrowser
from contextlib import closing
from datetime import datetime
import tempfile
from pathlib import Path

# DaisyUI imports
from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes, btn_styles
from cjm_fasthtml_daisyui.components.data_display.card import card, card_body, card_title, card_actions
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
from cjm_fasthtml_daisyui.components.data_display.stat import stat, stat_title, stat_value, stat_desc, stats
from cjm_fasthtml_daisyui.components.data_input.text_input import text_input, text_input_colors
from cjm_fasthtml_daisyui.components.navigation.navbar import navbar, navbar_start, navbar_center, navbar_end
from cjm_fasthtml_daisyui.components.layout.hero import hero, hero_content
from cjm_fasthtml_daisyui.components.layout.divider import divider
from cjm_fasthtml_daisyui.components.feedback.alert import alert, alert_colors
from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui, border_dui
from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
from cjm_fasthtml_daisyui.core.testing import create_theme_selector

# Tailwind imports
from cjm_fasthtml_tailwind.utilities.spacing import p, m, space
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import flex_display, gap, grid_cols, items, justify, grid_display
from cjm_fasthtml_tailwind.utilities.sizing import w, h, max_w, min_h
from cjm_fasthtml_tailwind.utilities.typography import text_color, font_size, font_weight, text_align, font_family, break_all
from cjm_fasthtml_tailwind.utilities.backgrounds import bg
from cjm_fasthtml_tailwind.utilities.borders import rounded
from cjm_fasthtml_tailwind.utilities.effects import shadow
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import flex
from cjm_fasthtml_tailwind.core.base import combine_classes

# Find an available port
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

# Get port from environment or find a free one
PORT_ENV = os.environ.get('FASTHTML_PORT', '0')
PORT = int(PORT_ENV) if PORT_ENV != '0' else find_free_port()
HOST = os.environ.get('FASTHTML_HOST', '127.0.0.1')

# Setup writable directory for session keys and other files
# Use temp directory when running from AppImage
if os.environ.get('APPIMAGE'):
    # Running from AppImage - use temp directory
    WORK_DIR = Path(tempfile.mkdtemp(prefix='fasthtml-app-'))
    os.chdir(WORK_DIR)
else:
    # Running normally - use current directory
    WORK_DIR = Path.cwd()

# Create the FastHTML app with DaisyUI headers
app, rt = fast_app(
    pico=False,
    hdrs=get_daisyui_headers() + [
        Script(src='https://unpkg.com/htmx.org@2.0.7'),
    ],
    title="FastHTML AppImage Demo"
)

# State for demo
todos = []
counter = 0

@rt('/')
def get():
    return Div(
        # Navbar
        Div(
            Div(
                Div(
                    H1("FastHTML AppImage Demo",
                       cls=combine_classes(font_size._2xl, font_weight.bold, text_dui.primary)),
                    cls=str(navbar_start)
                ),
                Div(
                    Span(f"Running on {platform.system()} {platform.release()}",
                         cls=combine_classes(badge, badge_colors.secondary)),
                    cls=str(navbar_center)
                ),
                Div(
                    create_theme_selector(),
                    cls=combine_classes(flex_display, justify.end, flex(1), navbar_end)
                ),
                cls=combine_classes(navbar, bg_dui.base_200, shadow.lg, p(4))
            )
        ),

        # Main content container
        Div(
            # Hero section with system info
            Div(
                Div(
                    H2(f"Python {sys.version.split()[0]}",
                       cls=combine_classes(font_size.xl, font_weight.semibold, text_dui.base_content)),
                    P(f"Server: {HOST}:{PORT}",
                      cls=combine_classes(text_dui.base_content)),
                    cls=combine_classes(hero_content, text_align.center)
                ),
                cls=combine_classes(hero, bg_dui.base_200, rounded.lg, m.y(4))
            ),

            # Grid layout for main sections
            Div(
                # Counter demo card
                Card(
                    Div(
                        H2("Counter Demo", cls=combine_classes(card_title, text_dui.primary)),
                        Div(
                            Div(
                                Span(f"Count: ", cls=str(font_weight.medium)),
                                Span(counter, id="counter",
                                     cls=combine_classes(font_size._2xl, font_weight.bold, text_dui.primary)),
                                cls=combine_classes(stat_value, m.y(4))
                            ),
                            cls=str(stat)
                        ),
                        Div(
                            Button("Increment",
                                   cls=combine_classes(btn, btn_colors.primary, btn_sizes.lg, w.full),
                                   hx_post="/increment",
                                   hx_target="#counter",
                                   hx_swap="innerHTML"),
                            cls=str(card_actions)
                        ),
                        cls=str(card_body)
                    ),
                    cls=combine_classes(card, bg_dui.base_100, shadow.xl)
                ),

                # Todo list card
                Card(
                    Div(
                        H2("Todo List", cls=combine_classes(card_title, text_dui.secondary)),
                        Form(
                            Div(
                                Input(type="text", name="task",
                                      placeholder="Enter a task...",
                                      required=True,
                                      cls=combine_classes(text_input, text_input_colors.secondary, w.full)),
                                cls=str(m.b(4))
                            ),
                            Button("Add Task", type="submit",
                                   cls=combine_classes(btn, btn_colors.secondary, w.full)),
                            hx_post="/add-todo",
                            hx_target="#todo-list",
                            hx_swap="innerHTML",
                            hx_on="htmx:afterRequest: this.reset()",
                            cls=str(space.y(2))
                        ),
                        Div(cls=str(divider)),
                        Div(
                            Ul(*[Li(todo, cls=combine_classes(p(2), bg_dui.base_200.hover, rounded.md, m.y(1)))
                                for todo in todos],
                               id="todo-list",
                               cls=str(space.y(2))),
                            cls=str(min_h(24))
                        ),
                        cls=str(card_body)
                    ),
                    cls=combine_classes(card, bg_dui.base_100, shadow.xl)
                ),

                cls=combine_classes(grid_display, grid_cols(1).md, grid_cols(2).lg, gap(6))
            ),

            # System information section
            Card(
                Div(
                    Div(
                        H2("System Information", cls=combine_classes(card_title, text_dui.accent)),
                        Button("Refresh",
                               cls=combine_classes(btn, btn_colors.accent, btn_sizes.sm),
                               hx_get="/system-info",
                               hx_target="#system-info",
                               hx_swap="outerHTML"),
                        cls=combine_classes(flex_display, justify.between, items.center)
                    ),
                    Div(cls=str(divider)),
                    Div(
                        *system_info_stats(),
                        cls=combine_classes(stats, bg_dui.base_200, rounded.lg, w.full)
                    ),
                    cls=str(card_body),
                    id="system-info"
                ),
                cls=combine_classes(card, bg_dui.base_100, shadow.xl, m.t(6))
            ),

            # Launch options info
            Div(
                Div(
                    H3("Launch Options", cls=combine_classes(font_size.lg, font_weight.semibold, text_dui.info_content)),
                    P("Configure how this app opens:", cls=str(text_dui.info_content)),
                    cls=str(m.b(2))
                ),
                Div(
                    Div("FASTHTML_BROWSER=app",
                        cls=combine_classes(badge, badge_colors.primary, font_family.mono)),
                    Span(" for standalone window mode", cls=str(text_dui.info_content)),
                    cls=str(m.y(2))
                ),
                Div(
                    Div("FASTHTML_BROWSER=none",
                        cls=combine_classes(badge, badge_colors.warning, font_family.mono)),
                    Span(" to not open browser automatically", cls=str(text_dui.info_content)),
                    cls=str(m.y(2))
                ),
                Div(
                    Div("Default",
                        cls=combine_classes(badge, badge_colors.success)),
                    Span(" Opens in your default browser", cls=str(text_dui.info_content)),
                    cls=str(m.y(2))
                ),
                cls=combine_classes(alert, alert_colors.info, m.t(6))
            ),

            cls=combine_classes(p(6), max_w.screen_2xl, m.auto)
        ),
        cls=combine_classes(min_h.screen, bg_dui.base_100)
    )

def system_info_stats():
    """Generate system info stats components."""
    is_appimage = os.environ.get('APPIMAGE')
    return [
        Div(
            Div("Process ID", cls=str(stat_title)),
            Div(str(os.getpid()), cls=str(stat_value)),
            cls=str(stat)
        ),
        Div(
            Div("Working Directory", cls=str(stat_title)),
            Div(str(WORK_DIR if is_appimage else os.getcwd()),
                cls=combine_classes(stat_value, font_size.sm, break_all)),
            cls=str(stat)
        ),
        Div(
            Div("AppImage", cls=str(stat_title)),
            Div("Yes" if is_appimage else "No",
                cls=combine_classes(stat_value,
                                   text_dui.success if is_appimage else text_dui.base_content)),
            cls=str(stat)
        ),
        Div(
            Div("Timestamp", cls=str(stat_title)),
            Div(datetime.now().strftime('%H:%M:%S'), cls=str(stat_value)),
            Div(datetime.now().strftime('%Y-%m-%d'), cls=str(stat_desc)),
            cls=str(stat)
        ),
    ]

@rt('/increment', methods=['POST'])
def increment():
    global counter
    counter += 1
    return Span(counter, id="counter",
                cls=combine_classes(font_size._2xl, font_weight.bold, text_dui.primary))

@rt('/add-todo', methods=['POST'])
def add_todo(task: str):
    todos.append(task)
    return Ul(*[Li(todo, cls=combine_classes(p(2), bg_dui.base_200.hover, rounded.md, m.y(1)))
              for todo in todos],
              id="todo-list",
              cls=str(space.y(2)))

@rt('/system-info')
def system_info():
    return Div(
        Div(
            H2("System Information", cls=combine_classes(card_title, text_dui.accent)),
            Button("Refresh",
                   cls=combine_classes(btn, btn_colors.accent, btn_sizes.sm),
                   hx_get="/system-info",
                   hx_target="#system-info",
                   hx_swap="outerHTML"),
            cls=combine_classes(flex_display, justify.between, items.center)
        ),
        Div(cls=str(divider)),
        Div(
            *system_info_stats(),
            cls=combine_classes(stats, bg_dui.base_200, rounded.lg, w.full)
        ),
        cls=str(card_body),
        id="system-info"
    )

def open_browser(url):
    """Open browser based on environment settings."""
    browser_mode = os.environ.get('FASTHTML_BROWSER', 'default').lower()

    if browser_mode == 'none':
        print(f"Server running at {url}")
        print("Browser auto-open disabled. Please open manually.")
        return

    if browser_mode == 'app':
        # Try to open in app mode (standalone window)
        print(f"Opening in app mode at {url}")

        # Try different browsers in app mode
        if sys.platform == 'linux':
            browsers = [
                ['google-chrome', '--app=' + url],
                ['chromium', '--app=' + url],
                ['firefox', '--new-window', url],  # Firefox doesn't have true app mode
            ]

            for browser_cmd in browsers:
                try:
                    subprocess.Popen(browser_cmd,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    return
                except FileNotFoundError:
                    continue

    # Default: open in regular browser
    print(f"Opening in browser at {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    import uvicorn
    import threading
    import time

    # The actual URL with the port we found
    url = f"http://{HOST}:{PORT}"

    # Open browser after a short delay
    timer = threading.Timer(1.5, lambda: open_browser(url))
    timer.daemon = True
    timer.start()

    print(f"Starting FastHTML server on {url}")

    # Run the server with the actual port
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")