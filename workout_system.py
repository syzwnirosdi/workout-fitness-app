import os
import re
from PIL import Image, ImageOps
import customtkinter as ctk


class WorkoutExpertSystem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Workout & Fitness Recommendation Expert System")
        self.design_w = 1180
        self.design_h = 780
        self.geometry(f"{self.design_w}x{self.design_h}")
        self.minsize(1100, 720)

        ctk.set_appearance_mode("light")

        try:
            self.state("zoomed")
        except Exception:
            pass

        self.is_fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        self.bg = "#F7F1E7"
        self.card = "#FFFFFF"
        self.surface = "#FAF8F2"
        self.soft = "#EFE7DA"
        self.green = "#155B35"
        self.green_dark = "#0E4327"
        self.green_soft = "#EAF2E8"
        self.gold = "#B18435"
        self.text = "#1E1E1E"
        self.muted = "#666666"
        self.border = "#DDD0BE"
        self.warning = "#9A5A32"
        self.warning_soft = "#FBF4E9"

        self.configure(fg_color=self.bg)

        self.profile = {}
        self.answers = {}
        self.current_question = 0
        self.temp_answer = None
        self.option_cards = []
        self.triggered_rules = []
        self.final_result = {}
        self.image_cache = {}
        self.asset_lookup = {}
        self.preview_running = False
        self.stage = None

        self.icon_aliases = {
            "background": ["background"],
            "logo": [
                "eco_fitness_emblem_with_gold_accents",
                "elegant_fitness_emblem_with_gold_accents",
                "logo_dumbbell_leaf",
                "logo",
            ],
            "profile": ["elegant_profile_icon_with_nature_accents", "age_user"],
            "progress": ["fitness_progress_emblem_with_nature_accents", "progress"],
            "walking": ["elegant_walking_figure_with_botanical_accents", "lifestyle_activity"],
            "health": ["heart_shield_with_heartbeat_and_cross", "health_condition"],
            "restriction": ["eco_health_restriction_emblem", "medical_restriction"],
            "injury": ["healing_nature_icon_with_bandage_and_leaf", "injury_bandage"],
            "goal": ["target_with_gold_arrow_and_leaves", "fitness_goal_target"],
            "running": ["eco_friendly_runner_logo_design", "workout_type_running"],
            "body_focus": ["fitness_target_design_badge", "body_focus"],
            "calendar": ["wellness_calendar_with_fitness_accents", "weekly_frequency_calendar"],
            "strength": ["health_and_strength_emblem", "fitness_level_dumbbell", "equipment_dumbbell"],
            "checklist": ["botanical_checklist_icon_with_gold_accents", "questionnaire_clipboard"],
            "wellness": ["elegant_wellness_emblem_with_botanical_accents", "safety_shield"],
            "rules": ["elegant_flowchart_icon_with_leaf_accents", "expert_rules_flow"],
            "bmi": ["health_meter_with_botanical_accents", "bmi_scale"],
            "equipment": ["elegant_fitness_emblem_with_gold_accents", "health_and_strength_emblem"],
            "result": ["elegant_trophy_with_botanical_accents", "result_trophy"],
        }

        self.build_asset_lookup()

        self.questions = [
            {
                "key": "fitness_level",
                "icon": "strength",
                "type": "single",
                "question": "What is your current fitness level?",
                "subtitle": "Choose the option that best describes your exercise experience.",
                "why": "Fitness level helps the system recommend a suitable workout difficulty.",
                "options": [
                    ("Beginner", "New to exercise or has limited experience"),
                    ("Intermediate", "Exercises regularly with some experience"),
                    ("Advanced", "Highly experienced and can perform advanced workouts"),
                ],
            },
            {
                "key": "activity_level",
                "icon": "walking",
                "type": "single",
                "question": "What is your lifestyle activity level?",
                "subtitle": "Choose the option that best describes your daily activity.",
                "why": "Daily activity level helps the system decide whether the workout plan should start gradually or actively.",
                "options": [
                    ("Sedentary", "Mostly inactive or sitting for long hours"),
                    ("Lightly active", "Some daily movement or light activity"),
                    ("Active", "Regularly active in daily routine"),
                ],
            },
            {
                "key": "health_condition",
                "icon": "health",
                "type": "single",
                "question": "Do you have any serious health condition?",
                "subtitle": "This helps the system apply the right safety consideration.",
                "why": "This prevents unsafe recommendations for users who may need professional medical advice.",
                "options": [
                    ("Yes", "The system will apply extra safety consideration"),
                    ("No", "No serious health condition selected"),
                ],
            },
            {
                "key": "medical_restriction",
                "icon": "restriction",
                "type": "single",
                "question": "Do you have any medical restriction?",
                "subtitle": "This helps the system avoid exercises that may need modification.",
                "why": "Medical restrictions help the system avoid exercises that may conflict with the user’s condition.",
                "options": [
                    ("Yes", "Some exercises may need to be avoided or modified"),
                    ("No", "No medical restriction selected"),
                ],
            },
            {
                "key": "injury",
                "icon": "injury",
                "type": "multiple",
                "question": "Do you have any injury?",
                "subtitle": "Select any injury areas so the system can avoid risky exercises.",
                "why": "Injury status helps the system avoid movements that may worsen discomfort or injury.",
                "options": [
                    ("No injury", "No current injury selected"),
                    ("Knee injury", "Avoid high-impact movements"),
                    ("Back injury", "Avoid heavy lifting and excessive bending"),
                    ("Shoulder / Arm injury", "Avoid risky upper-body strain"),
                    ("Leg injury", "Avoid exercises that stress the leg"),
                ],
            },
            {
                "key": "goal",
                "icon": "goal",
                "type": "single",
                "question": "What is your main fitness goal?",
                "subtitle": "Choose the main goal you want your plan to focus on.",
                "why": "The system needs one main goal to decide the direction of the workout recommendation.",
                "options": [
                    ("Weight loss", "Focus on calorie-burning and cardio-based training"),
                    ("Muscle gain", "Focus on strength and resistance training"),
                    ("General fitness", "Focus on balanced overall health"),
                    ("Flexibility", "Focus on mobility and stretching"),
                    ("Stamina improvement", "Focus on endurance and cardiovascular fitness"),
                ],
            },
            {
                "key": "preference",
                "icon": "running",
                "type": "multiple",
                "question": "What type of workout do you prefer?",
                "subtitle": "Choose the training style you enjoy most.",
                "why": "Workout preference helps the system suggest exercises the user is more likely to follow.",
                "options": [
                    ("Cardio", "Walking, cycling, jogging, or endurance exercises"),
                    ("Strength training", "Resistance, bodyweight, or weight training"),
                    ("Yoga / Stretching", "Flexibility, mobility, and stretching exercises"),
                    ("Mixed workout", "Combination of cardio, strength, and flexibility"),
                ],
            },
            {
                "key": "target_area",
                "icon": "body_focus",
                "type": "single_grid",
                "question": "Which body area do you want to focus on?",
                "subtitle": "Choose the primary area your workout plan should emphasize.",
                "why": "Target area helps the system select exercises for the correct body part.",
                "options": [
                    ("Full body", "Overall body workout"),
                    ("Upper body", "Chest, shoulders, back, and arms"),
                    ("Lower body", "Legs and glutes"),
                    ("Core / Abs", "Abdominal and core stability"),
                    ("Arms", "Arm-focused resistance exercises"),
                    ("Legs", "Leg-focused exercises"),
                ],
            },
            {
                "key": "frequency",
                "icon": "calendar",
                "type": "single",
                "question": "How many days per week can you exercise?",
                "subtitle": "Choose the schedule that best fits your routine.",
                "why": "Workout frequency helps the system assign a light, moderate, or active weekly schedule.",
                "options": [
                    ("1 - 2 days", "Light weekly schedule"),
                    ("3 - 4 days", "Moderate weekly schedule"),
                    ("5 - 6 days", "Active weekly schedule"),
                ],
            },
            {
                "key": "equipment",
                "icon": "equipment",
                "type": "single",
                "question": "What equipment do you have?",
                "subtitle": "Select the equipment available to personalize your workout plan.",
                "why": "Equipment availability helps the system choose bodyweight, home-based, or gym-based exercises.",
                "options": [
                    ("No equipment", "Bodyweight exercises will be recommended"),
                    ("Home equipment", "Dumbbells, resistance bands, or simple equipment"),
                    ("Gym equipment", "Machine-based and weight training can be recommended"),
                ],
            },
        ]

        self.after(100, self.show_learning_page)

    # ==========================================================
    # FULLSCREEN + ASSET FUNCTIONS
    # ==========================================================

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)

    def normalize_name(self, text):
        return re.sub(r"[^a-z0-9]", "", text.lower())

    def assets_dir(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    def build_asset_lookup(self):
        folder = self.assets_dir()
        if not os.path.exists(folder):
            return

        for filename in os.listdir(folder):
            name, ext = os.path.splitext(filename)
            if ext.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                self.asset_lookup[self.normalize_name(name)] = os.path.join(folder, filename)

    def find_asset(self, logical_key):
        aliases = self.icon_aliases.get(logical_key, [logical_key])

        for alias in aliases:
            key = self.normalize_name(alias)
            if key in self.asset_lookup:
                return self.asset_lookup[key]

        for alias in aliases:
            key = self.normalize_name(alias)
            for saved_key, path in self.asset_lookup.items():
                if key in saved_key or saved_key in key:
                    return path

        return None

    def remove_light_background(self, image):
        image = image.convert("RGBA")
        pixels = image.load()

        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]
                if r > 218 and g > 218 and b > 205:
                    pixels[x, y] = (255, 255, 255, 0)

        bbox = image.getbbox()
        if bbox:
            image = image.crop(bbox)

        return image

    def get_icon_image(self, logical_key, size):
        cache_key = ("icon", logical_key, size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        path = self.find_asset(logical_key)
        if not path:
            return None

        img = Image.open(path).convert("RGBA")
        img = self.remove_light_background(img)
        img.thumbnail(size, Image.LANCZOS)

        canvas = Image.new("RGBA", size, (255, 255, 255, 0))
        x = (size[0] - img.width) // 2
        y = (size[1] - img.height) // 2
        canvas.paste(img, (x, y), img)

        ctk_img = ctk.CTkImage(light_image=canvas, size=size)
        self.image_cache[cache_key] = ctk_img
        return ctk_img

    def get_background_image(self, logical_key, size):
        cache_key = ("background", logical_key, size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        path = self.find_asset(logical_key)
        if not path:
            return None

        img = Image.open(path).convert("RGBA")
        img = ImageOps.fit(img, size, method=Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, size=size)
        self.image_cache[cache_key] = ctk_img
        return ctk_img

    def icon_box(self, parent, logical_key, x, y, size=58, image_size=40, bg_color=None):
        bg_color = bg_color or self.green_soft

        box = ctk.CTkFrame(
            parent,
            width=size,
            height=size,
            fg_color=bg_color,
            corner_radius=12,
            border_width=1,
            border_color="#E2D9C8",
        )
        box.place(x=x, y=y)

        img = self.get_icon_image(logical_key, (image_size, image_size))
        if img:
            ctk.CTkLabel(
                box,
                image=img,
                text="",
                width=size,
                height=size,
                fg_color="transparent",
            ).place(x=0, y=0)
        else:
            ctk.CTkLabel(
                box,
                text="✓",
                width=size,
                height=size,
                font=("Segoe UI", 18, "bold"),
                text_color=self.green,
            ).place(x=0, y=0)

        return box

    def get_option_icon_key(self, question_key, option):
        icon_map = {
            "fitness_level": {
                "Beginner": "strength",
                "Intermediate": "progress",
                "Advanced": "equipment",
            },
            "activity_level": {
                "Sedentary": "profile",
                "Lightly active": "walking",
                "Active": "running",
            },
            "health_condition": {
                "Yes": "health",
                "No": "wellness",
            },
            "medical_restriction": {
                "Yes": "restriction",
                "No": "checklist",
            },
            "injury": {
                "No injury": "checklist",
                "Knee injury": "injury",
                "Back injury": "injury",
                "Shoulder / Arm injury": "injury",
                "Leg injury": "injury",
            },
            "goal": {
                "Weight loss": "goal",
                "Muscle gain": "strength",
                "General fitness": "wellness",
                "Flexibility": "walking",
                "Stamina improvement": "running",
            },
            "preference": {
                "Cardio": "running",
                "Strength training": "strength",
                "Yoga / Stretching": "wellness",
                "Mixed workout": "equipment",
            },
            "target_area": {
                "Full body": "body_focus",
                "Upper body": "strength",
                "Lower body": "body_focus",
                "Core / Abs": "wellness",
                "Arms": "strength",
                "Legs": "running",
            },
            "frequency": {
                "1 - 2 days": "calendar",
                "3 - 4 days": "calendar",
                "5 - 6 days": "progress",
            },
            "equipment": {
                "No equipment": "checklist",
                "Home equipment": "equipment",
                "Gym equipment": "strength",
            },
        }

        return icon_map.get(question_key, {}).get(option, "checklist")

    # ==========================================================
    # GENERAL UI FUNCTIONS
    # ==========================================================

    def clear_screen(self):
        self.preview_running = False
        for widget in self.winfo_children():
            widget.destroy()

    def set_background(self):
        self.update_idletasks()
        window_w = max(self.winfo_width(), self.design_w)
        window_h = max(self.winfo_height(), self.design_h)

        bg_img = self.get_background_image("background", (window_w, window_h))
        if bg_img:
            ctk.CTkLabel(
                self,
                image=bg_img,
                text="",
                width=window_w,
                height=window_h,
            ).place(x=0, y=0)
        else:
            self.configure(fg_color=self.bg)

        self.stage = ctk.CTkFrame(
            self,
            width=self.design_w,
            height=self.design_h,
            fg_color="transparent",
        )
        self.stage.place(relx=0.5, rely=0.5, anchor="center")

    def create_header(self):
        header = ctk.CTkFrame(
            self.stage,
            width=1180,
            height=96,
            fg_color="#FFFDF8",
            corner_radius=0,
            border_width=0,
        )
        header.place(x=0, y=0)

        ctk.CTkFrame(header, width=1180, height=1, fg_color="#CDAA6A").place(x=0, y=95)
        self.icon_box(header, "logo", 48, 18, size=62, image_size=52, bg_color=self.green_soft)

        ctk.CTkLabel(
            header,
            text="Workout & Fitness",
            width=430,
            height=35,
            font=("Georgia", 24, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=125, y=18)

        ctk.CTkLabel(
            header,
            text="Recommendation Expert System",
            width=430,
            height=24,
            font=("Georgia", 14, "bold"),
            text_color=self.gold,
            anchor="w",
        ).place(x=126, y=52)

        badge = ctk.CTkFrame(
            header,
            width=280,
            height=38,
            fg_color="#FBF5EA",
            corner_radius=20,
            border_width=1,
            border_color="#E0CCAC",
        )
        badge.place(x=850, y=30)

        self.icon_box(badge, "wellness", 12, 8, size=22, image_size=16, bg_color="#FBF5EA")

        ctk.CTkLabel(
            badge,
            text="Rule-Based  •  Safe  •  Explainable",
            width=225,
            height=30,
            font=("Segoe UI", 10, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=44, y=5)

    def main_card(self, width=900, height=570, x=140, y=145):
        card = ctk.CTkFrame(
            self.stage,
            width=width,
            height=height,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=1,
            border_color="#E3D6C4",
        )
        card.place(x=x, y=y)
        return card

    def button(self, parent, text, command, primary=True, width=160):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=45,
            corner_radius=10,
            fg_color=self.green if primary else self.soft,
            hover_color=self.green_dark if primary else "#E1D6C5",
            text_color="white" if primary else self.text,
            font=("Segoe UI", 11, "bold"),
            border_width=1 if not primary else 0,
            border_color="#D4BF9C",
        )

    def popup(self, title, content, width=720, height=500):
        pop = ctk.CTkToplevel(self)
        pop.title(title)
        pop.geometry(f"{width}x{height}")
        pop.resizable(False, False)
        pop.configure(fg_color=self.bg)
        pop.transient(self)
        pop.grab_set()

        box = ctk.CTkFrame(
            pop,
            width=width - 44,
            height=height - 44,
            fg_color="#FFFFFF",
            corner_radius=18,
            border_width=1,
            border_color=self.border,
        )
        box.place(x=22, y=22)

        self.icon_box(
            box,
            "rules" if "How" in title or "Reason" in title else "checklist",
            28,
            24,
            size=46,
            image_size=32,
        )

        ctk.CTkLabel(
            box,
            text=title,
            width=width - 150,
            height=40,
            font=("Georgia", 21, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=88, y=28)

        textbox = ctk.CTkTextbox(
            box,
            width=width - 100,
            height=height - 175,
            fg_color="#FFFFFF",
            text_color=self.text,
            border_width=0,
            font=("Segoe UI", 11),
            wrap="word",
        )
        textbox.place(x=35, y=90)
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")

        self.button(box, "Close", pop.destroy, True, 120).place(
            x=(width - 44) / 2 - 60,
            y=height - 105,
        )

    # ==========================================================
    # LEARNING PAGE
    # ==========================================================

    def show_learning_page(self):
        self.clear_screen()
        self.set_background()
        self.create_header()

        card = ctk.CTkFrame(
            self.stage,
            width=930,
            height=570,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=1,
            border_color="#E3D6C4",
        )
        card.place(x=125, y=145)

        ctk.CTkLabel(
            card,
            text="Workout & Fitness\nRecommendation Expert System",
            width=450,
            height=85,
            font=("Georgia", 27, "bold"),
            text_color=self.green,
            justify="left",
            anchor="w",
        ).place(x=45, y=35)

        ctk.CTkFrame(card, width=300, height=2, fg_color="#D1A55D").place(x=45, y=130)

        ctk.CTkLabel(
            card,
            text="Personalized workout guidance powered by forward chaining expert rules.",
            width=500,
            height=28,
            font=("Segoe UI", 11, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=45, y=150)

        intro = (
            "This system recommends a suitable workout plan using your profile, BMI, "
            "fitness level, health condition, injury status, workout preference, "
            "weekly frequency, and available equipment."
        )

        ctk.CTkLabel(
            card,
            text=intro,
            width=460,
            height=70,
            font=("Segoe UI", 11),
            text_color=self.text,
            wraplength=455,
            justify="left",
            anchor="w",
        ).place(x=45, y=190)

        features = [
            ("Enter profile details", "Age, gender, weight, and height are used to calculate BMI.", "profile"),
            ("Apply expert rules", "The system uses IF-THEN rules and forward chaining.", "rules"),
            ("Safety override", "BMI conflict, health condition, restriction, and injury can modify the output.", "wellness"),
            ("Get recommendation", "A workout plan, intensity, frequency, exercises, and safety note are generated.", "result"),
        ]

        y = 265
        for title, desc, icon_key in features:
            self.icon_box(card, icon_key, 45, y, size=48, image_size=32, bg_color=self.green_soft)

            ctk.CTkLabel(
                card,
                text=title,
                width=350,
                height=20,
                font=("Segoe UI", 11, "bold"),
                text_color=self.text,
                anchor="w",
            ).place(x=110, y=y + 4)

            ctk.CTkLabel(
                card,
                text=desc,
                width=390,
                height=24,
                font=("Segoe UI", 9),
                text_color=self.muted,
                anchor="w",
            ).place(x=110, y=y + 27)

            y += 56

        guide = ctk.CTkFrame(
            card,
            width=420,
            height=58,
            fg_color=self.green_soft,
            corner_radius=12,
            border_width=1,
            border_color="#D7E3D3",
        )
        guide.place(x=45, y=440)

        ctk.CTkLabel(
            guide,
            text="[?] Why asked?  Explains why a question is needed.\n[i] View Reasoning  Shows how the conclusion is reached.",
            width=390,
            height=44,
            font=("Segoe UI", 9, "bold"),
            text_color=self.green,
            justify="left",
            anchor="w",
        ).place(x=18, y=7)

        self.button(card, "Start Recommendation  →", self.show_profile_page, True, 230).place(x=45, y=510)

        visual = ctk.CTkFrame(
            card,
            width=360,
            height=455,
            fg_color="#FBFAF4",
            corner_radius=18,
            border_width=1,
            border_color="#D9C8AA",
        )
        visual.place(x=535, y=55)

        hero_circle = ctk.CTkFrame(
            visual,
            width=250,
            height=250,
            fg_color="#EEF4EA",
            corner_radius=125,
            border_width=1,
            border_color="#D7C69C",
        )
        hero_circle.place(x=55, y=70)

        hero_img = self.get_icon_image("logo", (175, 175))
        if hero_img:
            ctk.CTkLabel(
                hero_circle,
                image=hero_img,
                text="",
                width=250,
                height=250,
                fg_color="transparent",
            ).place(x=0, y=0)

        ctk.CTkLabel(
            visual,
            text="Safe guidance • BMI calculation\nClear rule-based reasoning",
            width=310,
            height=60,
            font=("Georgia", 14, "italic"),
            text_color=self.green,
            justify="center",
        ).place(x=25, y=350)

        ctk.CTkLabel(
            self.stage,
            text="Note: This system provides general workout guidance only and does not replace doctors or certified trainers.",
            width=650,
            height=22,
            font=("Segoe UI", 9, "italic"),
            text_color=self.warning,
            anchor="center",
        ).place(x=265, y=740)

    # ==========================================================
    # PROFILE PAGE + BMI
    # ==========================================================

    def show_profile_page(self):
        self.clear_screen()
        self.set_background()
        self.create_header()

        card = self.main_card()

        self.icon_box(card, "profile", 55, 35, size=62, image_size=42, bg_color=self.green_soft)

        ctk.CTkLabel(
            card,
            text="Personal Information",
            width=520,
            height=42,
            font=("Georgia", 27, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=135, y=40)

        ctk.CTkLabel(
            card,
            text="Enter your details so the system can calculate BMI and personalize the recommendation.",
            width=600,
            height=25,
            font=("Segoe UI", 11),
            text_color=self.muted,
            anchor="w",
        ).place(x=135, y=83)

        ctk.CTkButton(
            card,
            text="ⓘ   Why asked?",
            command=lambda: self.popup(
                "Why is this information asked?",
                "Age, gender, weight, and height help the system create a basic user profile. "
                "Weight and height are used to calculate BMI automatically. BMI is used only "
                "as a general screening indicator, not as a medical diagnosis.",
                590,
                320,
            ),
            width=130,
            height=36,
            corner_radius=8,
            fg_color=self.surface,
            hover_color=self.soft,
            text_color=self.green,
            font=("Segoe UI", 10, "bold"),
            border_width=1,
            border_color="#D6BE98",
        ).place(x=720, y=55)

        form = ctk.CTkFrame(
            card,
            width=430,
            height=330,
            fg_color=self.surface,
            corner_radius=14,
            border_width=1,
            border_color=self.border,
        )
        form.place(x=55, y=140)

        self.age_entry = self.form_entry(form, "Age", "Example: 22", 30, 30, "calendar")
        self.gender_combo = self.form_combo(form, "Gender", ["Female", "Male", "Prefer not to say"], 30, 105, "profile")
        self.weight_entry = self.form_entry(form, "Weight (kg)", "Example: 55", 30, 180, "bmi")
        self.height_entry = self.form_entry(form, "Height (cm)", "Example: 160", 30, 255, "progress")

        if self.profile:
            self.age_entry.insert(0, str(self.profile.get("age", "")))
            self.gender_combo.set(self.profile.get("gender", "Female"))
            self.weight_entry.insert(0, str(self.profile.get("weight", "")))
            self.height_entry.insert(0, str(self.profile.get("height", "")))
        else:
            self.gender_combo.set("Female")

        info = ctk.CTkFrame(
            card,
            width=350,
            height=330,
            fg_color="#FFFEFA",
            corner_radius=14,
            border_width=1,
            border_color=self.border,
        )
        info.place(x=530, y=140)

        self.icon_box(info, "bmi", 125, 25, size=90, image_size=68, bg_color=self.green_soft)

        ctk.CTkLabel(
            info,
            text="Live BMI Preview",
            width=300,
            height=28,
            font=("Georgia", 17, "bold"),
            text_color=self.green,
            anchor="center",
        ).place(x=25, y=125)

        ctk.CTkFrame(info, width=220, height=1, fg_color="#D6B16C").place(x=65, y=160)

        self.bmi_value_label = ctk.CTkLabel(
            info,
            text="Enter weight and height",
            width=300,
            height=45,
            font=("Georgia", 22, "bold"),
            text_color=self.gold,
            anchor="center",
        )
        self.bmi_value_label.place(x=25, y=175)

        self.bmi_category_label = ctk.CTkLabel(
            info,
            text="BMI category will appear here",
            width=300,
            height=28,
            font=("Segoe UI", 12, "bold"),
            text_color=self.green,
            anchor="center",
        )
        self.bmi_category_label.place(x=25, y=220)

        self.bmi_note_label = ctk.CTkLabel(
            info,
            text="BMI is a general screening indicator only.",
            width=290,
            height=45,
            font=("Segoe UI", 9, "italic"),
            text_color=self.muted,
            wraplength=285,
            justify="center",
            anchor="center",
        )
        self.bmi_note_label.place(x=30, y=265)

        self.age_entry.bind("<KeyRelease>", lambda event: self.update_bmi_preview())
        self.weight_entry.bind("<KeyRelease>", lambda event: self.update_bmi_preview())
        self.height_entry.bind("<KeyRelease>", lambda event: self.update_bmi_preview())
        self.update_bmi_preview()

        ctk.CTkFrame(card, width=820, height=1, fg_color=self.soft).place(x=45, y=495)
        self.button(card, "‹  Back", self.show_learning_page, False, 140).place(x=55, y=520)
        self.button(card, "Next  ›", self.validate_profile, True, 160).place(x=700, y=520)

    def update_bmi_preview(self):
        try:
            age_text = self.age_entry.get().strip()
            weight_text = self.weight_entry.get().strip()
            height_text = self.height_entry.get().strip()

            if weight_text == "" or height_text == "":
                self.bmi_value_label.configure(text="Enter weight and height", text_color=self.gold)
                self.bmi_category_label.configure(text="BMI category will appear here", text_color=self.green)
                return

            weight = float(weight_text)
            height_cm = float(height_text)

            if weight <= 0 or height_cm <= 0:
                raise ValueError

            height_m = height_cm / 100
            bmi = weight / (height_m ** 2)
            age = int(age_text) if age_text else None
            category = self.get_bmi_category(bmi, age)

            self.bmi_value_label.configure(text=f"BMI: {bmi:.1f}", text_color=self.green)
            self.bmi_category_label.configure(text=f"Category: {category}", text_color=self.green)

        except Exception:
            self.bmi_value_label.configure(text="Invalid BMI input", text_color=self.warning)
            self.bmi_category_label.configure(text="Please check weight/height", text_color=self.warning)

    def form_entry(self, parent, label, placeholder, x, y, icon_key):
        self.icon_box(parent, icon_key, x, y + 22, size=42, image_size=28, bg_color=self.green_soft)

        ctk.CTkLabel(
            parent,
            text=label,
            width=160,
            height=20,
            font=("Segoe UI", 10, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=x + 58, y=y)

        entry = ctk.CTkEntry(
            parent,
            width=320,
            height=38,
            corner_radius=8,
            border_color=self.border,
            fg_color="#FFFFFF",
            text_color=self.text,
            placeholder_text=placeholder,
            font=("Segoe UI", 11),
        )
        entry.place(x=x + 58, y=y + 24)
        return entry

    def form_combo(self, parent, label, values, x, y, icon_key):
        self.icon_box(parent, icon_key, x, y + 22, size=42, image_size=28, bg_color=self.green_soft)

        ctk.CTkLabel(
            parent,
            text=label,
            width=160,
            height=20,
            font=("Segoe UI", 10, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=x + 58, y=y)

        combo = ctk.CTkComboBox(
            parent,
            width=320,
            height=38,
            corner_radius=8,
            border_color=self.border,
            fg_color="#FFFFFF",
            button_color=self.green,
            button_hover_color=self.green_dark,
            values=values,
            text_color=self.text,
            font=("Segoe UI", 11),
        )
        combo.place(x=x + 58, y=y + 24)
        return combo

    def validate_profile(self):
        try:
            age = int(self.age_entry.get().strip())
            weight = float(self.weight_entry.get().strip())
            height_cm = float(self.height_entry.get().strip())
            gender = self.gender_combo.get().strip()

            if age < 10 or age > 100:
                raise ValueError("Age must be between 10 and 100.")
            if weight < 20 or weight > 250:
                raise ValueError("Weight must be between 20 kg and 250 kg.")
            if height_cm < 100 or height_cm > 230:
                raise ValueError("Height must be between 100 cm and 230 cm.")
            if gender == "":
                raise ValueError("Please select gender.")

            height_m = height_cm / 100
            bmi = weight / (height_m ** 2)

            self.profile = {
                "age": age,
                "age_group": self.get_age_group(age),
                "gender": gender,
                "weight": weight,
                "height": height_cm,
                "bmi": round(bmi, 1),
                "bmi_category": self.get_bmi_category(bmi, age),
            }

            self.current_question = 0
            self.show_question_page()

        except ValueError as error:
            self.popup(
                "Invalid Input",
                f"Please enter valid personal information.\n\nDetails: {error}",
                520,
                300,
            )

    def get_age_group(self, age):
        if age < 18:
            return "Below 18"
        if age <= 30:
            return "18 - 30"
        if age <= 50:
            return "31 - 50"
        return "Above 50"

    def get_bmi_category(self, bmi, age=None):
        if age is not None and age < 18:
            return "Youth BMI needs percentile"
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal"
        if bmi < 30:
            return "Overweight"
        return "Obese"

    # ==========================================================
    # QUESTION PAGE
    # ==========================================================

    def show_question_page(self):
        self.clear_screen()
        self.set_background()
        self.create_header()

        card = self.main_card()
        self.option_cards = []

        q = self.questions[self.current_question]
        key = q["key"]

        self.temp_answer = self.answers.get(
            key,
            "" if q["type"] in ["single", "single_grid"] else [],
        )

        ctk.CTkLabel(
            card,
            text=f"Question {self.current_question + 1} of {len(self.questions)}",
            width=220,
            height=24,
            font=("Georgia", 13, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=55, y=32)

        progress = ctk.CTkProgressBar(
            card,
            width=580,
            height=8,
            corner_radius=8,
            fg_color=self.soft,
            progress_color=self.green,
        )
        progress.place(x=55, y=62)

        progress_value = (self.current_question + 1) / len(self.questions)
        progress.set(progress_value)

        ctk.CTkLabel(
            card,
            text=f"{int(progress_value * 100)}%",
            width=50,
            height=20,
            font=("Segoe UI", 11, "bold"),
            text_color=self.green,
        ).place(x=645, y=55)

        ctk.CTkButton(
            card,
            text="ⓘ   Why asked?",
            command=lambda: self.popup("Why is this question asked?", q["why"], 560, 310),
            width=130,
            height=36,
            corner_radius=8,
            fg_color=self.surface,
            hover_color=self.soft,
            text_color=self.green,
            font=("Segoe UI", 10, "bold"),
            border_width=1,
            border_color="#D6BE98",
        ).place(x=730, y=45)

        self.icon_box(card, q["icon"], 55, 100, size=62, image_size=42, bg_color=self.green_soft)

        ctk.CTkLabel(
            card,
            text=q["question"],
            width=710,
            height=42,
            font=("Georgia", 25, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=135, y=104)

        ctk.CTkLabel(
            card,
            text=q["subtitle"],
            width=710,
            height=24,
            font=("Segoe UI", 11),
            text_color=self.muted,
            anchor="w",
        ).place(x=135, y=145)

        if q["type"] == "single_grid":
            self.create_grid_options(card, q)
        else:
            self.create_list_options(card, q)

        hint = "Multiple selection is allowed for this question." if q["type"] == "multiple" else "Select one option to continue."

        ctk.CTkLabel(
            card,
            text=f"❧   {hint}",
            width=600,
            height=24,
            font=("Segoe UI", 9, "italic"),
            text_color=self.muted,
            anchor="w",
        ).place(x=55, y=472)

        ctk.CTkFrame(card, width=585, height=1, fg_color=self.soft).place(x=240, y=485)

        back_command = self.show_profile_page if self.current_question == 0 else self.go_back
        self.button(card, "‹  Back", back_command, False, 140).place(x=55, y=505)

        next_text = "Generate Result  →" if self.current_question == len(self.questions) - 1 else "Next  ›"
        self.button(card, next_text, self.go_next, True, 160).place(x=700, y=505)

        self.refresh_cards()

    def create_list_options(self, parent, question):
        option_count = len(question["options"])
        height = 48 if option_count >= 5 else 58
        gap = 6 if option_count >= 5 else 9
        start_y = 185

        for index, (option, desc) in enumerate(question["options"]):
            y = start_y + index * (height + gap)

            frame = ctk.CTkFrame(
                parent,
                width=805,
                height=height,
                fg_color="#FFFFFF",
                corner_radius=10,
                border_width=1,
                border_color=self.border,
            )
            frame.place(x=55, y=y)

            mark = ctk.CTkLabel(
                frame,
                text="○",
                width=32,
                height=32,
                font=("Segoe UI", 18),
                text_color=self.muted,
            )
            mark.place(x=18, y=(height - 32) // 2)

            icon_circle = self.icon_box(
                frame,
                self.get_option_icon_key(question["key"], option),
                62,
                (height - 42) // 2,
                size=42,
                image_size=28,
                bg_color=self.green_soft,
            )

            title = ctk.CTkLabel(
                frame,
                text=option,
                width=430,
                height=20,
                font=("Georgia", 11, "bold"),
                text_color=self.text,
                anchor="w",
            )
            title.place(x=125, y=7)

            subtitle = ctk.CTkLabel(
                frame,
                text=desc,
                width=560,
                height=18,
                font=("Segoe UI", 8 if option_count >= 5 else 9),
                text_color=self.muted,
                anchor="w",
            )
            subtitle.place(x=125, y=28)

            item = {
                "frame": frame,
                "mark": mark,
                "icon": icon_circle,
                "title": title,
                "subtitle": subtitle,
                "value": option,
            }
            self.option_cards.append(item)

            for widget in [frame, mark, icon_circle, title, subtitle]:
                widget.bind("<Button-1>", lambda event, value=option: self.select_option(value))

    def create_grid_options(self, parent, question):
        positions = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]
        start_x = 55
        start_y = 185
        width = 385
        height = 76
        gap_x = 25
        gap_y = 12

        for index, (option, desc) in enumerate(question["options"]):
            col, row = positions[index]
            x = start_x + col * (width + gap_x)
            y = start_y + row * (height + gap_y)

            frame = ctk.CTkFrame(
                parent,
                width=width,
                height=height,
                fg_color="#FFFFFF",
                corner_radius=10,
                border_width=1,
                border_color=self.border,
            )
            frame.place(x=x, y=y)

            icon_circle = self.icon_box(
                frame,
                self.get_option_icon_key(question["key"], option),
                20,
                17,
                size=42,
                image_size=29,
                bg_color=self.green_soft,
            )

            title = ctk.CTkLabel(
                frame,
                text=option,
                width=210,
                height=22,
                font=("Georgia", 12, "bold"),
                text_color=self.text,
                anchor="w",
            )
            title.place(x=78, y=17)

            subtitle = ctk.CTkLabel(
                frame,
                text=desc,
                width=250,
                height=22,
                font=("Segoe UI", 9),
                text_color=self.muted,
                anchor="w",
            )
            subtitle.place(x=78, y=42)

            mark = ctk.CTkLabel(
                frame,
                text="",
                width=28,
                height=28,
                fg_color="#FFFFFF",
                corner_radius=14,
                text_color="white",
                font=("Segoe UI", 13, "bold"),
            )
            mark.place(x=338, y=24)

            item = {
                "frame": frame,
                "mark": mark,
                "icon": icon_circle,
                "title": title,
                "subtitle": subtitle,
                "value": option,
            }
            self.option_cards.append(item)

            for widget in [frame, icon_circle, title, subtitle, mark]:
                widget.bind("<Button-1>", lambda event, value=option: self.select_option(value))

    def is_selected(self, value):
        q = self.questions[self.current_question]
        if q["type"] == "multiple":
            return value in self.temp_answer
        return self.temp_answer == value

    def select_option(self, value):
        q = self.questions[self.current_question]
        key = q["key"]

        if q["type"] in ["single", "single_grid"]:
            self.temp_answer = value
        else:
            if key == "injury":
                if value == "No injury":
                    self.temp_answer = ["No injury"]
                else:
                    if "No injury" in self.temp_answer:
                        self.temp_answer.remove("No injury")
                    self.toggle(value)
            else:
                self.toggle(value)

        self.refresh_cards()

    def toggle(self, value):
        if value in self.temp_answer:
            self.temp_answer.remove(value)
        else:
            self.temp_answer.append(value)

    def refresh_cards(self):
        q = self.questions[self.current_question]

        for item in self.option_cards:
            selected = self.is_selected(item["value"])

            item["frame"].configure(
                fg_color=self.green_soft if selected else "#FFFFFF",
                border_color=self.green if selected else self.border,
                border_width=2 if selected else 1,
            )

            item["icon"].configure(fg_color="#DDEAD8" if selected else self.green_soft)
            item["title"].configure(text_color=self.green if selected else self.text)

            if selected:
                item["mark"].configure(text="✓", fg_color=self.green, text_color="white")
            else:
                if q["type"] in ["single", "single_grid"]:
                    item["mark"].configure(text="○", fg_color="#FFFFFF", text_color=self.muted)
                else:
                    item["mark"].configure(text="", fg_color="#FFFFFF", text_color=self.muted)

    def go_back(self):
        self.current_question -= 1
        self.show_question_page()

    def go_next(self):
        q = self.questions[self.current_question]
        key = q["key"]

        if q["type"] in ["single", "single_grid"] and not self.temp_answer:
            self.popup("Input Required", "Please select one option before continuing.", 430, 260)
            return

        if q["type"] == "multiple" and not self.temp_answer:
            self.popup("Input Required", "Please select at least one option before continuing.", 430, 260)
            return

        self.answers[key] = self.temp_answer

        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question_page()
        else:
            self.generate_recommendation()
            self.show_result_page()

    # ==========================================================
    # EXPERT SYSTEM RULE ENGINE
    # ==========================================================

    def has(self, key, value):
        answer = self.answers.get(key)
        if isinstance(answer, list):
            return value in answer
        return answer == value

    def any_injury(self):
        injuries = self.answers.get("injury", [])
        return isinstance(injuries, list) and "No injury" not in injuries and len(injuries) > 0

    def add_rule(self, rule):
        if rule not in self.triggered_rules:
            self.triggered_rules.append(rule)

    def add_exercise(self, exercises, exercise):
        if exercise not in exercises:
            exercises.append(exercise)

    def remove_exercises_by_keywords(self, exercises, keywords):
        refined = []
        for exercise in exercises:
            exercise_lower = exercise.lower()
            should_remove = False
            for keyword in keywords:
                if keyword.lower() in exercise_lower:
                    should_remove = True
                    break
            if not should_remove:
                refined.append(exercise)
        return refined

    def generate_recommendation(self):
        self.triggered_rules = []

        age_group = self.profile.get("age_group")
        bmi_category = self.profile.get("bmi_category")
        fitness = self.answers.get("fitness_level")
        activity = self.answers.get("activity_level")
        health = self.answers.get("health_condition")
        restriction = self.answers.get("medical_restriction")
        goal = self.answers.get("goal")
        frequency = self.answers.get("frequency")
        equipment = self.answers.get("equipment")
        body_focus = self.answers.get("target_area")

        plan = "Balanced Fitness Plan"
        focus = "Overall Wellness"
        workout_type = "Mixed"
        intensity = "Moderate"
        schedule = "3 days per week"
        exercises = []
        safety_notes = ["Perform each exercise with proper form and stop if discomfort occurs."]
        safety_override_active = False

        def add_safety(note):
            if note not in safety_notes:
                safety_notes.append(note)

        # ==========================================================
        # R1 - R5: GOAL-BASED RULES
        # ==========================================================

        if goal == "Weight loss":
            plan = "Cardio-Focused Workout Plan"
            focus = "Cardio Endurance & Fat Burning"
            workout_type = "Cardio"
            exercises = ["Brisk walking", "Cycling", "Low-impact cardio"]
            self.add_rule("R1: Weight loss goal → cardio-focused workout")

        elif goal == "Muscle gain":
            plan = "Strength Training Plan"
            focus = "Strength & Muscle Building"
            workout_type = "Strength"
            exercises = ["Resistance training", "Bodyweight strength", "Dumbbell exercise"]
            self.add_rule("R2: Muscle gain goal → strength training")

        elif goal == "General fitness":
            plan = "Balanced Fitness Plan"
            focus = "Cardio + Strength + Mobility"
            workout_type = "Mixed"
            exercises = ["Walking", "Bodyweight movement", "Stretching"]
            self.add_rule("R3: General fitness goal → balanced workout")

        elif goal == "Flexibility":
            plan = "Flexibility & Mobility Plan"
            focus = "Mobility & Stretching"
            workout_type = "Flexibility"
            intensity = "Light"
            exercises = ["Yoga flow", "Static stretching", "Mobility exercise"]
            self.add_rule("R4: Flexibility goal → mobility plan")

        elif goal == "Stamina improvement":
            plan = "Cardio Endurance Plan"
            focus = "Endurance & Cardiovascular Fitness"
            workout_type = "Cardio"
            exercises = ["Walking intervals", "Cycling", "Endurance circuit"]
            self.add_rule("R5: Stamina goal → endurance workout")

        # ==========================================================
        # R6 - R7: SERIOUS HEALTH / MEDICAL RESTRICTION RULES
        # ==========================================================

        if health == "Yes":
            intensity = "Light"
            safety_override_active = True
            add_safety("Consult a doctor or certified trainer before starting a new workout plan.")
            self.add_rule("R6: Serious health condition → light intensity and professional advice")

        if restriction == "Yes":
            if intensity != "Light":
                intensity = "Light to Moderate"
            safety_override_active = True
            add_safety("Avoid exercises that conflict with your medical restriction.")
            self.add_rule("R7: Medical restriction → reduce intensity and modify risky exercises")

        # ==========================================================
        # R8 - R11: INJURY-SPECIFIC RULES
        # ==========================================================

        if self.has("injury", "Knee injury"):
            intensity = "Light to Moderate"
            workout_type = "Low Impact"
            safety_override_active = True
            exercises = ["Walking", "Cycling", "Seated leg raise", "Gentle stretching"]
            add_safety("Avoid jumping, running, squats, lunges and high-impact movements.")
            self.add_rule("R8: Knee injury → low-impact exercises")

        if self.has("injury", "Back injury"):
            intensity = "Light to Moderate"
            safety_override_active = True
            self.add_exercise(exercises, "Gentle mobility")
            self.add_exercise(exercises, "Bird dog")
            self.add_exercise(exercises, "Dead bug")
            add_safety("Avoid heavy lifting, excessive bending and twisting movements.")
            self.add_rule("R9: Back injury → mobility and core stability exercises")

        if self.has("injury", "Shoulder / Arm injury"):
            intensity = "Light to Moderate"
            safety_override_active = True
            exercises = self.remove_exercises_by_keywords(
                exercises,
                ["push-up", "row", "bicep", "dumbbell", "upper-body", "shoulder"],
            )
            self.add_exercise(exercises, "Walking")
            self.add_exercise(exercises, "Lower-body mobility")
            add_safety("Avoid upper-body movements that cause shoulder or arm discomfort.")
            self.add_rule("R10: Shoulder/arm injury → avoid upper-body strain")

        if self.has("injury", "Leg injury"):
            intensity = "Light to Moderate"
            workout_type = "Low Impact"
            safety_override_active = True
            exercises = self.remove_exercises_by_keywords(
                exercises,
                ["jump", "running", "sprint", "lunge", "squat", "treadmill"],
            )
            self.add_exercise(exercises, "Seated mobility")
            self.add_exercise(exercises, "Gentle stretching")
            add_safety("Avoid exercises that place excessive stress on the injured leg.")
            self.add_rule("R11: Leg injury → avoid stressful leg exercises")

        # ==========================================================
        # R12 - R17: AGE / FITNESS / BMI + GOAL SAFETY RULES
        # ==========================================================

        if age_group == "Above 50" and fitness == "Beginner":
            intensity = "Low to Moderate"
            self.add_exercise(exercises, "Low-impact cardio")
            add_safety("Older beginners should start gradually with controlled intensity.")
            self.add_rule("R12: Older beginner → low to moderate intensity")

        if fitness == "Beginner" and activity == "Sedentary":
            if not safety_override_active:
                plan = "Gradual Beginner Workout Plan"
            intensity = "Light"
            self.add_exercise(exercises, "Beginner mobility routine")
            self.add_rule("R13: Beginner + sedentary lifestyle → gradual plan")

        if goal == "Weight loss" and bmi_category == "Underweight":
            plan = "Healthy Weight Maintenance Plan"
            focus = "Healthy Weight Improvement"
            workout_type = "Mixed"
            intensity = "Light"
            safety_override_active = True
            exercises = ["Walking", "Light resistance training", "Mobility exercise"]
            add_safety("Weight loss is not recommended because the user is already underweight.")
            add_safety("Focus on maintaining or gradually improving healthy body weight.")
            self.add_rule("R14: Underweight BMI + weight loss goal → safety override")

        elif goal == "Weight loss" and bmi_category in ["Overweight", "Obese"]:
            plan = "Gradual Cardio Weight Loss Plan"
            intensity = "Light to Moderate"
            self.add_rule("R15: Weight loss goal + overweight/obese BMI → gradual cardio plan")

        elif goal == "Muscle gain" and bmi_category == "Underweight":
            plan = "Muscle-Building Workout Plan"
            focus = "Healthy Weight Gain & Strength Development"
            self.add_rule("R16: Muscle gain goal + underweight BMI → muscle-building plan")

        elif goal == "Muscle gain" and bmi_category == "Obese":
            plan = "Strength-Based Fat Reduction Plan"
            focus = "Body Recomposition"
            intensity = "Light to Moderate" if safety_override_active else "Moderate"
            add_safety("Focus on reducing excess body fat while improving strength rather than rapid weight gain.")
            self.add_rule("R17: Obese BMI + muscle gain goal → body recomposition plan")

        # ==========================================================
        # R18 - R22: WORKOUT PREFERENCE RULES
        # ==========================================================

        if self.has("preference", "Cardio"):
            self.add_exercise(exercises, "Walking")
            self.add_exercise(exercises, "Cycling")
            if not safety_override_active:
                workout_type = "Cardio"
            self.add_rule("R18: Cardio preference → prioritize cardio")

        if self.has("preference", "Strength training") and not self.any_injury() and health == "No" and restriction == "No":
            self.add_exercise(exercises, "Resistance training")
            self.add_exercise(exercises, "Bodyweight strength")
            workout_type = "Strength"
            self.add_rule("R19: Strength preference + no safety issue → resistance training")

        elif self.has("preference", "Strength training"):
            self.add_exercise(exercises, "Light resistance training")
            add_safety("Strength training is modified because a safety factor was detected.")
            self.add_rule("R20: Strength preference + safety issue → modified light resistance")

        if self.has("preference", "Yoga / Stretching"):
            self.add_exercise(exercises, "Stretching")
            self.add_exercise(exercises, "Yoga flow")
            self.add_rule("R21: Yoga/stretching preference → mobility exercises")

        if self.has("preference", "Mixed workout"):
            if not safety_override_active:
                workout_type = "Mixed"
            if not self.has("injury", "Back injury"):
                self.add_exercise(exercises, "Core exercise")
            self.add_rule("R22: Mixed preference → balanced workout")

        # ==========================================================
        # R23 - R33: BODY FOCUS RULES
        # ==========================================================

        if body_focus == "Full body":
            self.add_exercise(exercises, "Full-body circuit")
            self.add_rule("R23: Full body focus → full-body exercise")

        if body_focus == "Upper body":
            if not self.has("injury", "Shoulder / Arm injury"):
                self.add_exercise(exercises, "Wall push-up")
                self.add_exercise(exercises, "Resistance band row")
                self.add_rule("R24: Upper body focus → upper-body exercises")
            else:
                add_safety("Upper-body exercises are limited because shoulder/arm injury is selected.")
                self.add_rule("R25: Upper body focus + shoulder/arm injury → restrict upper-body exercises")

        if body_focus == "Lower body":
            if not self.has("injury", "Knee injury") and not self.has("injury", "Leg injury"):
                self.add_exercise(exercises, "Glute bridge")
                self.add_exercise(exercises, "Calf raises")
                self.add_rule("R26: Lower body focus → lower-body exercises")
            else:
                add_safety("Lower-body exercises are limited because knee/leg injury is selected.")
                self.add_rule("R27: Lower body focus + knee/leg injury → restrict lower-body exercises")

        if body_focus == "Core / Abs":
            if not self.has("injury", "Back injury"):
                self.add_exercise(exercises, "Dead bug")
                self.add_exercise(exercises, "Plank")
                self.add_rule("R28: Core focus → core strengthening")
            else:
                self.add_exercise(exercises, "Bird dog")
                add_safety("Core exercises are modified because back injury is selected.")
                self.add_rule("R29: Core focus + back injury → modified core exercises")

        if body_focus == "Arms":
            if not self.has("injury", "Shoulder / Arm injury"):
                self.add_exercise(exercises, "Bicep curls")
                self.add_rule("R30: Arms focus → arm exercises")
            else:
                add_safety("Arm exercises are limited because shoulder/arm injury is selected.")
                self.add_rule("R31: Arms focus + shoulder/arm injury → restrict arm exercises")

        if body_focus == "Legs":
            if not self.has("injury", "Knee injury") and not self.has("injury", "Leg injury"):
                self.add_exercise(exercises, "Glute bridge")
                self.add_exercise(exercises, "Calf raises")
                self.add_rule("R32: Legs focus → leg exercises")
            else:
                add_safety("Leg exercises are limited because knee/leg injury is selected.")
                self.add_rule("R33: Legs focus + knee/leg injury → restrict leg exercises")

        # ==========================================================
        # R34 - R36: EQUIPMENT RULES
        # ==========================================================

        if equipment == "No equipment":
            self.add_exercise(exercises, "Bodyweight movement")
            self.add_rule("R34: No equipment → bodyweight exercises")

        elif equipment == "Home equipment":
            self.add_exercise(exercises, "Resistance band exercise")
            self.add_exercise(exercises, "Light dumbbell exercise")
            self.add_rule("R35: Home equipment → home resistance exercises")

        elif equipment == "Gym equipment":
            self.add_exercise(exercises, "Stationary bike")
            if not self.has("injury", "Knee injury") and not self.has("injury", "Leg injury"):
                self.add_exercise(exercises, "Treadmill")
            else:
                add_safety("Treadmill is avoided because knee or leg injury was selected.")
            self.add_rule("R36: Gym equipment → machine-based exercises with safety check")

        # ==========================================================
        # R37 - R40: FREQUENCY + FINAL SAFETY FILTER
        # ==========================================================

        if frequency == "1 - 2 days":
            schedule = "1 - 2 days per week"
            if fitness == "Beginner" or safety_override_active:
                intensity = "Light"
            self.add_rule("R37: 1–2 days/week → light weekly schedule")

        elif frequency == "3 - 4 days":
            schedule = "3 - 4 days per week"
            self.add_rule("R38: 3–4 days/week → moderate weekly schedule")

        elif frequency == "5 - 6 days":
            schedule = "5 - 6 days per week"
            if health == "No" and restriction == "No" and not self.any_injury() and not safety_override_active and bmi_category != "Underweight":
                intensity = "Moderate to High"
            else:
                intensity = "Light to Moderate"
                add_safety("High weekly frequency is adjusted because safety factors are present.")
            self.add_rule("R39: 5–6 days/week → active weekly schedule with safety check")

        if intensity in ["High", "Moderate to High"] and (
            self.any_injury() or health == "Yes" or restriction == "Yes" or safety_override_active
        ):
            intensity = "Light to Moderate"
            add_safety("Final safety filter reduced the intensity to protect the user.")
            self.add_rule("R40: Final safety filter → reduce high intensity")

        # Final exercise safety cleanup after all rules have added exercises
        if self.has("injury", "Knee injury") or self.has("injury", "Leg injury"):
            exercises = self.remove_exercises_by_keywords(
                exercises,
                ["jump", "running", "sprint", "treadmill", "lunge", "squat"],
            )

        if self.has("injury", "Shoulder / Arm injury"):
            exercises = self.remove_exercises_by_keywords(
                exercises,
                ["push-up", "row", "bicep", "shoulder", "upper-body", "dumbbell"],
            )

        if self.has("injury", "Back injury"):
            exercises = self.remove_exercises_by_keywords(
                exercises,
                ["heavy", "deadlift"],
            )

        if not exercises:
            exercises = ["Walking", "Gentle stretching", "Mobility exercise"]

        self.add_rule("R41: Final evaluation → generate recommendation")

        self.final_result = {
            "plan": plan,
            "focus": focus,
            "workout_type": workout_type,
            "body_focus": body_focus,
            "equipment": equipment,
            "intensity": intensity,
            "schedule": schedule,
            "exercises": exercises[:5],
            "safety": "\n".join([f"• {note}" for note in safety_notes]),
        }

    # ==========================================================
    # RESULT PAGE
    # ==========================================================

    def show_result_page(self):
        self.clear_screen()
        self.set_background()
        self.create_header()

        card = ctk.CTkFrame(
            self.stage,
            width=960,
            height=610,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=1,
            border_color="#E3D6C4",
        )
        card.place(x=110, y=130)

        self.icon_box(card, "result", 45, 28, size=58, image_size=40, bg_color=self.green_soft)

        ctk.CTkLabel(
            card,
            text="Your Workout Recommendation",
            width=650,
            height=45,
            font=("Georgia", 27, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=115, y=34)

        result = self.final_result

        self.result_box(card, 45, 105, "Recommended Plan", result["plan"], "strength")
        self.result_box(card, 350, 105, "Calculated BMI", f"{self.profile['bmi']} ({self.profile['bmi_category']})", "bmi")
        self.result_box(card, 655, 105, "Workout Frequency", result["schedule"], "calendar")

        self.result_box(card, 45, 215, "Workout Type", result["workout_type"], "running")
        self.result_box(card, 350, 215, "Training Focus", result["focus"], "goal")
        self.result_box(card, 655, 215, "Intensity Level", result["intensity"], "rules")

        exercise_box = ctk.CTkFrame(
            card,
            width=370,
            height=150,
            fg_color=self.green_soft,
            corner_radius=12,
            border_width=1,
            border_color="#D6CCB8",
        )
        exercise_box.place(x=45, y=340)

        self.icon_box(exercise_box, "strength", 22, 20, size=46, image_size=30, bg_color="#DDEAD8")

        ctk.CTkLabel(
            exercise_box,
            text="Recommended Exercises",
            width=260,
            height=28,
            font=("Georgia", 14, "bold"),
            text_color=self.green,
            anchor="w",
        ).place(x=82, y=20)

        exercises_text = "\n".join([f"❧  {exercise}" for exercise in result["exercises"]])

        ctk.CTkLabel(
            exercise_box,
            text=exercises_text,
            width=300,
            height=92,
            font=("Segoe UI", 10),
            text_color=self.text,
            justify="left",
            anchor="w",
        ).place(x=62, y=55)

        preview_box = ctk.CTkFrame(
            card,
            width=230,
            height=150,
            fg_color="#FBFAF4",
            corner_radius=12,
            border_width=1,
            border_color="#D6CCB8",
        )
        preview_box.place(x=435, y=340)

        self.icon_box(preview_box, "progress", 92, 18, size=48, image_size=32, bg_color=self.green_soft)

        ctk.CTkLabel(
            preview_box,
            text="Workout Preview",
            width=200,
            height=25,
            font=("Georgia", 14, "bold"),
            text_color=self.green,
            anchor="center",
        ).place(x=15, y=70)

        self.preview_label = ctk.CTkLabel(
            preview_box,
            text="Preparing preview...",
            width=190,
            height=32,
            font=("Segoe UI", 11, "bold"),
            text_color=self.green,
            anchor="center",
            wraplength=180,
            fg_color=self.green_soft,
            corner_radius=18,
        )
        self.preview_label.place(x=20, y=105)

        self.preview_items = result["exercises"] if result["exercises"] else ["Walking", "Stretching"]
        self.preview_index = 0
        self.preview_running = True
        self.animate_preview()

        safety_box = ctk.CTkFrame(
            card,
            width=250,
            height=150,
            fg_color=self.warning_soft,
            corner_radius=12,
            border_width=1,
            border_color="#D6CCB8",
        )
        safety_box.place(x=685, y=340)

        self.icon_box(safety_box, "wellness", 25, 20, size=46, image_size=30, bg_color="#E9DCC6")

        ctk.CTkLabel(
            safety_box,
            text="Safety Reminder",
            width=160,
            height=28,
            font=("Georgia", 14, "bold"),
            text_color=self.warning,
            anchor="w",
        ).place(x=82, y=20)

        ctk.CTkLabel(
            safety_box,
            text=result["safety"],
            width=190,
            height=80,
            font=("Segoe UI", 9),
            text_color=self.text,
            wraplength=185,
            justify="left",
            anchor="center",
        ).place(x=32, y=62)

        self.button(card, "▣   View Reasoning", self.show_how, False, 180).place(x=270, y=515)
        self.button(card, "↻   Restart", self.restart, True, 170).place(x=470, y=515)
        self.button(card, "↪   Exit", self.destroy, False, 150).place(x=660, y=515)

        ctk.CTkLabel(
            card,
            text="BMI is a general screening indicator only. This prototype provides general fitness guidance and does not replace professional advice.",
            width=760,
            height=24,
            font=("Segoe UI", 9, "italic"),
            text_color=self.warning,
            anchor="center",
        ).place(x=100, y=575)

    def result_box(self, parent, x, y, title, value, icon_key):
        box = ctk.CTkFrame(
            parent,
            width=280,
            height=78,
            fg_color=self.surface,
            corner_radius=10,
            border_width=1,
            border_color=self.border,
        )
        box.place(x=x, y=y)

        self.icon_box(box, icon_key, 20, 17, size=44, image_size=30, bg_color=self.green_soft)

        ctk.CTkLabel(
            box,
            text=title,
            width=180,
            height=18,
            font=("Segoe UI", 9),
            text_color=self.text,
            anchor="w",
        ).place(x=78, y=18)

        ctk.CTkLabel(
            box,
            text=value,
            width=185,
            height=30,
            font=("Georgia", 13, "bold"),
            text_color=self.green,
            anchor="w",
            wraplength=180,
        ).place(x=78, y=40)

    def animate_preview(self):
        if not self.preview_running:
            return

        if hasattr(self, "preview_label") and self.preview_items:
            item = self.preview_items[self.preview_index % len(self.preview_items)]
            self.preview_label.configure(text=item)
            self.preview_index += 1
            self.after(1200, self.animate_preview)

    # ==========================================================
    # REASONING POPUP
    # ==========================================================

    def show_how(self):
        result = self.final_result

        profile = [
            f"Age: {self.profile.get('age')} ({self.profile.get('age_group')})",
            f"Gender: {self.profile.get('gender')}",
            f"BMI: {self.profile.get('bmi')} ({self.profile.get('bmi_category')})",
            f"Fitness Level: {self.answers.get('fitness_level')}",
            f"Lifestyle: {self.answers.get('activity_level')}",
            f"Health Condition: {self.answers.get('health_condition')}",
            f"Medical Restriction: {self.answers.get('medical_restriction')}",
            f"Injury: {self.format_answer(self.answers.get('injury'))}",
            f"Goal: {self.answers.get('goal')}",
            f"Workout Type: {self.format_answer(self.answers.get('preference'))}",
            f"Body Focus: {self.answers.get('target_area')}",
            f"Days per week: {self.answers.get('frequency')}",
            f"Equipment: {self.answers.get('equipment')}",
        ]

        content = (
            "Matched User Profile\n"
            + "\n".join([f"• {item}" for item in profile])
            + "\n\nTriggered Expert Rules\n"
            + "\n".join([f"✓ {rule}" for rule in self.triggered_rules])
            + "\n\nFinal Conclusion\n"
            + f"The system recommends {result['plan']} because it best matches the user profile, "
            f"BMI category, fitness goal, safety condition, injury status, available equipment, "
            f"and weekly schedule.\n\n"
            + "Safety Explanation\n"
            + "If the user has a serious health condition, medical restriction, injury, or BMI-goal conflict, "
            + "the system gives higher priority to safety rules. Therefore, the final output can be different from a normal user."
        )

        self.popup("How was this conclusion reached?", content, 850, 620)

    def format_answer(self, value):
        if isinstance(value, list):
            return ", ".join(value)
        return value

    def restart(self):
        self.preview_running = False
        self.profile = {}
        self.answers = {}
        self.current_question = 0
        self.temp_answer = None
        self.option_cards = []
        self.triggered_rules = []
        self.final_result = {}
        self.show_learning_page()


if __name__ == "__main__":
    app = WorkoutExpertSystem()
    app.mainloop()