import customtkinter as ctk
from PIL import Image
import os

from modules.performance.ui import PerformanceUI
from modules.performance.backend import PerformanceMonitor
from modules.processes.ui import ProcessesUI
from modules.startup.ui import StartupAppsUI
from modules.settings.ui import SettingsUI


# ---------------- THEME COLORS ----------------
BACKGROUND_DARK = "#0E0E12"
SIDEBAR_BG = "#15151C"
SIDEBAR_HOVER = "#1F1F28"
SIDEBAR_ACTIVE = "#FF6B00"
CARD_BG = "#1B1B24"
TEXT_PRIMARY = "#F5F5F5"
TEXT_SECONDARY = "#B9B9C6"

ICON_SIZE = (20, 20)


# ==================================================
#                  MAIN DASHBOARD APP
# ==================================================
class TaskManagerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("System Monitoring Dashboard")
        self.root.geometry("1550x900")
        self.root.configure(bg=BACKGROUND_DARK)

        ctk.set_appearance_mode("dark")

        self.monitor = PerformanceMonitor()

        self.current_page = None
        self.page_instances = {}

        self.setup_sidebar()
        self.setup_content_area()
        self.show_performance()

    # ==================================================
    #                SIDEBAR + BUTTONS
    # ==================================================
    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.root, fg_color=SIDEBAR_BG, width=240, corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")

        # Title
        title = ctk.CTkLabel(
            self.sidebar,
            text="DASHBOARD",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        title.pack(anchor="w", pady=(25, 5), padx=20)

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="System Monitor",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=13),
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 25))

        # Neon icons folder
        icons_path = os.path.join("assets", "icons")

        self.btn_performance = self.sidebar_btn(
            "Performance",
            os.path.join(icons_path, "performance.png"),
            lambda: self.show_page("performance"),
        )

        self.btn_process = self.sidebar_btn(
            "Processes",
            os.path.join(icons_path, "process.png"),
            lambda: self.show_page("processes"),
        )

        self.btn_startup = self.sidebar_btn(
            "Startup Apps",
            os.path.join(icons_path, "startup.png"),
            lambda: self.show_page("startup"),
        )

        self.btn_settings = self.sidebar_btn(
            "Settings",
            os.path.join(icons_path, "settings.png"),
            lambda: self.show_page("settings"),
        )

        # Footer status
        footer = ctk.CTkLabel(
            self.sidebar,
            text="v1.0 • MONITORING ACTIVE",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=12),
        )
        footer.pack(side="bottom", pady=20)

    # Sidebar button builder
    def sidebar_btn(self, text, icon_path, command):
        if os.path.exists(icon_path):
            icon = ctk.CTkImage(Image.open(icon_path), size=ICON_SIZE)
        else:
            icon = None

        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            image=icon,
            anchor="w",
            width=200,
            height=48,
            fg_color=SIDEBAR_BG,
            hover_color=SIDEBAR_HOVER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8,
            command=command,
        )
        btn.pack(anchor="w", padx=20, pady=5)
        return btn

    # ==================================================
    #                 CONTENT AREA
    # ==================================================
    def setup_content_area(self):
        self.content_frame = ctk.CTkFrame(
            self.root,
            fg_color=BACKGROUND_DARK,
            corner_radius=0,
        )
        self.content_frame.pack(side="right", fill="both", expand=True)

    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    # ==================================================
    #                  PAGE MANAGER
    # ==================================================

    def show_page(self, name):
        if self.current_page == "performance":
            try:
                self.page_instances["performance"].stop_updates()
            except: 
                pass

        self.clear_content()

        if name == "performance":
            self.show_performance()
        elif name == "processes":
            self.show_processes()
        elif name == "startup":
            self.show_startup()
        elif name == "settings":
            self.show_settings()

        self.current_page = name

    # ============== INDIVIDUAL PAGES ===================

    def show_performance(self):
        page = PerformanceUI(self.content_frame, self.monitor)
        self.page_instances["performance"] = page
        page.start_updates()

        # Highlight button
        self.highlight_button(self.btn_performance)

    def show_processes(self):
        page = ProcessesUI(self.content_frame)
        self.page_instances["processes"] = page
        self.highlight_button(self.btn_process)

    def show_startup(self):
        page = StartupAppsUI(self.content_frame)
        self.page_instances["startup"] = page
        self.highlight_button(self.btn_startup)

    def show_settings(self):
        page = SettingsUI(self.content_frame)
        self.page_instances["settings"] = page
        self.highlight_button(self.btn_settings)

    # Highlight active sidebar button
    def highlight_button(self, active_btn):
        for btn in [
            self.btn_performance,
            self.btn_process,
            self.btn_startup,
            self.btn_settings,
        ]:
            btn.configure(fg_color=SIDEBAR_BG)

        active_btn.configure(fg_color=SIDEBAR_ACTIVE)


# ==================================================
#                  RUN APPLICATION
# ==================================================
if __name__ == "__main__":
    root = ctk.CTk()
    app = TaskManagerApp(root)
    root.mainloop()
