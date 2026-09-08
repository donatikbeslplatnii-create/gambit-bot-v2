from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'gambit-super-secret-key-2026'

# HTML ШАБЛОН (СУПЕР КРАСИВЫЙ САЙТ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Gambit Cabinet</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 40px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        h1 {
            font-size: 3em;
            background: linear-gradient(45deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 40px rgba(245,87,108,0.3);
        }
        .subtitle {
            color: #aaa;
            margin-top: 10px;
            font-size: 1.1em;
        }
        .user-info {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            margin-bottom: 25px;
        }
        .user-info strong {
            color: #f093fb;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            padding: 15px 25px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #f093fb;
        }
        .stat-card .label {
            color: #888;
            font-size: 0.9em;
        }
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        .controls input {
            padding: 12px 20px;
            border-radius: 30px;
            border: none;
            background: rgba(255,255,255,0.1);
            color: white;
            width: 250px;
            outline: none;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .controls input::placeholder {
            color: #666;
        }
        .controls input:focus {
            border-color: #f5576c;
        }
        .btn {
            padding: 12px 25px;
            border-radius: 30px;
            border: none;
            background: linear-gradient(45deg, #f093fb, #f5576c);
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(245,87,108,0.3);
        }
        .btn-danger {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        }
        .btn-danger:hover {
            box-shadow: 0 10px 30px rgba(238,90,36,0.3);
        }
        .btn-outline {
            background: transparent;
            border: 2px solid #f5576c;
        }
        .btn-outline:hover {
            background: #f5576c;
        }
        .game-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .game-card {
            background: rgba(255,255,255,0.06);
            border-radius: 15px;
            padding: 20px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.05);
            position: relative;
        }
        .game-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.1);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        .game-card .category {
            display: inline-block;
            background: rgba(245,87,108,0.3);
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            color: #f093fb;
            margin-bottom: 10px;
        }
        .game-card h3 {
            color: white;
            font-size: 1.3em;
            margin-bottom: 8px;
        }
        .game-card .desc {
            color: #aaa;
            font-size: 0.9em;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        .game-card .tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 10px 0;
        }
        .game-card .tag {
            background: rgba(255,255,255,0.05);
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            color: #888;
        }
        .game-card .delete-btn {
            background: #ff4444;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9em;
            margin-top: 10px;
            width: 100%;
        }
        .game-card .delete-btn:hover {
            background: #cc0000;
            transform: scale(1.02);
        }
        .empty {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .empty h2 {
            font-size: 2em;
            margin-bottom: 15px;
            color: #444;
        }
        .empty .emoji {
            font-size: 4em;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #444;
            font-size: 0.9em;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            display: none;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { transform: translateX(100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @media (max-width: 600px) {
            h1 { font-size: 2em; }
            .game-grid { grid-template-columns: 1fr; }
            .controls input { width: 100%; }
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Gambit Cabinet</h1>
            <div class="subtitle">Your personal game collection</div>
        </div>

        <div class="user-info">
            <strong>👤 User ID:</strong> <span id="userId">{{ user_id }}</span>
            <span style="margin: 0 10px;">|</span>
            <strong>👤 Username:</strong> <span id="username">{{ username or 'Unknown' }}</span>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number" id="gameCount">{{ games|length }}</div>
                <div class="label">🎮 Saved Games</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ categories|length }}</div>
                <div class="label">📂 Categories</div>
            </div>
            <div class="stat-card">
                <div class="number">🔥</div>
                <div class="label">Your Collection</div>
            </div>
        </div>

        <div class="controls">
            <input type="text" id="searchInput" placeholder="🔍 Search games..." onkeyup="filterGames()">
            <button class="btn btn-outline" onclick="window.location.href='/'">🔄 Refresh</button>
            <button class="btn btn-danger" onclick="clearAll()">🗑️ Clear All</button>
        </div>

        <div class="game-grid" id="gameGrid">
            {% if games %}
                {% for game in games %}
                <div class="game-card" data-name="{{ game.name.lower() }}" data-category="{{ game.category or 'unknown' }}">
                    <div class="category">{{ game.category or 'Unknown' }}</div>
                    <h3>{{ game.name }}</h3>
                    <div class="desc">{{ game.desc }}</div>
                    <div class="tags">
                        <span class="tag">🎯 {{ game.best or 'N/A' }}</span>
                        <span class="tag">✨ {{ game.vibe or 'N/A' }}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteGame('{{ game.name }}')">🗑️ Delete</button>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">
                    <div class="emoji">🎮</div>
                    <h2>No games saved yet</h2>
                    <p>Go to Telegram bot and save some games!</p>
                    <br>
                    <a href="https://t.me/GambitGame2026_4_bot" target="_blank" class="btn">🤖 Open Bot</a>
                </div>
            {% endif %}
        </div>

        <div class="footer">
            Made with ❤️ by Gambit • Powered by GOD IS BOT
        </div>
    </div>

    <div id="toast" class="toast"></div>

    <script>
        function filterGames() {
            const input = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.game-card');
            cards.forEach(card => {
                const name = card.getAttribute('data-name');
                const category = card.getAttribute('data-category');
                if (name.includes(input) || category.includes(input)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function deleteGame(gameName) {
            if (!confirm(`Delete "${gameName}" from your cabinet?`)) return;
            
            const userId = document.getElementById('userId').textContent.trim();
            
            fetch('/delete_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    game_name: gameName
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(`✅ Removed ${gameName}`);
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showToast('❌ Error removing game');
                }
            })
            .catch(error => {
                showToast('❌ Error: ' + error);
            });
        }

        function clearAll() {
            if (!confirm('🗑️ Delete ALL games from your cabinet?')) return;
            
            const userId = document.getElementById('userId').textContent.trim();
            
            fetch('/clear_all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('🗑️ All games cleared');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showToast('❌ Error clearing games');
                }
            })
            .catch(error => {
                showToast('❌ Error: ' + error);
            });
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }
    </script>
</body>
</html>
"""

def get_db_connection():
    conn = sqlite3.connect('gambit_users.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_games(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT saved_games FROM users WHERE user_id=?", (str(user_id),))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        try:
            games = json.loads(result[0])
            return games
        except:
            return []
    return []

def save_user_games(user_id, games):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET saved_games=? WHERE user_id=?", (json.dumps(games), str(user_id)))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    user_id = request.args.get('user_id', '0')
    username = request.args.get('username', 'Unknown')
    
    if user_id == '0':
        return '''
        <html>
        <body style="background: #0f0c29; color: white; font-family: Arial; text-align: center; padding: 50px;">
            <h1>🎮 Gambit Cabinet</h1>
            <p>Please open this page from the Telegram bot:</p>
            <br>
            <a href="https://t.me/GambitGame2026_4_bot" target="_blank" style="background: #f5576c; color: white; padding: 15px 30px; border-radius: 30px; text-decoration: none; display: inline-block;">
                🤖 Open Bot
            </a>
        </body>
        </html>
        '''
    
    games = get_user_games(user_id)
    
    # Получаем категории из игр
    categories = set()
    for game in games:
        if 'category' in game:
            categories.add(game['category'])
    
    return render_template_string(
        HTML_TEMPLATE, 
        user_id=user_id,
        username=username,
        games=games,
        categories=list(categories)
    )

@app.route('/delete_game', methods=['POST'])
def delete_game():
    data = request.json
    user_id = data.get('user_id')
    game_name = data.get('game_name')
    
    games = get_user_games(user_id)
    games = [g for g in games if g['name'] != game_name]
    save_user_games(user_id, games)
    
    return jsonify({'success': True})

@app.route('/clear_all', methods=['POST'])
def clear_all():
    data = request.json
    user_id = data.get('user_id')
    
    save_user_games(user_id, [])
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
