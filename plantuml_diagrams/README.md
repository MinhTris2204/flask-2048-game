# PlantUML Diagrams - Game 2048 Project

This folder contains activity diagrams describing all major functionalities of the Game 2048 project.

## Diagrams Overview

### 00_complete_system.puml
**Complete System Architecture**
- Overall system structure
- Frontend, Backend, External Services
- Database relationships
- Component interactions

### 01_game_basic_flow.puml
**Basic Game Flow**
- User login and game initialization
- Game loop: move, merge, check game over
- Score tracking and saving
- Session management
- UI rendering and animations

### 02_authentication.puml
**Authentication Flow**
- User registration (username/password)
- User login (username/password)
- Google OAuth login
- Session management
- Error handling

### 03_premium_payment.puml
**Premium Payment Flow**
- Premium plan selection
- PayOS payment integration
- Webhook processing
- Return URL handling
- Cancel handling
- Premium activation

### 04_premium_features.puml
**Premium Features Flow**
- Hint feature (suggest best move)
- Shuffle feature (randomize tiles)
- Swap feature (exchange two tiles)
- Premium status validation
- Error handling for non-premium users

### 05_undo_and_leaderboard.puml
**Undo and Leaderboard Flow**
- Undo move functionality
- Leaderboard display (top 20)
- Game history with pagination
- Statistics calculation

### 06_game_logic_core.puml
**Game Logic Core Detail**
- Detailed move processing algorithm
- Grid transformations (transpose, reverse)
- Tile compression and merging
- Game over detection
- Helper functions

## How to Generate Diagrams

### Online Method
1. Visit http://www.plantuml.com/plantuml/uml/
2. Copy the content of any `.puml` file
3. Paste into the online editor
4. Download as PNG, SVG, or other formats

### VS Code Method
1. Install "PlantUML" extension in VS Code
2. Open any `.puml` file
3. Press `Alt+D` or right-click → "Preview PlantUML"
4. Export using the preview panel

### Command Line Method
1. Install PlantUML: https://plantuml.com/download
2. Run: `plantuml plantuml_diagrams/*.puml`
3. Output PNG files will be generated in the same folder

### Docker Method
```bash
docker run -v "$PWD":/work plantuml/plantuml plantuml_diagrams/*.puml
```

## Features Covered

### Core Game Features
- ✅ Grid initialization (4x4)
- ✅ Random tile spawning (2 or 4)
- ✅ Move in 4 directions (up, down, left, right)
- ✅ Tile compression
- ✅ Tile merging
- ✅ Score calculation
- ✅ Moves counting
- ✅ Game over detection
- ✅ Best score tracking (localStorage)
- ✅ Undo move

### User Management
- ✅ Registration
- ✅ Login (username/password)
- ✅ Google OAuth login
- ✅ Session management
- ✅ Logout

### Premium Features
- ✅ Premium plans (daily, monthly, yearly)
- ✅ PayOS payment integration
- ✅ Webhook handling
- ✅ Automatic premium activation
- ✅ Premium expiration checking
- ✅ Hint feature
- ✅ Shuffle feature
- ✅ Swap tiles feature

### Social Features
- ✅ Leaderboard (top 20)
- ✅ Game history
- ✅ Statistics (total games, best score, average, total moves)
- ✅ Score saving to database

## Database Schema

### Users Table
- id (PK)
- username (unique)
- password_hash
- email (nullable, unique)
- google_id (nullable, unique)
- is_premium
- premium_expires_at
- created_at

### Scores Table
- id (PK)
- user_id (FK)
- score
- max_tile
- moves
- created_at

### PremiumPlans Table
- id (PK)
- name
- duration_days
- price
- description
- is_active

### Orders Table
- id (PK)
- user_id (FK)
- plan_id (FK, nullable)
- amount
- status
- payment_method
- transaction_id (unique)
- created_at
- completed_at

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (via SQLAlchemy ORM)
- **Authentication**: Flask-Login, Google OAuth
- **Payment**: PayOS integration
- **Session**: Flask sessions
- **Styling**: Custom CSS with gradients

## Important Notes

1. **Session Management**: Game state is stored in Flask sessions using Python pickle
2. **Premium Check**: Premium status is checked before each premium feature access
3. **Best Score**: Stored in browser localStorage, not in database
4. **Grid State**: Stored in session as serialized Game2048 object
5. **Payment Flow**: Uses both return URL and webhook for reliability
6. **Google OAuth**: Requires proper domain configuration for redirect URIs

## Future Enhancements (Not in Current Diagrams)

- Multiplayer mode
- Custom themes
- Daily challenges
- Achievements system
- Social sharing
- Mobile app version
- Tournament mode

