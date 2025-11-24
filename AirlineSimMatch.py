import tkinter as tk
from tkinter import messagebox
import random
from datetime import datetime, timedelta

# --- Game setup ---
score = 0
lives = 5  # Will be set based on difficulty (5 for easy, 3 for hard)
all_gates = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "B1", "B2", "B3", "B4", "B5"]
available_gates = all_gates.copy()
current_flight = None
gate_buttons = {}
occupied_gates = {}
departure_timers = {}
plane_labels = {}  # Track plane emoji labels for each gate
departure_labels = {}  # Track departure notification labels for each gate
game_time = None  # Current game time (9am to 5pm)
game_time_start = None  # Start of shift
game_time_end = None  # End of shift
time_timer = None  # Timer for game clock
assignment_timer = None  # Timer for assignment countdown
game_over = False  # Track if game is over
countdown_remaining = 5  # Countdown seconds remaining (5 seconds)
game_paused = False  # Track if game is paused
hint_used = False  # Track if hint was used for current flight
difficulty = "easy"  # Game difficulty: "easy" or "hard"

narrowbody_aircraft = ["A220", "B737", "B757", "E175", "CRJ900", "B717", "A321"]
widebody_aircraft = ["B777", "B787", "A350", "A330", "B767", "A380", "B787"]
narrowbody_gates = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
widebody_gates = ["B1", "B2", "B3", "B4", "B5"]

# Airport code to city name mapping
airport_cities = {
    # Domestic
    "ATL": "Atlanta", "MSP": "Minneapolis", "DTW": "Detroit", "SLC": "Salt Lake City",
    "LAX": "Los Angeles", "JFK": "New York", "BOS": "Boston", "SEA": "Seattle",
    "DEN": "Denver", "ORD": "Chicago", "MIA": "Miami", "MCO": "Orlando",
    "LAS": "Las Vegas", "PHX": "Phoenix", "SFO": "San Francisco", "DCA": "Washington DC",
    "PDX": "Portland", "SAN": "San Diego", "TPA": "Tampa", "AUS": "Austin",
    "RDU": "Raleigh", "CLT": "Charlotte", "PHL": "Philadelphia", "BWI": "Baltimore",
    # International
    "LHR": "London", "CDG": "Paris", "AMS": "Amsterdam", "FCO": "Rome",
    "BCN": "Barcelona", "MAD": "Madrid", "FRA": "Frankfurt", "MUC": "Munich",
    "HND": "Tokyo", "ICN": "Seoul", "PVG": "Shanghai", "HKG": "Hong Kong",
    "SYD": "Sydney", "MEL": "Melbourne", "GRU": "São Paulo", "EZE": "Buenos Aires",
    "SCL": "Santiago", "CPH": "Copenhagen", "NCE": "Nice", "BER": "Berlin",
    "ARN": "Stockholm", "LIS": "Lisbon", "DUB": "Dublin", "ZRH": "Zurich"
}

def is_widebody(aircraft):
    return aircraft in widebody_aircraft

def can_use_gate(aircraft, gate):
    if is_widebody(aircraft):
        return gate in widebody_gates
    else:
        return gate in narrowbody_gates

def generate_flight():
    flight_num = "DL" + str(random.randint(100, 999))
    
    # Domestic destinations (narrowbody aircraft only)
    domestic_destinations = [
        "ATL", "MSP", "DTW", "SLC", "LAX", "JFK", "BOS", "SEA", 
        "DEN", "ORD", "MIA", "MCO", "LAS", "PHX", "SFO", "DCA",
        "PDX", "SAN", "TPA", "AUS", "RDU", "CLT", "PHL", "BWI"
    ]
    
    # International destinations (widebody aircraft only)
    international_destinations = [
        "LHR", "CDG", "AMS", "FCO", "BCN", "MAD", "FRA", "MUC",
        "HND", "ICN", "PVG", "HKG", "SYD", "MEL", "GRU", "EZE",
        "SCL", "CPH", "NCE", "BER", "ARN", "LIS", "DUB", "ZRH"
    ]
    
    # Randomly decide if this is a widebody flight (60% narrowbody, 40% widebody)
    # Ratio closer to gate availability: 8 narrowbody gates, 5 widebody gates
    use_widebody = random.random() < 0.40
    
    if use_widebody:
        aircraft = random.choice(widebody_aircraft)
        # Widebody only international
        destination = random.choice(international_destinations)
    else:
        aircraft = random.choice(narrowbody_aircraft)
        # Narrowbody only domestic
        destination = random.choice(domestic_destinations)
    
    return {"flight": flight_num, "aircraft": aircraft, "destination": destination}

def show_end_game_dialog(is_win, final_score):
    """Show game over dialog with replay and close options"""
    global game_over
    game_over = True
    
    # Cancel all timers
    if time_timer:
        root.after_cancel(time_timer)
    if assignment_timer:
        root.after_cancel(assignment_timer)
    
    # Create custom dialog
    dialog = tk.Toplevel(root)
    dialog.title("Game Over" if not is_win else "Shift Complete!")
    dialog.geometry("400x250")
    dialog.config(bg="#34495e")
    dialog.transient(root)
    dialog.grab_set()
    
    if is_win:
        title_text = "🎉 SHIFT COMPLETE! 🎉"
        message_text = f"Congratulations! You made it through your 8-hour shift!\n\nFinal Score: {final_score}"
        title_color = "#2ecc71"
    else:
        title_text = "❌ GAME OVER ❌"
        message_text = f"You lost all your lives!\n\nFinal Score: {final_score}"
        title_color = "#e74c3c"
    
    title_label = tk.Label(dialog, text=title_text, font=("Arial", 16, "bold"),
                          bg="#34495e", fg=title_color)
    title_label.pack(pady=20)
    
    message_label = tk.Label(dialog, text=message_text, font=("Arial", 12),
                            bg="#34495e", fg="white", justify=tk.CENTER)
    message_label.pack(pady=20)
    
    button_frame = tk.Frame(dialog, bg="#34495e")
    button_frame.pack(pady=20)
    
    replay_btn = tk.Button(button_frame, text="🔄 Play Again", command=lambda: restart_game(dialog),
                          bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                          width=12, height=2, relief=tk.RAISED, bd=3)
    replay_btn.pack(side=tk.LEFT, padx=10)
    
    close_btn = tk.Button(button_frame, text="❌ Close", command=root.quit,
                         bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                         width=12, height=2, relief=tk.RAISED, bd=3)
    close_btn.pack(side=tk.LEFT, padx=10)

def restart_game(dialog=None):
    """Restart the game from beginning"""
    global score, lives, available_gates, occupied_gates, departure_timers, current_flight
    global game_time, game_time_start, game_time_end, game_over, assignment_timer, time_timer, game_paused, hint_used
    
    # Close dialog if exists
    if dialog:
        dialog.destroy()
    
    # Reset game state
    game_over = False
    game_paused = False
    hint_used = False
    score = 0
    lives = 5 if difficulty == "easy" else 3
    available_gates = all_gates.copy()
    occupied_gates = {}
    departure_timers = {}
    current_flight = None
    
    # Cancel all existing timers
    for timer_id in departure_timers.values():
        root.after_cancel(timer_id)
    if assignment_timer:
        root.after_cancel(assignment_timer)
    if time_timer:
        root.after_cancel(time_timer)
    
    # Reset time to 9am
    game_time_start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    game_time = game_time_start
    game_time_end = game_time_start.replace(hour=17, minute=0)  # 5pm
    
    # Update displays
    score_label.config(text=f"Score: {score}")
    lives_label.config(text=f"Lives: {'❤️' * lives}")
    time_label.config(text=f"Time: {game_time.strftime('%I:%M %p')}")
    result_label.config(text="")
    countdown_label.config(text="")
    pause_btn.config(text="⏸ Pause", bg="#3498db")
    hint_btn.config(text="💡 Get Hint", bg="#f39c12", state=tk.NORMAL)
    
    # Clear all departure notifications
    for gate in departure_labels:
        departure_labels[gate].config(text="")
    
    update_gate_display()
    
    # Start new game
    update_game_time()
    next_flight()

def toggle_pause():
    """Toggle game pause state"""
    global game_paused
    
    if game_over:
        return
    
    game_paused = not game_paused
    
    if game_paused:
        # Pause the game
        pause_btn.config(text="▶ Resume", bg="#2ecc71")
        result_label.config(text="⏸️ GAME PAUSED ⏸️", fg="#f39c12")
        disable_all_buttons()
        
        # Cancel timers
        if assignment_timer:
            root.after_cancel(assignment_timer)
        if time_timer:
            root.after_cancel(time_timer)
    else:
        # Resume the game
        pause_btn.config(text="⏸ Pause", bg="#3498db")
        result_label.config(text="")
        enable_all_buttons()
        
        # Restart timers
        update_game_time()
        start_assignment_countdown()

def show_hint():
    """Show the city name for the current flight destination"""
    global hint_used
    
    if difficulty == "hard":
        messagebox.showinfo("Hard Mode", "Hints are not available in Hard Mode!")
        return
    
    if game_over or game_paused or not current_flight:
        return
    
    if hint_used:
        messagebox.showinfo("Hint Already Used", "You've already used the hint for this flight!")
        return
    
    hint_used = True
    airport_code = current_flight['destination']
    city_name = airport_cities.get(airport_code, "Unknown City")
    
    # Update hint button to show it was used
    hint_btn.config(text="💡 Hint Used", bg="#95a5a6", state=tk.DISABLED)
    
    # Show the city name in a message box
    messagebox.showinfo("Destination Hint", 
                       f"✈️ Flight {current_flight['flight']}\n\n"
                       f"Destination: {airport_code} - {city_name}\n\n"
                       f"Aircraft: {current_flight['aircraft']}")

def depart_plane(gate):
    global game_over
    if game_over or game_paused:
        return
    
    if gate in occupied_gates:
        available_gates.append(gate)
        del occupied_gates[gate]
        
        # Show departure notification next to the gate
        if gate in departure_labels:
            departure_labels[gate].config(text=f"✈️ DEPARTED", fg="#3498db")
            root.after(3000, lambda g=gate: departure_labels[g].config(text=""))
        
        enable_all_buttons()
        update_gate_display()

def schedule_departure(gate, flight_info):
    departure_time = random.randint(5000, 20000)
    timer_id = root.after(departure_time, lambda: depart_plane(gate))
    departure_timers[gate] = timer_id

def update_game_time():
    global game_time, time_timer, game_over
    if game_over or game_paused:
        return
    
    # Advance time by 5 minutes per tick (10 seconds real time = 1 hour game time = 12 ticks)
    game_time += timedelta(minutes=5)
    
    # Check if shift is over (5pm)
    if game_time >= game_time_end:
        game_over = True
        show_end_game_dialog(True, score)
        return
    
    # Update time display
    time_label.config(text=f"Time: {game_time.strftime('%I:%M %p')}")
    
    # Schedule next time update (~0.833 seconds real time)
    time_timer = root.after(833, update_game_time)

def update_lives_display():
    """Update the lives display with hearts"""
    hearts = "❤️" * lives
    lives_label.config(text=f"Lives: {hearts}")

def update_countdown_display():
    global countdown_remaining, assignment_timer, game_over
    if game_over or game_paused:
        return
    
    if countdown_remaining > 0:
        colors = {5: "#3498db", 4: "#3498db", 3: "#3498db", 2: "#f39c12", 1: "#e74c3c"}
        text = f"⚠️ {countdown_remaining} ⚠️" if countdown_remaining == 1 else f"⏰ {countdown_remaining}"
        countdown_label.config(text=text, fg=colors[countdown_remaining], font=("Arial", 24, "bold"))
        
        countdown_remaining -= 1
        assignment_timer = root.after(1000, update_countdown_display)
    else:
        assignment_timeout()

def start_assignment_countdown():
    global countdown_remaining, assignment_timer, game_over
    if game_over:
        return
    
    # Cancel existing timer if any
    if assignment_timer:
        root.after_cancel(assignment_timer)
    
    # Reset countdown to 5 seconds
    countdown_remaining = 5
    countdown_label.config(text="⏰ 5", fg="#3498db", font=("Arial", 24, "bold"))
    
    # Start countdown display updates
    assignment_timer = root.after(1000, update_countdown_display)

def assignment_timeout():
    global game_over, lives
    if game_over:
        return
    
    # Lose a life for timeout
    lives -= 1
    update_lives_display()
    
    result_label.config(text=f"⏰ Time's up! Lost 1 life | Lives remaining: {lives}")
    
    # Check for game over
    if lives <= 0:
        game_over = True
        show_end_game_dialog(False, score)
        return
    
    # Move to next flight
    root.after(1000, next_flight)

def next_flight():
    global current_flight, game_over, hint_used
    if game_over or game_paused:
        return
    
    # Reset hint for new flight (only in easy mode)
    hint_used = False
    if difficulty == "easy":
        hint_btn.config(text="💡 Get Hint", bg="#f39c12", state=tk.NORMAL)
    
    current_flight = generate_flight()
    flight_label.config(
        text=f"Incoming flight {current_flight['flight']} to {current_flight['destination']} ({current_flight['aircraft']})"
    )
    result_label.config(text="")
    enable_all_buttons()
    
    # Start 5-second countdown
    start_assignment_countdown()

def disable_all_buttons():
    for btn in gate_buttons.values():
        btn.config(state=tk.DISABLED)

def enable_all_buttons():
    for gate, btn in gate_buttons.items():
        if gate in available_gates:
            btn.config(state=tk.NORMAL)
        else:
            btn.config(state=tk.DISABLED)

def update_gate_display():
    for gate, btn in gate_buttons.items():
        if gate in occupied_gates:
            btn_height = 2 if gate in widebody_gates else 1
            btn.config(text=occupied_gates[gate]['flight'], bg="lightcoral", state=tk.DISABLED, font=("Arial", 8, "bold"), width=5, height=btn_height)
            if gate in plane_labels:
                plane_labels[gate].config(text="🛬")
        else:
            if gate in widebody_gates:
                btn.config(text=gate, bg="#f5b041", state=tk.NORMAL, font=("Arial", 8, "bold"), width=5, height=2)
            else:
                btn.config(text=gate, bg="#2ecc71", state=tk.NORMAL, font=("Arial", 8, "bold"), width=5, height=1)
            if gate in plane_labels:
                plane_labels[gate].config(text="")

def assign_gate(gate):
    global score, assignment_timer, game_over, lives
    if game_over or game_paused:
        return
    
    # Cancel the countdown timer
    if assignment_timer:
        root.after_cancel(assignment_timer)
        assignment_timer = None
    
    # Clear countdown display
    countdown_label.config(text="")
    
    disable_all_buttons()
    
    if not can_use_gate(current_flight['aircraft'], gate):
        # Lose a life for wrong gate
        lives -= 1
        update_lives_display()
        
        if is_widebody(current_flight['aircraft']):
            messagebox.showerror("Gate Too Small", f"❌ {current_flight['aircraft']} is a WIDEBODY!\n\nToo large for A gates. Must use B gates.\n\n💔 Lost 1 life!")
            result_label.config(text=f"❌ Widebody cannot fit in Gate {gate} | Lives: {lives}")
        else:
            messagebox.showerror("Gate Too Large", f"❌ {current_flight['aircraft']} is a NARROWBODY!\n\nToo small for B gates. Must use A gates.\n\n💔 Lost 1 life!")
            result_label.config(text=f"❌ Narrowbody must use A gates, not {gate} | Lives: {lives}")
        
        # Check for game over
        if lives <= 0:
            game_over = True
            show_end_game_dialog(False, score)
            return
        
        enable_all_buttons()
        root.after(1000, next_flight)
        return
    
    available_gates.remove(gate)
    occupied_gates[gate] = current_flight
    
    # Award points based on aircraft type
    if is_widebody(current_flight['aircraft']):
        points = 20
        result_label.config(text=f"✅ {current_flight['flight']} ({current_flight['aircraft']}) assigned to Gate {gate} (+20 pts)")
    else:
        points = 10
        result_label.config(text=f"✅ {current_flight['flight']} ({current_flight['aircraft']}) assigned to Gate {gate} (+10 pts)")
    
    score += points
    score_label.config(text=f"Score: {score}")
    
    schedule_departure(gate, current_flight)
    update_gate_display()
    root.after(1000, next_flight)

# --- GUI setup ---
root = tk.Tk()
root.title("Airport Operations Simulator")
root.geometry("700x600")
root.config(bg="#2c3e50")

# Header section (create but don't pack yet)
header_frame = tk.Frame(root, bg="#34495e", relief=tk.RAISED, bd=2)

title_label = tk.Label(header_frame, text="✈️ AIRPORT OPERATIONS SIMULATOR ✈️", 
                       font=("Arial", 13, "bold"), bg="#34495e", fg="white")
title_label.pack(pady=5)

# Time display
time_label = tk.Label(header_frame, text="Time: 09:00 AM", font=("Arial", 10, "bold"),
                     bg="#34495e", fg="#3498db")
time_label.pack(pady=2)

flight_label = tk.Label(header_frame, text="", font=("Arial", 10, "bold"), 
                        bg="#34495e", fg="#f39c12")
flight_label.pack(pady=2)

lives_label = tk.Label(header_frame, text="Lives: ❤️❤️❤️", font=("Arial", 11, "bold"),
                      bg="#34495e", fg="#e74c3c")
lives_label.pack(pady=2)

score_label = tk.Label(header_frame, text=f"Score: {score}", font=("Arial", 10, "bold"),
                       bg="#34495e", fg="#2ecc71")
score_label.pack(pady=2)

# Countdown timer display 
countdown_label = tk.Label(header_frame, text="", font=("Arial", 20, "bold"),
                          bg="#34495e", fg="#3498db")
countdown_label.pack(pady=5)

# Pause button
pause_btn = tk.Button(header_frame, text="⏸ Pause", command=toggle_pause,
                     bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                     width=12, height=1, relief=tk.RAISED, bd=2)
pause_btn.pack(pady=5)

# Hint button
hint_btn = tk.Button(header_frame, text="💡 Get Hint", command=show_hint,
                    bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
                    width=12, height=1, relief=tk.RAISED, bd=2)
hint_btn.pack(pady=2)

map_frame = tk.Frame(root, bg="#2c3e50")

# Terminal A - Left side (vertical, green)
terminal_a_frame = tk.Frame(map_frame, bg="#27ae60", relief=tk.RIDGE, bd=4)
terminal_a_frame.grid(row=0, column=0, padx=40, pady=5)

a_label = tk.Label(terminal_a_frame, text="TERMINAL A\nNARROWBODY", 
                   font=("Arial", 10, "bold"), bg="#27ae60", fg="white")
a_label.pack(pady=3)

for gate in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]:
    # Container for gate + jetbridge + plane
    gate_container = tk.Frame(terminal_a_frame, bg="#27ae60")
    gate_container.pack(pady=1)
    
    # Gate button
    btn = tk.Button(gate_container, text=gate, width=5, height=1, 
                    command=lambda g=gate: assign_gate(g), bg="#2ecc71", 
                    font=("Arial", 8, "bold"), relief=tk.RAISED, bd=2)
    btn.pack(side=tk.LEFT, padx=2)
    gate_buttons[gate] = btn
    
    # Jetbridge (line)
    jetbridge = tk.Label(gate_container, text="━━", bg="#27ae60", fg="white", font=("Arial", 10))
    jetbridge.pack(side=tk.LEFT)
    
    # Plane emoji (initially hidden, fixed width to prevent movement)
    plane = tk.Label(gate_container, text="", bg="#27ae60", font=("Arial", 16), width=2)
    plane.pack(side=tk.LEFT, padx=2)
    plane_labels[gate] = plane
    
    # Departure notification label (initially hidden)
    departure_notif = tk.Label(gate_container, text="", bg="#27ae60", 
                              font=("Arial", 8, "bold"), fg="#3498db", width=12)
    departure_notif.pack(side=tk.LEFT, padx=5)
    departure_labels[gate] = departure_notif

# Terminal B - Right side (vertical, orange)
terminal_b_frame = tk.Frame(map_frame, bg="#f39c12", relief=tk.RIDGE, bd=4)
terminal_b_frame.grid(row=0, column=1, padx=40, pady=5)

b_label = tk.Label(terminal_b_frame, text="TERMINAL B\nWIDEBODY", 
                   font=("Arial", 10, "bold"), bg="#f39c12", fg="white")
b_label.pack(pady=3)

for gate in ["B1", "B2", "B3", "B4", "B5"]:
    # Container for gate + jetbridge + plane
    gate_container = tk.Frame(terminal_b_frame, bg="#f39c12")
    gate_container.pack(pady=1)
    
    # Gate button
    btn = tk.Button(gate_container, text=gate, width=5, height=2, 
                    command=lambda g=gate: assign_gate(g), bg="#f5b041", 
                    font=("Arial", 8, "bold"), relief=tk.RAISED, bd=2)
    btn.pack(side=tk.LEFT, padx=2)
    gate_buttons[gate] = btn
    
    # Jetbridge (line)
    jetbridge = tk.Label(gate_container, text="━━", bg="#f39c12", fg="white", font=("Arial", 10))
    jetbridge.pack(side=tk.LEFT)
    
    # Plane emoji (initially hidden, fixed width to prevent movement)
    plane = tk.Label(gate_container, text="", bg="#f39c12", font=("Arial", 16), width=2)
    plane.pack(side=tk.LEFT, padx=2)
    plane_labels[gate] = plane
    
    # Departure notification label (initially hidden)
    departure_notif = tk.Label(gate_container, text="", bg="#f39c12", 
                              font=("Arial", 8, "bold"), fg="#3498db", width=12)
    departure_notif.pack(side=tk.LEFT, padx=5)
    departure_labels[gate] = departure_notif

# Control panel section (create but don't pack yet)
control_frame = tk.Frame(root, bg="#34495e", relief=tk.RAISED, bd=3)

result_label = tk.Label(control_frame, text="", font=("Arial", 11, "bold"), 
                        bg="#34495e", fg="white")
result_label.pack(pady=10)

def start_game_from_menu(menu_frame, selected_difficulty):
    """Start the game after dismissing the menu"""
    global game_time_start, game_time, game_time_end, difficulty, lives
    
    # Set difficulty
    difficulty = selected_difficulty
    
    # Set lives based on difficulty
    lives = 5 if difficulty == "easy" else 3
    
    # Hide menu
    menu_frame.destroy()
    
    # Show game elements (smaller header padding to focus on terminals)
    header_frame.pack(fill=tk.X, padx=10, pady=5)
    map_frame.pack(padx=20, pady=15)
    control_frame.pack(padx=10, pady=5, fill=tk.X)
    
    # Update lives display
    lives_label.config(text=f"Lives: {'❤️' * lives}")
    
    # Hide hint button in hard mode
    if difficulty == "hard":
        hint_btn.pack_forget()
    
    # Initialize game time (9am start)
    game_time_start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    game_time = game_time_start
    game_time_end = game_time_start.replace(hour=17, minute=0)  # 5pm end
    
    # Start the game
    update_game_time()
    next_flight()

def show_main_menu():
    """Display the main menu with instructions"""
    menu_frame = tk.Frame(root, bg="#2c3e50")
    menu_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title = tk.Label(menu_frame, text="✈️ AIRPORT OPERATIONS SIMULATOR ✈️",
                    font=("Arial", 18, "bold"), bg="#2c3e50", fg="white")
    title.pack(pady=15)
    
    # Instructions panel
    instructions_frame = tk.Frame(menu_frame, bg="#34495e", relief=tk.RIDGE, bd=5)
    instructions_frame.pack(padx=40, pady=10)
    
    instructions_title = tk.Label(instructions_frame, text="📋 HOW TO PLAY",
                                 font=("Arial", 14, "bold"), bg="#34495e", fg="#3498db")
    instructions_title.pack(pady=10)
    
    instructions_text = """🎯 OBJECTIVE: Survive 8-hour shift (9 AM - 5 PM)

⏰ RULES:
• Assign flights to gates within 5 SECONDS
• Terminal A: Narrowbody → Domestic
• Terminal B: Widebody → International

💔 LIVES SYSTEM:
• Easy Mode: 5 lives ❤️❤️❤️❤️❤️
• Hard Mode: 3 lives ❤️❤️❤️
• Wrong gate type: -1 life
• Timeout (5 seconds): -1 life
• Lose all lives = GAME OVER

📊 SCORING:
• ✅ Narrowbody: +10  |  ✅ Widebody: +20
• Score is for bragging rights only!

🎉 WIN: Reach 5 PM with lives remaining"""
    
    instructions_label = tk.Label(instructions_frame, text=instructions_text,
                                 font=("Arial", 10), bg="#34495e", fg="white",
                                 justify=tk.LEFT, padx=20, pady=10)
    instructions_label.pack()
    
    # Difficulty selection frame
    difficulty_frame = tk.Frame(menu_frame, bg="#2c3e50")
    difficulty_frame.pack(pady=15)
    
    difficulty_label = tk.Label(difficulty_frame, text="SELECT DIFFICULTY:",
                               font=("Arial", 12, "bold"), bg="#2c3e50", fg="white")
    difficulty_label.pack(pady=5)
    
    button_container = tk.Frame(difficulty_frame, bg="#2c3e50")
    button_container.pack(pady=10)
    
    # Easy mode button
    easy_button = tk.Button(button_container, text="🟢 EASY MODE\n(Hints Available)", 
                           command=lambda: start_game_from_menu(menu_frame, "easy"),
                           bg="#2ecc71", fg="white", font=("Arial", 12, "bold"),
                           width=18, height=3, relief=tk.RAISED, bd=5,
                           cursor="hand2")
    easy_button.pack(side=tk.LEFT, padx=10)
    
    # Hard mode button
    hard_button = tk.Button(button_container, text="🔴 HARD MODE\n(No Hints)", 
                           command=lambda: start_game_from_menu(menu_frame, "hard"),
                           bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                           width=18, height=3, relief=tk.RAISED, bd=5,
                           cursor="hand2")
    hard_button.pack(side=tk.LEFT, padx=10)
    
    # Credits
    credits = tk.Label(menu_frame, text="Good luck, Rookie Dispatcher! 🛫",
                      font=("Arial", 9, "italic"), bg="#2c3e50", fg="#95a5a6")
    credits.pack(pady=5)
    
    # Designer credit
    designer = tk.Label(menu_frame, text="Game designed by Rowan Seskin and Gabrielle Godfrey",
                       font=("Arial", 8), bg="#2c3e50", fg="#7f8c8d")
    designer.pack(side=tk.BOTTOM, pady=10)

# Show main menu first (game elements not packed yet, so they're hidden)
show_main_menu()

root.mainloop()
