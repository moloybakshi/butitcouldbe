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
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (245, 245, 245)
PRIMARY_COLOR = (52, 152, 219)  # Bright blue
SECONDARY_COLOR = (46, 204, 113)  # Bright green
ACCENT_COLOR = (231, 76, 60)  # Bright red
BACKGROUND_COLOR = (236, 240, 241)  # Light grayish background
TEXT_COLOR = (44, 62, 80)  # Dark blue-gray for text

# Adjusted font sizes and line heights
FONT_SIZE = 20  # Reduced from 28
LARGE_FONT_SIZE = 32  # New constant for larger text
SMALL_FONT_SIZE = 16  # New constant for smaller text
LINE_HEIGHT = 28  # Reduced from 36
PADDING = 12  # Slightly reduced from 15
BORDER_RADIUS = 10  # Slightly reduced from 12

# Define emoji constants
EMOJI_SCENARIO = "📜"
EMOJI_GOAL = "🎯"
EMOJI_RESPONSES = "💬"
EMOJI_AI = "🤖"
EMOJI_SEND = "➤"
EMOJI_AUTO = "⚡"
EMOJI_WIN = "✨"
EMOJI_LOSE = "✖"
EMOJI_RESTART = "🔄"

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Convince the AI!")

# Try to load custom fonts, fall back to default if not available
try:
    # Try to load system fonts that support emojis
    font_names = [
        "Segoe UI Emoji",  # Windows
        "Apple Color Emoji",  # macOS
        "Noto Color Emoji",  # Linux
        "Arial Unicode MS",  # Common fallback
        "Arial"  # Final fallback
    ]

    font = None
    large_font = None
    small_font = None

    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, FONT_SIZE)
            large_font = pygame.font.SysFont(font_name, LARGE_FONT_SIZE)
            small_font = pygame.font.SysFont(font_name, SMALL_FONT_SIZE)

            # Test emoji rendering
            test_text = "🎮🎯💬📝"
            test_surface = font.render(test_text, True, BLACK)
            if test_surface.get_width() > 0:  # If emojis rendered successfully
                break
        except:
            continue

    if font is None:
        font = pygame.font.Font(None, FONT_SIZE)
        large_font = pygame.font.Font(None, LARGE_FONT_SIZE)
        small_font = pygame.font.Font(None, SMALL_FONT_SIZE)

except Exception as e:
    print(f"Font loading error: {str(e)}")
    font = pygame.font.Font(None, FONT_SIZE)
    large_font = pygame.font.Font(None, LARGE_FONT_SIZE)
    small_font = pygame.font.Font(None, SMALL_FONT_SIZE)

# Create fonts directory if it doesn't exist
if not os.path.exists("assets/fonts"):
    os.makedirs("assets/fonts")

# Create placeholder sprites if they don't exist
def create_placeholder_sprites():
    # AI sprite (modern robot)
    ai_surface = pygame.Surface((150, 150), pygame.SRCALPHA)  # Increased size

    # Body (rounded rectangle)
    pygame.draw.rect(ai_surface, PRIMARY_COLOR, (25, 35, 100, 80), border_radius=15)

    # Head (circle)
    pygame.draw.circle(ai_surface, PRIMARY_COLOR, (75, 50), 35)

    # Eyes (white circles with black pupils)
    pygame.draw.circle(ai_surface, WHITE, (60, 45), 12)
    pygame.draw.circle(ai_surface, WHITE, (90, 45), 12)
    pygame.draw.circle(ai_surface, BLACK, (60, 45), 6)
    pygame.draw.circle(ai_surface, BLACK, (90, 45), 6)

    # Antenna
    pygame.draw.rect(ai_surface, PRIMARY_COLOR, (70, 10, 10, 20))
    pygame.draw.circle(ai_surface, ACCENT_COLOR, (75, 5), 8)

    # Digital smile
    points = [(55, 65), (75, 75), (95, 65)]
    pygame.draw.lines(ai_surface, WHITE, False, points, 3)

    ai_surface = pygame.transform.scale(ai_surface, (150, 150))
    pygame.image.save(ai_surface, "assets/sprites/ai_sprite.png")

    # Player sprite (modern avatar)
    player_surface = pygame.Surface((150, 150), pygame.SRCALPHA)  # Increased size

    # Head (circle with gradient)
    pygame.draw.circle(player_surface, (255, 200, 150), (75, 75), 50)  # Base color

    # Eyes (almond shaped)
    pygame.draw.ellipse(player_surface, WHITE, (55, 60, 20, 15))
    pygame.draw.ellipse(player_surface, WHITE, (85, 60, 20, 15))
    pygame.draw.ellipse(player_surface, BLACK, (60, 62, 10, 10))
    pygame.draw.ellipse(player_surface, BLACK, (90, 62, 10, 10))

    # Smile (curved line)
    pygame.draw.arc(player_surface, BLACK, (55, 70, 40, 30), 0, 3.14, 3)

    # Hair
    for i in range(0, 360, 30):
        angle = math.radians(i)
        x = 75 + 45 * math.cos(angle)
        y = 75 + 45 * math.sin(angle)
        if y < 75:  # Only draw hair on top half
            pygame.draw.line(player_surface, BLACK, (75, 75), (x, y), 3)

    player_surface = pygame.transform.scale(player_surface, (150, 150))
    pygame.image.save(player_surface, "assets/sprites/player_sprite.png")

# Create placeholder sprites if they don't exist
if not os.path.exists("assets/sprites/ai_sprite.png"):
    create_placeholder_sprites()

# Load sprites
ai_sprite = pygame.image.load("assets/sprites/ai_sprite.png").convert_alpha()
player_sprite = pygame.image.load("assets/sprites/player_sprite.png").convert_alpha()

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
        # Draw background with rounded corners
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=BORDER_RADIUS)

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
                text = font.render(self.lines[line_index], True, TEXT_COLOR)
                y_pos = self.y + i * LINE_HEIGHT - (self.scroll_position % LINE_HEIGHT) + PADDING
                if self.y <= y_pos <= self.y + self.height - LINE_HEIGHT:
                    surface.blit(text, (self.x + PADDING, y_pos))

        # Reset clipping
        surface.set_clip(old_clip)

        # Draw scrollbar background
        pygame.draw.rect(surface, LIGHT_GRAY, self.scrollbar_rect, border_radius=BORDER_RADIUS)

        # Draw scrollbar if needed
        if self.total_height > self.height:
            pygame.draw.rect(surface, PRIMARY_COLOR, self.scrollbar_handle_rect, border_radius=BORDER_RADIUS)
            pygame.draw.rect(surface, TEXT_COLOR, self.scrollbar_handle_rect, 1, border_radius=BORDER_RADIUS)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        self.pressed = False
        self.animation_scale = 1.0
        self.is_restart = "Restart" in text  # Check if this is a restart button

    def draw(self, surface):
        # Draw button with animation
        button_rect = self.rect.copy()
        if self.pressed:
            button_rect.x += 2
            button_rect.y += 2
            self.animation_scale = 0.95
        elif self.hover:
            self.animation_scale = 1.05
        else:
            self.animation_scale = 1.0

        # Draw button background with gradient effect
        if self.is_restart:
            # Restart button has a different hover color scheme
            color = tuple(min(c + 50, 255) for c in self.color) if self.hover else self.color
        else:
            color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color

        pygame.draw.rect(surface, color, button_rect, border_radius=BORDER_RADIUS)

        # Draw text
        text_color = WHITE if self.is_restart else TEXT_COLOR
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)

        # Apply scale animation
        text_rect.width *= self.animation_scale
        text_rect.height *= self.animation_scale

        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False
        return False

class StartMenu:
    def __init__(self):
        button_width = 300
        button_height = 50
        center_x = WINDOW_WIDTH // 2 - button_width // 2
        self.true_button = Button(center_x, 300, button_width, button_height,
                                "Convince AI it's TRUE", SECONDARY_COLOR)
        self.false_button = Button(center_x, 370, button_width, button_height,
                                 "Convince AI it's FALSE", PRIMARY_COLOR)

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

            # Draw title with large font
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
            # First attempt with entertaining but thought-provoking prompt
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "gemma3:4b",
                    "prompt": """Generate ONE entertaining but thought-provoking statement for debate. The statement should be:
1. A clear declarative statement (not a question)
2. Something that could be argued as true or false
3. Combines everyday things with bigger concepts
4. Has a touch of humor while being debatable
5. Could have interesting evidence on both sides

Examples of good statements:
- "Cats possess an innate understanding of quantum physics"
- "Procrastination is actually a form of time travel"
- "Pizza tastes better because it believes in you"
- "Houseplants secretly judge our life choices"
- "Parallel universes are created by lost socks in the dryer"
- "The internet experiences emotions just like humans do"
- "Smartphones intentionally die at dramatic moments"
- "Dreams are bug reports from the simulation we live in"

Rules:
- Must be a STATEMENT, not a question
- Should be debatable but not absurd
- Mix mundane objects with profound concepts
- Keep it relatable but intriguing
- Make it fun but arguable

Generate ONE entertaining statement. Return ONLY the statement, nothing else.""",
                    "stream": False
                }
            )

            scenario = response.json()['response'].strip().strip('"')

            # If the response is empty or too short, try a second prompt
            if len(scenario) < 10:
                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        "model": "gemma3:4b",
                        "prompt": """Create ONE amusing debate statement about:
- Everyday objects having secret lives
- Technology having hidden wisdom
- Food having metaphysical properties
- Pets having cosmic knowledge
- Time having personal preferences
- Common annoyances having deeper meaning

Make it a clear declarative statement (not a question).
Return ONLY the statement.""",
                        "stream": False
                    }
                )
                scenario = response.json()['response'].strip().strip('"')

            # Clean up any common formatting issues
            scenario = scenario.replace("The statement: ", "").replace("Scenario: ", "").strip()

            # Convert questions to statements if needed
            if scenario.endswith("?"):
                scenario = scenario[:-1] + "."
            if scenario.lower().startswith("what if "):
                scenario = scenario[8:].capitalize()
            if scenario.lower().startswith("why do "):
                scenario = scenario[7:].capitalize() + " because of cosmic laws."

            # If still empty or too short, generate a procedural scenario
            if len(scenario) < 10:
                # Generate a procedural scenario using entertaining templates
                subjects = [
                    "Your coffee maker",
                    "The internet",
                    "Traffic lights",
                    "Your bed",
                    "Social media",
                    "The refrigerator",
                    "Your favorite song",
                    "The weekend",
                    "Your computer",
                    "The weather"
                ]
                verbs = [
                    "possesses the wisdom of",
                    "secretly controls",
                    "understands",
                    "manipulates",
                    "communicates with",
                    "influences",
                    "philosophically aligns with",
                    "channels the energy of",
                    "transcends",
                    "bends"
                ]
                effects = [
                    "ancient cosmic knowledge",
                    "the space-time continuum",
                    "quantum mathematics",
                    "parallel dimensions",
                    "universal consciousness",
                    "metaphysical reality",
                    "the laws of physics",
                    "human motivation",
                    "cosmic harmony",
                    "the collective unconscious"
                ]

                scenario = f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(effects)}"

            print(f"Generated scenario: {scenario}")  # Debug logging
            return scenario

        except Exception as e:
            print(f"Error generating scenario: {str(e)}")  # Debug logging
            # Generate a procedural scenario as fallback
            topics = [
                "Smartphones possess emotional intelligence",
                "Vegetables experience philosophical enlightenment",
                "The internet has achieved consciousness",
                "Cars develop personalities based on their owners",
                "Mirrors reflect alternate realities",
                "Gym equipment conspires for human health",
                "Calendars manipulate the flow of time",
                "Autocorrect has literary aspirations",
                "Keys teleport to test human patience",
                "Clouds are shepherds of cosmic energy"
            ]

            return random.choice(topics)

    def __init__(self, convince_true):
        self.x = WINDOW_WIDTH - 250  # Adjusted position
        self.y = WINDOW_HEIGHT // 2
        self.conviction = 0 if convince_true else 100
        self.current_scenario = self.generate_scenario()
        self.convince_true = convince_true
        self.response = "Convince me!" if convince_true else "I believe this is true. Prove me wrong!"
        self.thinking = False
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.scale = 1.0
        self.conversation_history = []
        self.complete_history = []
        self.response_count = 0
        self.MAX_RESPONSES = 10
        self.autoplay = False
        self.last_autoplay_time = 0
        self.autoplay_delay = 2000
        self.autosave_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.waiting_for_auto_response = False  # New flag for single auto response
        self.thinking_dots = 0
        self.last_dot_update = 0
        self.dot_update_delay = 500  # Update dots every 500ms

        # Create text areas with adjusted spacing for new font sizes
        self.scenario_area = ScrollableTextArea(50, 30, WINDOW_WIDTH - 400, 100, 5)
        self.conversation_area = ScrollableTextArea(50, 150, WINDOW_WIDTH - 400, WINDOW_HEIGHT - 300, 20)

        # Add content with better formatting and simpler Unicode
        self.scenario_area.add_line(f"{EMOJI_SCENARIO} Scenario: {self.current_scenario}")
        self.scenario_area.add_line(f"{EMOJI_GOAL} Your goal: Convince the AI that this is {'TRUE' if convince_true else 'FALSE'}")
        self.scenario_area.add_line(f"{EMOJI_RESPONSES} Responses remaining: {self.MAX_RESPONSES - self.response_count}")
        self.conversation_area.add_line(f"{EMOJI_AI} AI: {self.response}")
        self.complete_history.append(f"AI: {self.response}")

        self.autosave_conversation()

    def draw(self):
        # Animate the AI sprite
        self.animation_frame += self.animation_speed
        if self.thinking:
            self.scale = 1.0 + 0.05 * abs(math.sin(self.animation_frame))

            # Update thinking dots animation
            current_time = pygame.time.get_ticks()
            if current_time - self.last_dot_update > self.dot_update_delay:
                self.thinking_dots = (self.thinking_dots + 1) % 4
                self.last_dot_update = current_time

            # Draw thinking indicator
            dots = "." * self.thinking_dots
            thinking_text = f"Thinking{dots}"
            thinking_surface = font.render(thinking_text, True, PRIMARY_COLOR)
            thinking_rect = thinking_surface.get_rect(center=(self.x, self.y + 150))
            screen.blit(thinking_surface, thinking_rect)
        else:
            self.scale = 1.0

        # Draw AI sprite
        scaled_sprite = pygame.transform.scale(ai_sprite,
            (int(150 * self.scale), int(150 * self.scale)))  # Larger sprite
        sprite_rect = scaled_sprite.get_rect(center=(self.x, self.y))
        screen.blit(scaled_sprite, sprite_rect)

        # Draw conviction meter with modern style
        meter_width = 200  # Wider meter
        meter_height = 15  # Taller meter

        # Draw meter background with gradient
        pygame.draw.rect(screen, LIGHT_GRAY,
                        (self.x - meter_width//2, self.y + 100, meter_width, meter_height),
                        border_radius=meter_height//2)

        # Draw conviction level
        conviction_width = int(meter_width * (self.conviction / 100))
        if conviction_width > 0:
            pygame.draw.rect(screen, PRIMARY_COLOR if self.convince_true else ACCENT_COLOR,
                           (self.x - meter_width//2, self.y + 100, conviction_width, meter_height),
                           border_radius=meter_height//2)

        # Draw conviction score with appropriate font sizes
        score = self.conviction if self.convince_true else 100 - self.conviction
        score_text = f"{score}%"

        # Draw score in a circular badge with large font for the number
        circle_radius = 35  # Slightly smaller
        circle_pos = (WINDOW_WIDTH - circle_radius - 20, circle_radius + 20)

        # Draw outer circle with gradient
        for i in range(5):
            radius = circle_radius - i
            color = PRIMARY_COLOR if self.convince_true else ACCENT_COLOR
            color = tuple(min(c + i*10, 255) for c in color)
            pygame.draw.circle(screen, color, circle_pos, radius)

        # Draw inner circle
        inner_radius = circle_radius - 5
        pygame.draw.circle(screen, WHITE, circle_pos, inner_radius)

        # Draw score text with large font
        score_surface = large_font.render(score_text, True, TEXT_COLOR)
        score_rect = score_surface.get_rect(center=circle_pos)
        screen.blit(score_surface, score_rect)

        # Draw "CONVICTION" text below with small font
        label_surface = small_font.render("CONVICTION", True, TEXT_COLOR)
        label_rect = label_surface.get_rect(center=(circle_pos[0], circle_pos[1] + circle_radius + 10))
        screen.blit(label_surface, label_rect)

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
            # More varied end-game responses
            if self.convince_true:
                if self.conviction >= 70:
                    endings = [
                        "You've done it! Your compelling evidence and logical reasoning have won me over. I now see the truth in this.",
                        "I can't deny it anymore - you've presented such strong arguments that I'm fully convinced now.",
                        "What a revelation! Your evidence has completely changed my perspective. I believe you're right.",
                        "Remarkable! You've successfully shown me the truth. Your arguments were absolutely convincing."
                    ]
                else:
                    endings = [
                        "Time's up! While you raised some interesting points, I'm still not convinced by the evidence.",
                        "Nice try, but your arguments weren't quite strong enough to change my mind on this.",
                        "I appreciate the effort, but I remain skeptical. The evidence just wasn't compelling enough.",
                        "We're done here, and I'm still not seeing enough proof to believe this claim."
                    ]
            else:
                if self.conviction <= 30:
                    endings = [
                        "You've successfully debunked this! Your evidence has thoroughly disproven my initial belief.",
                        "I stand corrected! Your arguments have completely dismantled my previous position.",
                        "I was wrong - you've shown me clear evidence that this isn't true at all.",
                        "You've convinced me completely. The evidence against this is overwhelming."
                    ]
                else:
                    endings = [
                        "Time's up! Your arguments weren't enough to shake my conviction in this.",
                        "I've heard your points, but I still believe this is true. You haven't provided enough evidence.",
                        "Sorry, but I remain convinced. Your arguments didn't effectively counter the evidence.",
                        "We're done, and I still stand by my initial position. The counter-arguments weren't strong enough."
                    ]
            self.response = random.choice(endings)
            self.conversation_area.add_line(f"AI: {self.response}")
            self.complete_history.append(f"AI: {self.response}")
            self.autosave_conversation()
            return True

        self.response_count += 1
        self.thinking = True
        self.thinking_dots = 0
        self.last_dot_update = pygame.time.get_ticks()

        # Add "Thinking..." to conversation area immediately
        self.conversation_area.add_line(f"AI: Thinking...")

        try:
            # Add current input to conversation area and history
            self.conversation_area.add_line(f"Player: {player_input}")
            self.conversation_history.append(f"Player: {player_input}")
            self.complete_history.append(f"Player: {player_input}")

            # Keep only last 6 exchanges for context
            history_pairs = []
            for i in range(0, len(self.conversation_history)-1, 2):
                if i+1 < len(self.conversation_history):
                    history_pairs.append((self.conversation_history[i], self.conversation_history[i+1]))
            history_pairs = history_pairs[-3:]  # Keep last 3 exchanges

            # Format conversation history for AI context
            history_text = ""
            for player_msg, ai_msg in history_pairs:
                history_text += f"{player_msg}\n{ai_msg}\n\n"
            history_text += f"Player: {player_input}\n"  # Add current input

            # Calculate response style based on conviction and responses left
            responses_left = self.MAX_RESPONSES - self.response_count
            conviction_level = "high" if self.conviction > 70 else "low" if self.conviction < 30 else "medium"

            # Generate dynamic personality traits based on game state
            personality_traits = []
            if self.convince_true:
                if conviction_level == "low":
                    personality_traits = ["deeply skeptical", "requires solid evidence", "analytically minded"]
                elif conviction_level == "medium":
                    personality_traits = ["cautiously interested", "open to new ideas", "thoughtfully considering"]
                else:
                    personality_traits = ["nearly convinced", "excited by the evidence", "eager to understand more"]
            else:
                if conviction_level == "high":
                    personality_traits = ["strongly convinced", "confident in their belief", "seeking to understand opposing views"]
                elif conviction_level == "medium":
                    personality_traits = ["starting to question", "weighing both sides", "carefully analyzing"]
                else:
                    personality_traits = ["doubting their position", "reconsidering the evidence", "open to being wrong"]

            # Extract key points from player's argument
            key_points_prompt = f"""Extract 2-3 key points from this argument: "{player_input}"
            Format: Just the points, one per line, no numbers or bullets."""

            key_points_response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "gemma3:4b",
                    "prompt": key_points_prompt,
                    "stream": False
                }
            )
            key_points = key_points_response.json()['response'].strip()

            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "gemma3:4b",
                    "prompt": f"""You are an AI with a distinct personality in a debate about: "{self.current_scenario}"

Your Current State:
- Personality: {random.choice(personality_traits)}
- Conviction Level: {conviction_level}
- Responses Left: {responses_left}
- Goal: You are {'being convinced this is true' if self.convince_true else 'being convinced this is false'}

Key Points from Player's Latest Argument:
{key_points}

Recent Conversation History:
{history_text}

Response Guidelines:
1. NEVER use generic phrases like "Hmm" or "Interesting"
2. ALWAYS address at least one specific point from the player's argument
3. Base your response on your conviction level:
   - High conviction: Challenge their evidence firmly but fairly
   - Medium conviction: Show openness while raising specific concerns
   - Low conviction: Acknowledge good points while seeking final clarification
4. Show clear reasoning for why you agree or disagree with their points
5. If nearing the end ({responses_left} responses left), be more decisive
6. Keep responses concise but meaningful

Write a natural response that directly addresses their argument:""",
                    "stream": False
                }
            )
            response_text = response.json()['response']
            self.response = response_text

            # Remove the "Thinking..." line before adding the actual response
            self.conversation_area.lines.pop()
            self.conversation_area.add_line(f"AI: {response_text}")
            self.conversation_history.append(f"AI: {response_text}")
            self.complete_history.append(f"AI: {response_text}")
            self.autosave_conversation()

            # Update conviction based on response content and current state
            conviction_change = 0
            positive_indicators = ["compelling", "convincing", "good point", "makes sense", "i see", "you're right", "valid", "agree"]
            negative_indicators = ["doubt", "skeptical", "not sure", "unconvinced", "disagree", "but still", "however", "yet"]
            strong_indicators = ["absolutely", "completely", "definitely", "totally", "fully", "strongly"]

            # Calculate base conviction change
            response_lower = response_text.lower()
            if self.convince_true:
                for indicator in positive_indicators:
                    if indicator in response_lower:
                        base_change = 10
                        # Check if indicator is preceded by a strong indicator
                        for strong in strong_indicators:
                            if f"{strong} {indicator}" in response_lower:
                                base_change *= 1.5
                        conviction_change += base_change
                for indicator in negative_indicators:
                    if indicator in response_lower:
                        conviction_change -= 5
            else:
                for indicator in positive_indicators:
                    if indicator in response_lower:
                        base_change = 10
                        for strong in strong_indicators:
                            if f"{strong} {indicator}" in response_lower:
                                base_change *= 1.5
                        conviction_change -= base_change
                for indicator in negative_indicators:
                    if indicator in response_lower:
                        conviction_change += 5

            # Apply conviction change with momentum and context
            if self.convince_true:
                if self.conviction > 50:  # Already leaning towards convinced
                    conviction_change *= 1.5
                elif responses_left <= 3:  # Near the end
                    conviction_change *= 1.2
                self.conviction = min(100, max(0, self.conviction + conviction_change))
            else:
                if self.conviction < 50:  # Already leaning towards doubt
                    conviction_change *= 1.5
                elif responses_left <= 3:  # Near the end
                    conviction_change *= 1.2
                self.conviction = min(100, max(0, self.conviction + conviction_change))

            # Force a decision on the last response if appropriate
            if responses_left <= 1:
                if self.convince_true and self.conviction >= 70:
                    self.conviction = 100
                    return True
                elif not self.convince_true and self.conviction <= 30:
                    self.conviction = 0
                    return True

        except Exception as e:
            # Remove the "Thinking..." line before adding the error response
            self.conversation_area.lines.pop()
            error_response = "Error connecting to AI model"
            self.conversation_area.add_line(f"AI: {error_response}")
            self.complete_history.append(f"AI: {error_response}")
            self.autosave_conversation()

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
        self.scenario_area.add_line(f"{EMOJI_SCENARIO} Scenario: {self.current_scenario}")
        self.scenario_area.add_line(f"{EMOJI_GOAL} Your goal: Convince the AI that this is {'TRUE' if self.convince_true else 'FALSE'}")
        self.scenario_area.add_line(f"{EMOJI_RESPONSES} Responses remaining: {self.MAX_RESPONSES - self.response_count}")
        self.conversation_area.add_line(f"{EMOJI_AI} AI: {self.response}")
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
        self.cursor_blink_rate = 30
        self.selection_start = None
        self.selection_end = None
        self.cursor_pos = 0
        self.placeholder_text = "Type your argument here..."
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
            # Handle mouse click
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                # Calculate cursor position based on click
                click_x = event.pos[0] - (self.rect.x + PADDING)
                click_y = event.pos[1] - (self.rect.y + PADDING)
                line_index = click_y // LINE_HEIGHT
                if line_index < len(self.lines):
                    line = self.lines[line_index]
                    for i, char in enumerate(line):
                        if font.size(line[:i])[0] > click_x:
                            self.cursor_pos = sum(len(l) for l in self.lines[:line_index]) + i
                            break
                    else:
                        self.cursor_pos = sum(len(l) for l in self.lines[:line_index]) + len(line)
                self.selection_start = self.cursor_pos
                self.selection_end = self.cursor_pos
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click release
            if self.active and self.dragging:
                self.selection_end = self.cursor_pos
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.active and self.dragging:  # Only update selection while dragging
                click_x = event.pos[0] - (self.rect.x + PADDING)
                click_y = event.pos[1] - (self.rect.y + PADDING)
                line_index = max(0, min(len(self.lines) - 1, click_y // LINE_HEIGHT))
                if line_index < len(self.lines):
                    line = self.lines[line_index]
                    for i, char in enumerate(line):
                        if font.size(line[:i])[0] > click_x:
                            self.cursor_pos = sum(len(l) for l in self.lines[:line_index]) + i
                            break
                    else:
                        self.cursor_pos = sum(len(l) for l in self.lines[:line_index]) + len(line)
                    self.selection_end = self.cursor_pos

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if event.mod & pygame.KMOD_SHIFT:  # Shift+Enter for new line
                    self.text += '\n'
                    return None
                elif self.text.strip():  # Regular Enter to submit
                    text = self.text
                    self.text = ""
                    self.lines = []
                    self.selection_start = None
                    self.selection_end = None
                    self.cursor_pos = 0
                    return text
            elif event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None and self.selection_start != self.selection_end:
                    # Delete selected text
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text = self.text[:start] + self.text[end:]
                    self.cursor_pos = start
                    self.selection_start = self.selection_end = None
                elif self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.selection_start is not None and self.selection_start != self.selection_end:
                    # Delete selected text
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text = self.text[:start] + self.text[end:]
                    self.cursor_pos = start
                    self.selection_start = self.selection_end = None
                elif self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                if event.mod & pygame.KMOD_SHIFT:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    if self.cursor_pos > 0:
                        self.cursor_pos -= 1
                        self.selection_end = self.cursor_pos
                else:
                    if self.selection_start is not None:
                        self.cursor_pos = min(self.selection_start, self.selection_end)
                        self.selection_start = self.selection_end = None
                    elif self.cursor_pos > 0:
                        self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                if event.mod & pygame.KMOD_SHIFT:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    if self.cursor_pos < len(self.text):
                        self.cursor_pos += 1
                        self.selection_end = self.cursor_pos
                else:
                    if self.selection_start is not None:
                        self.cursor_pos = max(self.selection_start, self.selection_end)
                        self.selection_start = self.selection_end = None
                    elif self.cursor_pos < len(self.text):
                        self.cursor_pos += 1
            elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                if self.selection_start is not None and self.selection_start != self.selection_end:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    pygame.scrap.put(pygame.SCRAP_TEXT, self.text[start:end].encode())
            elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                try:
                    clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT).decode()
                    if self.selection_start is not None and self.selection_start != self.selection_end:
                        start = min(self.selection_start, self.selection_end)
                        end = max(self.selection_start, self.selection_end)
                        self.text = self.text[:start] + clipboard_text + self.text[end:]
                        self.cursor_pos = start + len(clipboard_text)
                        self.selection_start = self.selection_end = None
                    else:
                        self.text = self.text[:self.cursor_pos] + clipboard_text + self.text[self.cursor_pos:]
                        self.cursor_pos += len(clipboard_text)
                except:
                    pass
            elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                # Select all text
                self.selection_start = 0
                self.selection_end = len(self.text)
                self.cursor_pos = self.selection_end
            else:
                if self.selection_start is not None and self.selection_start != self.selection_end:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text = self.text[:start] + event.unicode + self.text[end:]
                    self.cursor_pos = start + 1
                    self.selection_start = self.selection_end = None
                else:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
            # Wrap text
            self.lines = wrap_text(self.text.replace('\n', ' '), font, self.text_width)
        return None

    def draw(self, surface):
        # Draw background with subtle gradient
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=BORDER_RADIUS)

        # Draw border with glow effect when active
        if self.active:
            glow_rect = self.rect.copy()
            glow_rect.inflate_ip(4, 4)
            pygame.draw.rect(surface, (*PRIMARY_COLOR, 100), glow_rect, 4, border_radius=BORDER_RADIUS)

        border_color = PRIMARY_COLOR if self.active else TEXT_COLOR
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=BORDER_RADIUS)

        # Draw placeholder text if empty
        if not self.text and not self.active:
            placeholder_surface = font.render(self.placeholder_text, True, (150, 150, 150))
            surface.blit(placeholder_surface, (self.rect.x + PADDING, self.rect.y + PADDING))

        # Draw text and selection with improved styling
        y = self.rect.y + PADDING
        current_pos = 0
        for i, line in enumerate(self.lines):
            if self.selection_start is not None and self.selection_end is not None:
                start = min(self.selection_start, self.selection_end)
                end = max(self.selection_start, self.selection_end)
                if start < current_pos + len(line) and end > current_pos:
                    sel_start = max(0, start - current_pos)
                    sel_end = min(len(line), end - current_pos)
                    if sel_start < sel_end:
                        sel_rect = pygame.Rect(
                            self.rect.x + PADDING + font.size(line[:sel_start])[0],
                            y,
                            font.size(line[sel_start:sel_end])[0],
                            LINE_HEIGHT
                        )
                        pygame.draw.rect(surface, (*PRIMARY_COLOR, 50), sel_rect,
                                       border_radius=4)

            text_surface = font.render(line, True, TEXT_COLOR)
            surface.blit(text_surface, (self.rect.x + PADDING, y))
            y += LINE_HEIGHT
            current_pos += len(line)

        # Draw cursor with animation
        if self.active:
            self.cursor_timer = (self.cursor_timer + 1) % (self.cursor_blink_rate * 2)
            if self.cursor_timer < self.cursor_blink_rate:
                cursor_x = self.rect.x + PADDING
                cursor_y = self.rect.y + PADDING
                current_pos = 0
                for line in self.lines:
                    if current_pos + len(line) >= self.cursor_pos:
                        cursor_x += font.size(line[:self.cursor_pos - current_pos])[0]
                        break
                    cursor_y += LINE_HEIGHT
                    current_pos += len(line)
                pygame.draw.line(surface, PRIMARY_COLOR, (cursor_x, cursor_y),
                               (cursor_x, cursor_y + LINE_HEIGHT), 2)

def main():
    # Start with the menu
    menu = StartMenu()
    convince_true = menu.run()

    if convince_true is None:
        return

    clock = pygame.time.Clock()
    ai = AISprite(convince_true)
    player = Player()

    # Create input area with adjusted positioning for new font sizes
    input_box = InputBox(50, WINDOW_HEIGHT - 100, WINDOW_WIDTH - 300, 80)
    send_button = Button(WINDOW_WIDTH - 230, WINDOW_HEIGHT - 100, 180, 80, f"Send {EMOJI_SEND}", PRIMARY_COLOR)
    autoplay_button = Button(WINDOW_WIDTH - 230, WINDOW_HEIGHT - 160, 180, 50, f"Auto {EMOJI_AUTO}", PRIMARY_COLOR)

    game_over = False

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            ai.scenario_area.handle_event(event)
            ai.conversation_area.handle_event(event)

            if autoplay_button.handle_event(event) and not game_over:
                ai.waiting_for_auto_response = True
                ai.last_autoplay_time = current_time

            if send_button.handle_event(event) and not game_over:
                if input_box.text.strip():
                    game_over = ai.get_ai_response(input_box.text)
                    input_box.text = ""
                    input_box.lines = []
                    input_box.selection_start = None
                    input_box.selection_end = None
                    input_box.cursor_pos = 0

            if not ai.waiting_for_auto_response:
                result = input_box.handle_event(event)
                if result is not None and not game_over:
                    game_over = ai.get_ai_response(result)

        if ai.waiting_for_auto_response and not game_over and current_time - ai.last_autoplay_time >= ai.autoplay_delay:
            automated_response = ai.get_automated_response()
            game_over = ai.get_ai_response(automated_response)
            ai.waiting_for_auto_response = False  # Reset after generating one response

        # Draw background with subtle pattern
        screen.fill(BACKGROUND_COLOR)
        for i in range(0, WINDOW_WIDTH, 20):
            for j in range(0, WINDOW_HEIGHT, 20):
                pygame.draw.circle(screen, (240, 242, 245), (i, j), 1)

        # Draw UI elements
        if ai.waiting_for_auto_response:
            pygame.draw.rect(screen, GRAY, input_box.rect)
        input_box.draw(screen)
        send_button.draw(screen)
        autoplay_button.draw(screen)

        player.draw()
        ai.draw()

        # Draw game over state
        if game_over:
            # Create semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill(BACKGROUND_COLOR)
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))

            if (ai.convince_true and ai.conviction >= 100) or (not ai.convince_true and ai.conviction <= 0):
                win_text = font.render("🎉 You convinced the AI! Press R to restart", True, SECONDARY_COLOR)
            else:
                if ai.convince_true:
                    win_text = font.render("❌ Game Over - AI remains unconvinced! Press R to restart", True, ACCENT_COLOR)
                else:
                    win_text = font.render("❌ Game Over - AI still believes it's true! Press R to restart", True, ACCENT_COLOR)

            text_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(win_text, text_rect)

            ai.waiting_for_auto_response = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                ai.reset()
                game_over = False

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()