"""
Performance Dashboard UI - Black & Orange Futuristic Theme
Layout:
  Row 1: Disk (left) | Memory (right)
  Row 2: GPU Memory (left) | GPU Usage (right)
  Row 3: CPU Usage (full width)
Includes:
  - 12px rounded cards
  - Matte dark background
  - Orange line with soft fill glow
"""

import tkinter as tk
import customtkinter as ctk
from modules.performance.backend import PerformanceMonitor
from modules.utils.helpers import check_matplotlib, check_psutil

# THEME COLORS (match main.py)
BACKGROUND_DARK = "#0E0E12"
CARD_BG = "#1B1B24"
ACCENT_ORANGE = "#FF6B00"
ACCENT_ORANGE_LIGHT = "#FF8C32"
TEXT_PRIMARY = "#F5F5F5"
TEXT_MUTED = "#8B8B94"


class PerformanceUI:
    def __init__(self, parent, monitor=None):
        self.parent = parent
        self.monitor = monitor if monitor else PerformanceMonitor()
        self.update_running = False
        self.update_job = None

        if not check_matplotlib():
            ctk.CTkLabel(
                parent,
                text="Install matplotlib: pip install matplotlib",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="red",
            ).pack(pady=20)
            return

        if not check_psutil():
            ctk.CTkLabel(
                parent,
                text="Install psutil: pip install psutil",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="red",
            ).pack(pady=20)
            return

        self._setup_matplotlib()
        self.build_ui()

    # ---------------- MATPLOTLIB SETUP ----------------

    def _setup_matplotlib(self):
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        self.Figure = Figure
        self.FigureCanvasTkAgg = FigureCanvasTkAgg

    # ---------------- UI LAYOUT ----------------

    def build_ui(self):
        self.parent.configure(fg_color=BACKGROUND_DARK)


        # HEADER
        header = ctk.CTkFrame(self.parent, fg_color=BACKGROUND_DARK)
        header.pack(fill="x", padx=22, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="PERFORMANCE",
            font=ctk.CTkFont("Segoe UI", 26, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            header,
            text="System Resource Monitoring",
            font=ctk.CTkFont("Segoe UI", 14),
            text_color=ACCENT_ORANGE,
        )
        subtitle.pack(side="left", padx=(12, 0))

        # MAIN CONTAINER
        container = ctk.CTkFrame(self.parent, fg_color=BACKGROUND_DARK)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Grid layout for 3 rows, 2 columns
        for r in range(3):
            container.grid_rowconfigure(r, weight=1, pad=8)
        container.grid_columnconfigure(0, weight=1, pad=8)
        container.grid_columnconfigure(1, weight=1, pad=8)

        self.build_graph_cards(container)

    # ---------------- CARD CREATOR ----------------

    def create_card(self, parent, title, row, col, colspan=1):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            corner_radius=12,  # 12px rounded corners
        )
        card.grid(
            row=row,
            column=col,
            columnspan=colspan,
            sticky="nsew",
            padx=8,
            pady=8,
        )

        label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont("Segoe UI", 16, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        label.pack(anchor="w", padx=14, pady=(8, 0))

        underline = ctk.CTkFrame(
            card, fg_color=ACCENT_ORANGE, height=2, corner_radius=2
        )
        underline.pack(fill="x", padx=14, pady=(4, 10))

        frame = tk.Frame(card, bg=CARD_BG, highlightthickness=0, bd=0)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        return frame

    # ---------------- BUILD GRAPH CARDS ----------------

    def build_graph_cards(self, parent):
        # slightly larger figs so charts fill cards nicely
        fig_w, fig_h = 5.6, 2.6

        # Row 1: Disk (left) | Memory (right)
        disk_frame = self.create_card(parent, "Disk Usage", 0, 0)
        self.disk_fig = self.Figure(figsize=(fig_w, fig_h), dpi=90)
        self._style_figure(self.disk_fig)
        self.disk_ax = self.disk_fig.add_subplot(111)
        self._style_axis(self.disk_ax)
        self.disk_canvas = self.FigureCanvasTkAgg(self.disk_fig, disk_frame)
        self.disk_canvas.get_tk_widget().pack(fill="both", expand=True)

        mem_frame = self.create_card(parent, "Memory Usage", 0, 1)
        self.mem_fig = self.Figure(figsize=(fig_w, fig_h), dpi=90)
        self._style_figure(self.mem_fig)
        self.mem_ax = self.mem_fig.add_subplot(111)
        self._style_axis(self.mem_ax)
        self.mem_canvas = self.FigureCanvasTkAgg(self.mem_fig, mem_frame)
        self.mem_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Row 2: GPU Memory (left) | GPU Usage (right)
        gpumem_frame = self.create_card(parent, "GPU Memory", 1, 0)
        self.gpu_mem_fig = self.Figure(figsize=(fig_w, fig_h), dpi=90)
        self._style_figure(self.gpu_mem_fig)
        self.gpu_mem_ax = self.gpu_mem_fig.add_subplot(111)
        self._style_axis(self.gpu_mem_ax)
        self.gpu_mem_canvas = self.FigureCanvasTkAgg(self.gpu_mem_fig, gpumem_frame)
        self.gpu_mem_canvas.get_tk_widget().pack(fill="both", expand=True)

        gpu_frame = self.create_card(parent, "GPU Usage", 1, 1)
        self.gpu_fig = self.Figure(figsize=(fig_w, fig_h), dpi=90)
        self._style_figure(self.gpu_fig)
        self.gpu_ax = self.gpu_fig.add_subplot(111)
        self._style_axis(self.gpu_ax)
        self.gpu_canvas = self.FigureCanvasTkAgg(self.gpu_fig, gpu_frame)
        self.gpu_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Row 3: CPU Usage (full width)
        cpu_frame = self.create_card(parent, "CPU Usage", 2, 0, colspan=2)
        self.cpu_fig = self.Figure(figsize=(fig_w * 2, fig_h), dpi=90)
        self._style_figure(self.cpu_fig)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self._style_axis(self.cpu_ax)
        self.cpu_canvas = self.FigureCanvasTkAgg(self.cpu_fig, cpu_frame)
        self.cpu_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------- STYLING ----------------

    def _style_figure(self, fig):
        fig.patch.set_facecolor(CARD_BG)
        # tighten layout a bit so charts are bigger
        fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.18)

    def _style_axis(self, ax):
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=TEXT_MUTED, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#33333F")
        ax.grid(True, color="#2A2A35", alpha=0.35)
        ax.set_ylim(0, 100)
        ax.set_xlim(0, 60)
        ax.set_ylabel("%", color=TEXT_MUTED)

    # ---------------- UPDATE GRAPHS ----------------

    def _draw_orange_series(self, ax, values):
        x = list(range(len(values)))
        ax.clear()
        self._style_axis(ax)

        # soft fill under line (glow effect)
        ax.fill_between(
            x,
            values,
            [0] * len(values),
            color=ACCENT_ORANGE,
            alpha=0.15,
        )

        # glow line
        ax.plot(
            x,
            values,
            color=ACCENT_ORANGE_LIGHT,
            linewidth=5,
            alpha=0.25,
        )

        # main line
        ax.plot(
            x,
            values,
            color=ACCENT_ORANGE,
            linewidth=2.4,
        )

    def update_graphs(self):
        data = self.monitor.get_all_data()

        self._draw_orange_series(self.disk_ax, data["disk"])
        self.disk_canvas.draw()

        self._draw_orange_series(self.mem_ax, data["memory"])
        self.mem_canvas.draw()

        self._draw_orange_series(self.gpu_mem_ax, data["gpu_memory"])
        self.gpu_mem_canvas.draw()

        self._draw_orange_series(self.gpu_ax, data["gpu"])
        self.gpu_canvas.draw()

        self._draw_orange_series(self.cpu_ax, data["cpu"])
        self.cpu_canvas.draw()

    # ---------------- UPDATE LOOP ----------------

    def start_updates(self):
        self.update_running = True
        self._loop_update()

    def _loop_update(self):
        if not self.update_running:
            return
        try:
            self.update_graphs()
        except Exception:
            pass
        self.update_job = self.parent.after(600, self._loop_update)

    def stop_updates(self):
        self.update_running = False
        if self.update_job:
            try:
                self.parent.after_cancel(self.update_job)
            except Exception:
                pass
            self.update_job = None
