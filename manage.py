import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

class WelcomePage(tk.Frame):
    def __init__(self, master, switch_to_recipes):
        super().__init__(master)
        self.master = master
        self.switch_to_recipes = switch_to_recipes
        self.configure(bg="white")
        self.create_widgets()

    def create_widgets(self):
        welcome_label = ttk.Label(self, text="مرحبًا بكم في تطبيق وصفات الطبخ!", font=("Arial", 24, "bold"), background="white")
        welcome_label.pack(pady=50)

        start_button = ttk.Button(self, text="ابدأ التصفح", command=self.switch_to_recipes)
        start_button.pack(pady=20)

class RecipePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg="white")
        
        # بيانات الوصفات
        self.recipes = [
            {
                "title": "مكرونة بالبشاميل",
                "ingredients": "مكرونة، لحم مفروم، حليب، دقيق، زبدة، ملح، فلفل أسود",
                "instructions": "1. تسلق المكرونة.\n2. تحضر البشاميل.\n3. توضع طبقات المكرونة واللحم والبشاميل وتخبز.",
                "image": "pasta.jpg"  # ضع هنا اسم صورة موجودة مع المشروع
            },
            {
                "title": "بيتزا مارغريتا",
                "ingredients": "عجينة بيتزا، صلصة طماطم، جبن موتزاريلا، ريحان طازج",
                "instructions": "1. تفرد العجينة.\n2. توزع الصلصة والجبن.\n3. تخبز وتزين بالريحان.",
                "image": "pizza.jpg"
            }
        ]
        self.current_index = 0

        self.create_widgets()
        self.display_recipe()

    def create_widgets(self):
        self.title_label = ttk.Label(self, text="", font=("Arial", 24, "bold"), background="white")
        self.title_label.pack(pady=10)

        self.image_label = tk.Label(self, background="white")
        self.image_label.pack(pady=10)

        self.ingredients_label = ttk.Label(self, text="", font=("Arial", 14), background="white", justify="right")
        self.ingredients_label.pack(pady=10)

        self.instructions_label = ttk.Label(self, text="", font=("Arial", 14), background="white", justify="right")
        self.instructions_label.pack(pady=10)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=20)

        self.prev_button = ttk.Button(self.button_frame, text="السابق", command=self.prev_recipe)
        self.prev_button.grid(row=0, column=0, padx=10)

        self.next_button = ttk.Button(self.button_frame, text="التالي", command=self.next_recipe)
        self.next_button.grid(row=0, column=1, padx=10)

    def display_recipe(self):
        recipe = self.recipes[self.current_index]
        self.title_label.config(text=recipe["title"])
        self.ingredients_label.config(text=f"المكونات:\n{recipe['ingredients']}")
        self.instructions_label.config(text=f"طريقة التحضير:\n{recipe['instructions']}")

        # تحميل وعرض الصورة
        try:
            image = Image.open(recipe["image"])
            image = image.resize((300, 200))
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.photo)
        except Exception as e:
            self.image_label.config(image='', text="(لا توجد صورة)")

    def next_recipe(self):
        if self.current_index < len(self.recipes) - 1:
            self.current_index += 1
            self.display_recipe()
        else:
            messagebox.showinfo("معلومة", "هذه آخر وصفة.")

    def prev_recipe(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_recipe()
        else:
            messagebox.showinfo("معلومة", "هذه أول وصفة.")

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("تطبيق وصفات الطبخ")
        self.geometry("700x800")
        self.configure(bg="white")

        self.show_welcome_page()

    def show_welcome_page(self):
        self.clear_widgets()
        self.welcome_page = WelcomePage(self, self.show_recipe_page)
        self.welcome_page.pack(fill="both", expand=True)

    def show_recipe_page(self):
        self.clear_widgets()
        self.recipe_page = RecipePage(self)
        self.recipe_page.pack(fill="both", expand=True)

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
