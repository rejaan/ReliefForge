import customtkinter as ctk

# Erscheinungsbild
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class SliceForge(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SliceForge")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Linke Seite (Vorschau)
        self.preview = ctk.CTkFrame(self)
        self.preview.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        self.preview_label = ctk.CTkLabel(
            self.preview,
            text="No image loaded",
            font=("Helvetica", 24)
        )
        self.preview_label.pack(expand=True)

        # Rechte Seite (Einstellungen)
        self.sidebar = ctk.CTkFrame(self, width=300)
        self.sidebar.pack(side="right", fill="y", padx=15, pady=15)

        ctk.CTkLabel(
            self.sidebar,
            text="SliceForge",
            font=("Helvetica", 26, "bold")
        ).pack(pady=(20, 30))

        ctk.CTkButton(
            self.sidebar,
            text="Open Image"
        ).pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            self.sidebar,
            text="Generate STL"
        ).pack(fill="x", padx=20, pady=10)


if __name__ == "__main__":
    app = SliceForge()
    app.mainloop()