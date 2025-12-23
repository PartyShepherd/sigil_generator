import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, request, render_template
import io
import base64
from matplotlib.patches import Circle

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend

letter_mapping = {
    "A": [("A", "#FFFF00")],  
    "E": [("A", "#FFFF00")],  
    "B": [("B", "#FFFF00")],  # Beth now only represents B
    "C": [("G", "#0000FF")],  
    "CH": [("Ch", "#FFD700")],  
    "H": [("H", "#FF0000")],  
    "G": [("G", "#0000FF")],  
    "GH": [("GH", "#0000FF")],  
    "D": [("D", "#008000")],  
    "DH": [("DH", "#008000")],  
    "V": [("V", "#FF4500")],  # Vav now represents V
    "U": [("V", "#FF4500")],  # Vav now represents U
    "W": [("V", "#FF4500")],  # Vav now represents W
    "O": [("O", "#4B0082")],  
    "Z": [("Z", "#FFA500")],  
    "T": [("T", "#FFFF00")],  
    "TH": [("TH", "#4B0082")],  
    "I": [("I", "#9ACD32")],  
    "J": [("I", "#9ACD32")],  
    "Y": [("I", "#9ACD32")],  
    "K": [("K", "#800080")],  
    "KH": [("KH", "#9400D3")],  
    "L": [("L", "#008000")],  
    "M": [("M", "#0000FF")],  
    "N": [("N", "#20B2AA")],  
    "S": [("S", "#FF4500")],  
    "SH": [("Sh", "#FF0000")],  
    "P": [("P", "#FF0000")],  
    "PH": [("PH", "#FFA500")],  
    "F": [("F", "#FF0000")],  
    "X": [("X", "#800080")],  
    "TZ": [("X", "#800080")],  
    "Q": [("Q", "#9400D3")],  
    "R": [("R", "#FFA500")],  
    "RH": [("RH", "#FFD700")],  
}

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    sigil_image = None
    if request.method == 'POST':
        word = request.form.get('word', '').strip()
        if word:
            sigil_image = draw_rose_sigil(word)
    return render_template('index.html', sigil_image=sigil_image)

def preprocess_word(word):
    word = word.upper()
    processed_word = []
    skip_next = False

    for i in range(len(word)):
        if skip_next:
            skip_next = False
            continue
        
        if i < len(word) - 1:
            two_letter_combo = word[i] + word[i + 1]
            if two_letter_combo in letter_mapping:
                processed_word.append(two_letter_combo)  
                skip_next = True  
                continue
        
        if word[i] in letter_mapping:
            processed_word.append(word[i])

    return processed_word  

def draw_rose_sigil(word="JAMES"):
    word = preprocess_word(word)
    
    all_positions = {}
    ordered_outer_letters = ["H", "Z", "V", "E", "Q", "X", "O", "S", "N", "L", "I", "T", "Ch"]
    ordered_middle_letters = ["R", "RH", "P", "PH", "F", "K", "KH", "TH", "G", "GH", "D", "DH", "B"]  
    ordered_mother_letters = ["M", "A", "Sh"]

    all_positions.update({letter: (-np.cos(i * (2 * np.pi / len(ordered_outer_letters))) * 2, 
                                   np.sin(i * (2 * np.pi / len(ordered_outer_letters))) * 2) 
                          for i, letter in enumerate(ordered_outer_letters)})

    # **Ensure Heh (H) is placed between Vav (V) and Qoph (Q)**
    v_index = ordered_outer_letters.index("V")
    q_index = ordered_outer_letters.index("Q")
    h_index = (v_index + q_index) / 2
    all_positions["H"] = (-np.cos(h_index * (2 * np.pi / len(ordered_outer_letters))) * 2,
                           np.sin(h_index * (2 * np.pi / len(ordered_outer_letters))) * 2)

    all_positions.update({letter: (-np.cos(i * (2 * np.pi / len(ordered_middle_letters))) * 1.2,  
                                   np.sin(i * (2 * np.pi / len(ordered_middle_letters))) * 1.2)  
                          for i, letter in enumerate(ordered_middle_letters)})

    # **Mother Letters Stay Fixed**
    all_positions["A"] = (0, 0.7)   # Aleph inside Kaph
    all_positions["M"] = (-0.7, 0.0)  # Mem inside Beth
    all_positions["Sh"] = (0.7, 0.0)  # Shin inside Gimel

    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#D3D3D3')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.add_patch(Circle((0, 0), 2.5, fill=False, edgecolor='black', lw=2))

    prev_pos = None
    prev_color = None
    first_pos = None
    last_pos = None
    seen_positions = {}

    for char in word:
        if char in letter_mapping:
            letter, color = letter_mapping[char][0]
            if letter not in all_positions:
                continue
            x, y = all_positions[letter]
            ax.text(x, y, letter, fontsize=16, ha='center', va='center', color=color, fontweight='bold')

            # **Make sure lines use the color of the previous letter**
            if prev_pos:
                ax.plot([prev_pos[0], x], [prev_pos[1], y], color=prev_color, lw=2)

            # **Handle repeating letters with a loop**
            if (x, y) in seen_positions:
                ax.add_patch(Circle((x, y), 0.2, fill=False, edgecolor=color, lw=2))  # Loop with letter color
            seen_positions[(x, y)] = True

            if first_pos is None:
                first_pos = (x, y)
            last_pos = (x, y)

            prev_pos = (x, y)
            prev_color = color  # Store the current letter color for the next line

    # **Black "O" at Start**
    if first_pos:
        ax.add_patch(Circle(first_pos, 0.2, fill=False, edgecolor='black', lw=3))

    # **Diagonal Dash at End**
    if last_pos:
        ax.plot([last_pos[0], last_pos[0] + 0.2], 
                [last_pos[1], last_pos[1] - 0.2], 
                color='black', lw=3)

    plt.axis('off')
    plt.title("An Alchemelodic Sigil Generator", color="black")  
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor=fig.get_facecolor())  
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return img_base64

if __name__ == '__main__':
    app.run(debug=True)
