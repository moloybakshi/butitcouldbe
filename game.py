import pygame
import random
import requests
import json
import os
import math
import datetime
from dotenv import load_dotenv

# Initialize Pygame
pygame.init()

# Load environment variables
load_dotenv()

# Game constants
WINDOW_WIDTH = 1000  # Increased width
WINDOW_HEIGHT = 700  # Increased height
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
BLUE = (100, 100, 255)
GREEN = (100, 255, 100)
FONT_SIZE = 24
LINE_HEIGHT = 30
PADDING = 10

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Convince the AI!")
font = pygame.font.Font(None, FONT_SIZE)
large_font = pygame.font.Font(None, FONT_SIZE * 2)

# Load sprites
def load_sprite_sheet(filename, rows, cols):
    sheet = pygame.image.load(filename).convert_alpha()
    sprite_width = sheet.get_width() // cols
    sprite_height = sheet.get_height() // rows
    sprites = []
    for row in range(rows):
        for col in range(cols):
            x = col * sprite_width
            y = row * sprite_height
            sprite = sheet.subsurface(pygame.Rect(x, y, sprite_width, sprite_height))
            sprites.append(sprite)
    return sprites

# Create placeholder sprites if they don't exist
def create_placeholder_sprites():
    # AI sprite (simple robot)
    ai_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(ai_surface, (100, 100, 255), (50, 50), 40)  # Body
    pygame.draw.circle(ai_surface, (255, 255, 255), (35, 40), 10)  # Left eye
    pygame.draw.circle(ai_surface, (255, 255, 255), (65, 40), 10)  # Right eye
    pygame.draw.rect(ai_surface, (200, 200, 200), (30, 60, 40, 20))  # Mouth
    ai_surface = pygame.transform.scale(ai_surface, (100, 100))
    pygame.image.save(ai_surface, "assets/sprites/ai_sprite.png")

    # Player sprite (simple human)
    player_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(player_surface, (255, 200, 150), (50, 50), 40)  # Head
    pygame.draw.circle(player_surface, (0, 0, 0), (35, 40), 5)  # Left eye
    pygame.draw.circle(player_surface, (0, 0, 0), (65, 40), 5)  # Right eye
    pygame.draw.arc(player_surface, (0, 0, 0), (30, 60, 40, 20), 0, 3.14, 2)  # Smile
    player_surface = pygame.transform.scale(player_surface, (100, 100))
    pygame.image.save(player_surface, "assets/sprites/player_sprite.png")

# Create sprites directory if it doesn't exist
if not os.path.exists("assets/sprites"):
    os.makedirs("assets/sprites")

# Create placeholder sprites if they don't exist
if not os.path.exists("assets/sprites/ai_sprite.png"):
    create_placeholder_sprites()

# Load sprites
ai_sprite = pygame.image.load("assets/sprites/ai_sprite.png").convert_alpha()
player_sprite = pygame.image.load("assets/sprites/player_sprite.png").convert_alpha()

# Scenarios
SCENARIOS = [
    "You are actually a cat in a human body",
    "The world is flat",
    "Aliens built the pyramids",
    "Time travel is real",
    "You're living in a simulation",
    "The moon landing was faked",
    "Dinosaurs still exist",
    "The Earth is hollow",
    "Bigfoot is real",
    "Ghosts are real"
]

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        width = font.size(test_line)[0]

        if width > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    return lines

class ScrollableTextArea:
    def __init__(self, x, y, width, height, max_lines=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_lines = max_lines
        self.lines = []
        self.scroll_position = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.scrollbar_width = 20
        self.text_width = width - self.scrollbar_width - (2 * PADDING)
        self.scrollbar_rect = pygame.Rect(x + width - self.scrollbar_width, y, self.scrollbar_width, height)
        self.scrollbar_handle_height = max(20, height * (height / (max_lines * LINE_HEIGHT)))
        self.scrollbar_handle_rect = pygame.Rect(x + width - self.scrollbar_width, y, self.scrollbar_width, self.scrollbar_handle_height)
        self.dragging = False
        self.drag_offset = 0
        self.total_height = 0

    def add_line(self, text):
        # Wrap the text before adding
        wrapped_lines = wrap_text(text, font, self.text_width)
        self.lines.extend(wrapped_lines)
        self.total_height = len(self.lines) * LINE_HEIGHT
        self.update_scrollbar()
        # Auto-scroll to bottom when new content is added
        if self.total_height > self.height:
            self.scroll_position = self.total_height - self.height

    def clear(self):
        self.lines = []
        self.scroll_position = 0
        self.total_height = 0
        self.update_scrollbar()

    def update_scrollbar(self):
        if self.total_height > self.height:
            visible_ratio = self.height / self.total_height
            self.scrollbar_handle_height = max(20, self.height * visible_ratio)
            self.scrollbar_handle_rect.height = self.scrollbar_handle_height
            max_scroll = self.total_height - self.height
            if max_scroll > 0:
                scroll_ratio = self.scroll_position / max_scroll
                self.scrollbar_handle_rect.y = self.y + (self.height - self.scrollbar_handle_height) * scroll_ratio

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scrollbar_handle_rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = event.pos[1] - self.scrollbar_handle_rect.y
            elif self.rect.collidepoint(event.pos):
                # Handle mouse wheel scrolling
                if event.button == 4:  # Scroll up
                    self.scroll_position = max(0, self.scroll_position - LINE_HEIGHT)
                elif event.button == 5:  # Scroll down
                    max_scroll = max(0, self.total_height - self.height)
                    self.scroll_position = min(max_scroll, self.scroll_position + LINE_HEIGHT)
                self.update_scrollbar()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            if self.total_height > self.height:
                new_y = event.pos[1] - self.drag_offset
                new_y = max(self.y, min(self.y + self.height - self.scrollbar_handle_height, new_y))
                scroll_ratio = (new_y - self.y) / (self.height - self.scrollbar_handle_height)
                max_scroll = max(0, self.total_height - self.height)
                self.scroll_position = min(max_scroll, scroll_ratio * self.total_height)
                self.update_scrollbar()

    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        # Create a clipping area for the text
        clip_rect = pygame.Rect(self.x, self.y, self.width - self.scrollbar_width, self.height)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        # Draw text
        visible_height = self.height - (2 * PADDING)
        visible_lines = min(visible_height // LINE_HEIGHT + 1, len(self.lines))
        start_index = int(self.scroll_position // LINE_HEIGHT)

        for i in range(visible_lines):
            line_index = start_index + i
            if 0 <= line_index < len(self.lines):
                text = font.render(self.lines[line_index], True, BLACK)
                y_pos = self.y + i * LINE_HEIGHT - (self.scroll_position % LINE_HEIGHT) + PADDING
                if self.y <= y_pos <= self.y + self.height - LINE_HEIGHT:
                    surface.blit(text, (self.x + PADDING, y_pos))

        # Reset clipping
        surface.set_clip(old_clip)

        # Draw scrollbar background
        pygame.draw.rect(surface, GRAY, self.scrollbar_rect)

        # Draw scrollbar if needed
        if self.total_height > self.height:
            pygame.draw.rect(surface, (100, 100, 100), self.scrollbar_handle_rect)
            pygame.draw.rect(surface, BLACK, self.scrollbar_handle_rect, 1)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface):
        color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                return True
        return False

class StartMenu:
    def __init__(self):
        button_width = 300
        button_height = 50
        center_x = WINDOW_WIDTH // 2 - button_width // 2
        self.true_button = Button(center_x, 300, button_width, button_height,
                                "Convince AI it's TRUE", GREEN)
        self.false_button = Button(center_x, 370, button_width, button_height,
                                 "Convince AI it's FALSE", BLUE)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if self.true_button.handle_event(event):
                    return True
                if self.false_button.handle_event(event):
                    return False

            screen.fill(WHITE)

            # Draw title
            title = large_font.render("Choose Your Role", True, BLACK)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
            screen.blit(title, title_rect)

            # Draw buttons
            self.true_button.draw(screen)
            self.false_button.draw(screen)

            pygame.display.flip()

class AISprite:
    def generate_scenario(self):
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "gemma3:4b",
                    "prompt": """Generate ONE simple, clear scenario for a debate game. The scenario should be:
1. A single clear statement that can be argued true or false
2. Similar to classic conspiracy theories or urban legends
3. Not offensive or controversial
4. Easy to understand and debate
5. No complex or multi-part claims
6. Similar to these examples:
   - "Aliens built the pyramids"
   - "The Earth is flat"
   - "Bigfoot exists in the forests"
   - "Time travel is possible"
   - "Ghosts are real"
   - "The moon landing was faked"
   - "Dinosaurs still exist"
   - "You're living in a simulation"

Rules:
- Keep it to ONE simple statement
- Don't use complex language
- Don't include multiple claims
- Don't reference real people or current events
- Make it fun and engaging to debate

Generate ONE scenario following these examples. Return ONLY the statement, nothing else.""",
                    "stream": False
                }
            )
            scenario = response.json()['response'].strip().strip('"')
            # Clean up any common formatting issues
            scenario = scenario.replace("The statement: ", "").replace("Scenario: ", "").strip()
            return scenario
        except Exception as e:
            # Fallback scenarios if API fails
            fallback_scenarios = [
                "Aliens built the pyramids",
                "The Earth is flat",
                "Bigfoot exists in the forests",
                "Time travel is possible",
                "Ghosts are real",
                "The moon landing was faked",
                "Dinosaurs still exist",
                "You're living in a simulation",
                "Telepathy is real",
                "Dragons once existed"
            ]
            return random.choice(fallback_scenarios)

    def __init__(self, convince_true):
        self.x = WINDOW_WIDTH - 200
        self.y = WINDOW_HEIGHT // 2
        self.conviction = 0 if convince_true else 100  # Start at 100 for false statements
        self.current_scenario = self.generate_scenario()
        self.convince_true = convince_true  # Whether player is trying to convince true or false
        self.response = "Convince me!" if convince_true else "I believe this is true. Prove me wrong!"
        self.thinking = False
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.scale = 1.0
        self.conversation_history = []
        self.complete_history = []  # For saving (keeps everything)
        self.response_count = 0
        self.MAX_RESPONSES = 10
        self.autoplay = False
        self.last_autoplay_time = 0
        self.autoplay_delay = 2000  # 2 seconds between responses
        self.autosave_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create text areas with more space
        self.scenario_area = ScrollableTextArea(50, 50, 600, 100, 5)
        self.conversation_area = ScrollableTextArea(50, 200, 600, 400, 20)
        self.scenario_area.add_line(f"Scenario: {self.current_scenario}")
        self.scenario_area.add_line(f"Your goal: Convince the AI that this is {'TRUE' if convince_true else 'FALSE'}")
        self.scenario_area.add_line(f"Responses remaining: {self.MAX_RESPONSES - self.response_count}")
        self.conversation_area.add_line(f"AI: {self.response}")
        self.complete_history.append(f"AI: {self.response}")  # Add initial response to complete history

        # Autosave initial state
        self.autosave_conversation()

    def draw(self):
        # Animate the AI sprite
        self.animation_frame += self.animation_speed
        if self.thinking:
            self.scale = 1.0 + 0.05 * abs(math.sin(self.animation_frame))
        else:
            self.scale = 1.0

        # Draw AI sprite
        scaled_sprite = pygame.transform.scale(ai_sprite,
            (int(100 * self.scale), int(100 * self.scale)))
        sprite_rect = scaled_sprite.get_rect(center=(self.x, self.y))
        screen.blit(scaled_sprite, sprite_rect)

        # Draw conviction meter bar
        pygame.draw.rect(screen, BLACK, (self.x - 50, self.y + 60, 100, 10))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - 50, self.y + 60, self.conviction, 10))

        # Draw numerical conviction score in the corner
        score_text = f"Conviction: {100 - self.conviction}%" if not self.convince_true else f"Conviction: {self.conviction}%"
        score_surface = font.render(score_text, True, BLACK)
        score_rect = score_surface.get_rect(topright=(WINDOW_WIDTH - 20, 20))
        # Draw background for better visibility
        padding = 5
        bg_rect = pygame.Rect(score_rect.x - padding, score_rect.y - padding,
                            score_rect.width + 2*padding, score_rect.height + 2*padding)
        pygame.draw.rect(screen, LIGHT_GRAY, bg_rect)
        pygame.draw.rect(screen, BLACK, bg_rect, 1)
        screen.blit(score_surface, score_rect)

        # Draw text areas
        self.scenario_area.draw(screen)
        self.conversation_area.draw(screen)

    def get_automated_response(self):
        try:
            # Format conversation history
            history_text = "\n".join(self.conversation_history[-6:] if self.conversation_history else [])

            # Create a prompt for the player AI
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "gemma3:4b",
                    "prompt": f"""You are an AI debater trying to convince another AI about a scenario. Be persuasive and use logical arguments.

🎯 Current scenario: "{self.current_scenario}"
💬 Your goal: Convince the AI that this is {'TRUE' if self.convince_true else 'FALSE'}
⚡ Responses left: {self.MAX_RESPONSES - self.response_count}

Previous conversation:
{history_text}

🔥 Response Guidelines:
- Use compelling evidence and logical arguments
- Be concise but persuasive
- {'Present evidence and logical proofs to support the truth' if self.convince_true else 'Present evidence and logical arguments to disprove this'}
- Adapt your strategy based on the AI\'s previous responses
- For false claims, focus on debunking with facts
- For true claims, focus on providing supporting evidence

{f'🚨 Getting urgent now - only {self.MAX_RESPONSES - self.response_count} chances left to make your point!' if self.MAX_RESPONSES - self.response_count <= 3 else ''}

Your response (write a natural, human-like message):""",
                    "stream": False
                }
            )
            response_text = response.json()['response']

            # Add automated response to conversation area
            self.conversation_area.add_line(f"Player (Auto): {response_text}")
            return response_text

        except Exception as e:
            # Fallback to predefined responses
            if self.convince_true:
                responses = [
                    "Look, I've seen this with my own eyes!",
                    "Let me tell you about my personal experience with this.",
                    "I know this sounds crazy, but hear me out...",
                    "Trust me, I've done a lot of research on this.",
                    "I can show you proof right now.",
                    "This happened to me personally.",
                    "I was skeptical too until I learned about this.",
                    "Think about it logically for a second.",
                    "Let me explain why this makes sense.",
                    "I totally understand your doubt, but..."
                ]
                self.conviction = min(100, self.conviction + 15)
            else:
                responses = [
                    "Wait, that's not right at all!",
                    "I used to believe that too, but then I learned...",
                    "That's a common mistake, let me explain why.",
                    "I know for a fact this isn't true because...",
                    "Trust me, I've looked into this extensively.",
                    "That's just an old myth people keep spreading.",
                    "I thought the same thing until I found out...",
                    "Let me show you why this doesn't make sense.",
                    "I understand why you'd think that, but...",
                    "That's actually been proven wrong many times."
                ]
                self.conviction = max(0, self.conviction - 15)
            fallback_response = random.choice(responses)
            self.conversation_area.add_line(f"Player (Auto-Fallback): {fallback_response}")
            return fallback_response

    def get_ai_response(self, player_input):
        if self.response_count >= self.MAX_RESPONSES:
            # Base victory on conviction score alone
            if self.convince_true:
                if self.conviction >= 70:  # High conviction for true statements
                    self.response = "I'm convinced! You've presented compelling evidence and logical arguments that have changed my mind. I now believe this is true."
                else:
                    self.response = "Discussion over! While you made some interesting points, I remain unconvinced. The evidence wasn't strong enough to change my mind."
            else:
                if self.conviction <= 30:  # Low conviction for false statements
                    self.response = "You're right, it's false! Your arguments and evidence have successfully convinced me that this isn't true. I see now why this belief was incorrect."
                else:
                    self.response = "Discussion over! I still believe this is true. Your arguments were interesting, but not enough to change my mind."
            self.conversation_area.add_line(f"AI: {self.response}")
            self.autosave_conversation()  # Autosave at game end
            return True

        self.response_count += 1
        self.thinking = True
        try:
            # Add current input to conversation area
            self.conversation_area.add_line(f"Player: {player_input}")

            # Keep only last 6 exchanges for display and AI context
            if len(self.conversation_history) > 6:
                self.conversation_history = self.conversation_history[-6:]

            # Format conversation history for AI context
            history_text = "\n".join(self.conversation_history)

            # Adjust the prompt based on whether player is trying to convince true or false
            belief_state = "skeptical" if self.convince_true else "initially believing"
            goal_state = "believe in" if self.convince_true else "doubt"

            # Calculate urgency based on remaining responses
            responses_left = self.MAX_RESPONSES - self.response_count
            urgency_level = "FINAL" if responses_left <= 1 else "URGENT" if responses_left <= 3 else "normal"

            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "gemma3:4b",
                    "prompt": f"""You are a {belief_state} AI character in a game. The player's goal is to make you {goal_state} the current scenario.

🎯 Current scenario: "{self.current_scenario}"
💬 Responses remaining: {responses_left} out of {self.MAX_RESPONSES}
⚡ Urgency level: {urgency_level}
{'🌟 Current stance: You currently believe this is true, but the player is trying to convince you it is false.' if not self.convince_true else ''}

Previous conversation:
{history_text}

🔥 Response Guidelines:
- Be decisive - there are only {responses_left} responses left
- For FALSE scenarios: Start believing, but be open to changing your mind with good evidence
- For TRUE scenarios: Start skeptical, but be open to being convinced with good arguments
- Show your thought process clearly
- If you're convinced, explain why and what changed your mind
- If you're not convinced, explain what evidence would change your mind

{f'🚨 URGENT: With only {responses_left} responses remaining, you must make a strong decision about your final stance!' if responses_left <= 3 else ''}
{f'⚠️ FINAL RESPONSE: You must definitively decide if you are convinced or not!' if responses_left <= 1 else ''}

Your response:""",
                    "stream": False
                }
            )
            response_text = response.json()['response']
            self.response = response_text

            # Add AI response to conversation area
            self.conversation_area.add_line(f"AI: {response_text}")

            # Autosave after each interaction
            self.autosave_conversation()

            # Update conviction based on response content
            if self.convince_true:
                if any(word in response_text.lower() for word in ["you make a good point", "that's compelling", "i'm starting to believe", "you might be right", "i see your point", "that makes sense"]):
                    self.conviction = min(100, self.conviction + 25)
                elif any(word in response_text.lower() for word in ["maybe", "possibly", "could be", "might", "interesting", "that makes sense"]):
                    self.conviction = min(100, self.conviction + 15)
                elif any(word in response_text.lower() for word in ["no", "don't", "not", "never", "doubt", "skeptical"]):
                    self.conviction = max(0, self.conviction - 10)
            else:
                if any(word in response_text.lower() for word in ["you make a good point", "that's compelling", "i'm starting to doubt", "you might be right", "i see your point", "that makes sense"]):
                    self.conviction = max(0, self.conviction - 25)
                elif any(word in response_text.lower() for word in ["doubt", "maybe not", "could be wrong", "might not", "questionable"]):
                    self.conviction = max(0, self.conviction - 15)
                elif any(word in response_text.lower() for word in ["certain", "sure", "definitely", "absolutely"]):
                    self.conviction = min(100, self.conviction + 10)

            # Force a decision on the last response if conviction is appropriate
            responses_left = self.MAX_RESPONSES - self.response_count
            if responses_left <= 1:
                if self.convince_true and self.conviction >= 70:
                    self.conviction = 100
                    final_response = "I'm convinced! Your arguments and evidence have successfully changed my mind. I now believe this is true."
                    self.conversation_area.add_line(f"AI: {final_response}")
                    return True
                elif not self.convince_true and self.conviction <= 30:
                    self.conviction = 0
                    final_response = "You're right, it's false! Your evidence and reasoning have convinced me that this isn't true. I see now why this belief was incorrect."
                    self.conversation_area.add_line(f"AI: {final_response}")
                    return True

        except Exception as e:
            error_response = "Error connecting to AI model"
            self.conversation_area.add_line(f"AI: {error_response}")
            self.autosave_conversation()  # Autosave even after error
        self.thinking = False
        return False

    def autosave_conversation(self):
        # Create an autosave file with timestamp of game start
        if not hasattr(self, 'autosave_timestamp'):
            self.autosave_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure conversations directory exists
        if not os.path.exists("conversations"):
            os.makedirs("conversations")

        filename = f"conversations/autosave_{self.autosave_timestamp}.txt"

        try:
            with open(filename, "w") as f:
                f.write(f"Scenario: {self.current_scenario}\n")
                f.write(f"Goal: Convince AI that this is {'TRUE' if self.convince_true else 'FALSE'}\n")
                f.write(f"Current Conviction: {self.conviction}%\n")
                f.write(f"Responses remaining: {self.MAX_RESPONSES - self.response_count}\n")
                f.write("\nConversation:\n")
                f.write("-" * 50 + "\n")

                # Group lines into exchanges (player + AI)
                exchanges = []
                current_exchange = []
                for line in self.conversation_area.lines:
                    current_exchange.append(line)
                    if line.startswith("AI:"):
                        exchanges.append(current_exchange)
                        current_exchange = []

                # Write each exchange with a separator
                for exchange in exchanges:
                    for line in exchange:
                        f.write(f"{line}\n")
                    f.write("-" * 50 + "\n")

                # Write any remaining lines
                for line in current_exchange:
                    f.write(f"{line}\n")

        except Exception as e:
            print(f"Autosave failed: {str(e)}")

    def reset(self):
        # Create new autosave timestamp for new game
        self.autosave_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.conviction = 0 if self.convince_true else 100
        self.current_scenario = self.generate_scenario()
        self.response = "Convince me!" if self.convince_true else "I believe this is true. Prove me wrong!"
        self.conversation_history = []
        self.complete_history = []
        self.response_count = 0
        self.scenario_area.clear()
        self.conversation_area.clear()
        self.scenario_area.add_line(f"Scenario: {self.current_scenario}")
        self.scenario_area.add_line(f"Your goal: Convince the AI that this is {'TRUE' if self.convince_true else 'FALSE'}")
        self.scenario_area.add_line(f"Responses remaining: {self.MAX_RESPONSES - self.response_count}")
        self.conversation_area.add_line(f"AI: {self.response}")
        self.complete_history.append(f"AI: {self.response}")

        # Autosave initial state
        self.autosave_conversation()

class Player:
    def __init__(self):
        self.x = 100
        self.y = WINDOW_HEIGHT // 2
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.scale = 1.0

    def draw(self):
        # Animate the player sprite
        self.animation_frame += self.animation_speed
        self.scale = 1.0 + 0.02 * abs(math.sin(self.animation_frame))

        # Draw player sprite
        scaled_sprite = pygame.transform.scale(player_sprite,
            (int(100 * self.scale), int(100 * self.scale)))
        sprite_rect = scaled_sprite.get_rect(center=(self.x, self.y))
        screen.blit(scaled_sprite, sprite_rect)

class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.text_width = width - (2 * PADDING)
        self.lines = []
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 30  # Frames per blink

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if event.mod & pygame.KMOD_SHIFT:  # Shift+Enter for new line
                    self.text += '\n'
                    return None
                elif self.text.strip():  # Regular Enter to submit
                    text = self.text
                    self.text = ""
                    self.lines = []
                    return text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            # Wrap text
            self.lines = wrap_text(self.text.replace('\n', ' '), font, self.text_width)
        return None

    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        # Draw text
        y = self.rect.y + PADDING
        for line in self.lines:
            text_surface = font.render(line, True, BLACK)
            surface.blit(text_surface, (self.rect.x + PADDING, y))
            y += LINE_HEIGHT

        # Draw cursor
        if self.active:
            self.cursor_timer = (self.cursor_timer + 1) % (self.cursor_blink_rate * 2)
            if self.cursor_timer < self.cursor_blink_rate:
                if self.lines:
                    last_line = self.lines[-1]
                    cursor_x = self.rect.x + PADDING + font.size(last_line)[0]
                    cursor_y = self.rect.y + PADDING + (len(self.lines) - 1) * LINE_HEIGHT
                else:
                    cursor_x = self.rect.x + PADDING
                    cursor_y = self.rect.y + PADDING
                pygame.draw.line(surface, BLACK, (cursor_x, cursor_y),
                               (cursor_x, cursor_y + LINE_HEIGHT))

def main():
    # Start with the menu
    menu = StartMenu()
    convince_true = menu.run()

    if convince_true is None:  # User closed the window
        return

    clock = pygame.time.Clock()
    ai = AISprite(convince_true)
    player = Player()
    input_box = InputBox(50, WINDOW_HEIGHT - 100, WINDOW_WIDTH - 100, 80)
    game_over = False

    # Create autoplay button
    autoplay_button = Button(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 50, 120, 40, "Autoplay", BLUE)

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # Handle text area scrolling
            ai.scenario_area.handle_event(event)
            ai.conversation_area.handle_event(event)

            # Handle autoplay button
            if autoplay_button.handle_event(event):
                ai.autoplay = not ai.autoplay
                ai.last_autoplay_time = current_time
                autoplay_button.text = "Stop Auto" if ai.autoplay else "Autoplay"

            # Handle input box if not in autoplay mode
            if not ai.autoplay:
                result = input_box.handle_event(event)
                if result is not None and not game_over:
                    game_over = ai.get_ai_response(result)

        # Handle autoplay logic
        if ai.autoplay and not game_over and current_time - ai.last_autoplay_time >= ai.autoplay_delay:
            automated_response = ai.get_automated_response()
            game_over = ai.get_ai_response(automated_response)
            ai.last_autoplay_time = current_time

        screen.fill(WHITE)

        # Draw input box (grayed out during autoplay)
        if ai.autoplay:
            pygame.draw.rect(screen, GRAY, input_box.rect)
        input_box.draw(screen)

        # Draw sprites
        player.draw()
        ai.draw()

        # Draw autoplay button
        autoplay_button.draw(screen)

        # Check if game is over
        if game_over:
            if (ai.convince_true and ai.conviction >= 100) or (not ai.convince_true and ai.conviction <= 0):
                win_text = font.render("You convinced the AI! Press R to restart", True, BLACK)
            else:
                if ai.convince_true:
                    win_text = font.render("Game Over - AI remains unconvinced! Press R to restart", True, BLACK)
                else:
                    win_text = font.render("Game Over - AI still believes it's true! Press R to restart", True, BLACK)
            screen.blit(win_text, (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2))

            # Stop autoplay when game ends
            ai.autoplay = False
            autoplay_button.text = "Autoplay"

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                ai.reset()
                game_over = False

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()