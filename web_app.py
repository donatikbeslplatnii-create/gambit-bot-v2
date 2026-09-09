from flask import Flask, request, jsonify, render_template_string
import sqlite3
import json
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👑 GOD GAMBIT — Cabinet</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #0a0a0f;
            min-height: 100vh;
            color: #fff;
            padding: 20px;
            background-image: 
                radial-gradient(ellipse at 20% 50%, rgba(72, 0, 255, 0.1) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 50%, rgba(255, 0, 150, 0.1) 0%, transparent 60%),
                linear-gradient(180deg, #0a0a0f 0%, #1a0a2e 100%);
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 40px 20px 30px;
            margin-bottom: 30px;
            position: relative;
        }
        .header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 2px;
            background: linear-gradient(90deg, transparent, #f5576c, #f093fb, transparent);
        }
        h1 {
            font-size: 3.5em;
            font-weight: 900;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #ff6b6b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 60px rgba(245, 87, 108, 0.3);
            letter-spacing: 2px;
        }
        .subtitle {
            color: #888;
            font-size: 1.1em;
            margin-top: 10px;
            letter-spacing: 3px;
        }
        .user-info {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
            padding: 18px 30px;
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.06);
            backdrop-filter: blur(10px);
        }
        .user-info span {
            color: #aaa;
        }
        .user-info strong {
            color: #f093fb;
            font-weight: 600;
        }
        .user-info .badge {
            background: linear-gradient(135deg, #f5576c, #f093fb);
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
            margin: 30px 0;
        }
        .stat-card {
            text-align: center;
            padding: 15px 30px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            min-width: 120px;
        }
        .stat-card .number {
            font-size: 2.2em;
            font-weight: 800;
            background: linear-gradient(135deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-card .label {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
            margin: 30px 0 40px;
        }
        .controls input {
            padding: 14px 25px;
            border-radius: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05);
            color: white;
            font-size: 1em;
            width: 300px;
            outline: none;
            transition: all 0.3s ease;
        }
        .controls input::placeholder {
            color: #555;
        }
        .controls input:focus {
            border-color: #f5576c;
            box-shadow: 0 0 30px rgba(245, 87, 108, 0.1);
        }
        .btn {
            padding: 14px 30px;
            border-radius: 30px;
            border: none;
            font-weight: 700;
            font-size: 0.95em;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(245, 87, 108, 0.3);
        }
        .btn-danger {
            background: rgba(255, 0, 0, 0.2);
            color: #ff6b6b;
            border: 1px solid rgba(255, 0, 0, 0.2);
        }
        .btn-danger:hover {
            background: rgba(255, 0, 0, 0.3);
        }
        .btn-outline {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.15);
            color: #aaa;
        }
        .btn-outline:hover {
            border-color: #f5576c;
            color: white;
        }
        .game-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .game-card {
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.06);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        .game-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #f093fb, #f5576c);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .game-card:hover {
            transform: translateY(-8px);
            background: rgba(255,255,255,0.06);
            border-color: rgba(245, 87, 108, 0.3);
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        }
        .game-card:hover::before {
            opacity: 1;
        }
        .game-card .category {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.7em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: rgba(245, 87, 108, 0.15);
            color: #f093fb;
            margin-bottom: 12px;
        }
        .game-card h3 {
            font-size: 1.3em;
            font-weight: 700;
            margin-bottom: 8px;
            color: #fff;
        }
        .game-card .desc {
            color: #888;
            font-size: 0.9em;
            line-height: 1.5;
            margin-bottom: 12px;
        }
        .game-card .tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }
        .game-card .tag {
            padding: 3px 12px;
            border-radius: 12px;
            font-size: 0.75em;
            background: rgba(255,255,255,0.05);
            color: #666;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .game-card .delete-btn {
            padding: 8px 20px;
            border-radius: 10px;
            border: none;
            background: rgba(255, 0, 0, 0.1);
            color: #ff6b6b;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            font-size: 0.9em;
        }
        .game-card .delete-btn:hover {
            background: rgba(255, 0, 0, 0.25);
        }
        .empty {
            text-align: center;
            padding: 80px 20px;
            color: #444;
        }
        .empty .emoji {
            font-size: 4em;
            margin-bottom: 20px;
            display: block;
        }
        .empty h2 {
            font-size: 1.8em;
            margin-bottom: 10px;
            color: #666;
        }
        .empty p {
            color: #444;
            font-size: 1.1em;
        }
        .footer {
            text-align: center;
            padding: 40px 20px 20px;
            color: #333;
            font-size: 0.9em;
            border-top: 1px solid rgba(255,255,255,0.03);
            margin-top: 40px;
        }
        .footer a {
            color: #f5576c;
            text-decoration: none;
        }
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 16px 28px;
            border-radius: 12px;
            background: rgba(0,0,0,0.9);
            color: white;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            display: none;
            z-index: 1000;
            font-weight: 500;
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
            .stats { gap: 20px; }
        }
        .loading {
            text-align: center;
            padding: 60px;
            color: #444;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👑 GOD GAMBIT</h1>
            <div class="subtitle">✦ YOUR GAME CABINET ✦</div>
        </div>

        <div class="user-info">
            <span>👤 <strong>{{ user_id }}</strong></span>
            <span>|</span>
            <span>📛 <strong>{{ username or 'Unknown' }}</strong></span>
            <span class="badge">🔥 VIP</span>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{{ games|length }}</div>
                <div class="label">🎮 Games</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ categories|length }}</div>
                <div class="label">📂 Genres</div>
            </div>
            <div class="stat-card">
                <div class="number">🏆</div>
                <div class="label">Collection</div>
            </div>
        </div>

        <div class="controls">
            <input type="text" id="searchInput" placeholder="🔍 Search games..." onkeyup="filterGames()">
            <button class="btn btn-primary" onclick="window.location.reload()">🔄 Refresh</button>
            <button class="btn btn-danger" onclick="clearAll()">🗑️ Clear All</button>
        </div>

        <div class="game-grid" id="gameGrid">
            {% if games %}
                {% for game in games %}
                <div class="game-card" data-name="{{ game.name.lower() }}">
                    <div class="category">{{ game.category or 'Unknown' }}</div>
                    <h3>{{ game.name }}</h3>
                    <div class="desc">{{ game.desc[:100] }}{% if game.desc|length > 100 %}...{% endif %}</div>
                    <div class="tags">
                        <span class="tag">🎯 {{ game.best or 'N/A' }}</span>
                        <span class="tag">✨ {{ game.vibe or 'N/A' }}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteGame('{{ game.name }}')">🗑️ Remove</button>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">
                    <span class="emoji">🎮</span>
                    <h2>Your cabinet is empty</h2>
                    <p>Save games from the bot and they'll appear here!</p>
                    <br>
                    <a href="https://t.me/GambitGame2026_5_bot" target="_blank" class="btn btn-primary">🤖 Open Bot</a>
                </div>
            {% endif %}
        </div>

        <div class="footer">
            Made with ❤️ · <a href="https://t.me/GambitGame2026_5_bot" target="_blank">@GambitGame2026_5_bot</a> · Powered by GOD IS BOT
        </div>
    </div>

    <div id="toast" class="toast"></div>

    <script>
        function filterGames() {
            const input = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.game-card');
            cards.forEach(card => {
                const name = card.getAttribute('data-name');
                card.style.display = name.includes(input) ? 'block' : 'none';
            });
        }

        function deleteGame(name) {
            if (!confirm('🗑️ Delete "' + name + '" from your cabinet?')) return;
            const userId = '{{ user_id }}';
            fetch('/delete_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, game_name: name })
            })
            .then(r => r.json())
            .then(d => {
                if (d.success) {
                    showToast('✅ Removed ' + name);
                    setTimeout(() => location.reload(), 800);
                }
            })
            .catch(e => showToast('❌ Error: ' + e));
        }

        function clearAll() {
            if (!confirm('🗑️ Delete ALL games from your cabinet?')) return;
            const userId = '{{ user_id }}';
            fetch('/clear_all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            })
            .then(r => r.json())
            .then(d => {
                if (d.success) {
                    showToast('🗑️ All games cleared');
                    setTimeout(() => location.reload(), 800);
                }
            })
            .catch(e => showToast('❌ Error: ' + e));
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }
    </script>
</body>
</html>
'''

def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    user_id = request.args.get('user_id', '0')
    username = request.args.get('username', 'Unknown')
    
    if user_id == '0':
        return '''
        <html>
        <body style="background: #0a0a0f; color: white; font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="font-size: 3em; background: linear-gradient(135deg, #f093fb, #f5576c); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">👑 GOD GAMBIT</h1>
            <p style="color: #888;">Open this page from the Telegram bot</p>
            <br>
            <a href="https://t.me/GambitGame2026_5_bot" target="_blank" style="background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 15px 40px; border-radius: 30px; text-decoration: none; display: inline-block; font-weight: bold;">🤖 Open Bot</a>
        </body>
        </html>
        '''
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    games = json.loads(row[0]) if row and row[0] else []
    
    categories = set()
    for game in games:
        if 'category' in game:
            categories.add(game['category'])
    
    return render_template_string(HTML_TEMPLATE, user_id=user_id, username=username, games=games, categories=list(categories))

@app.route('/delete_game', methods=['POST'])
def delete_game():
    data = request.json
    user_id = data.get('user_id')
    game_name = data.get('game_name')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    
    if row and row[0]:
        games = json.loads(row[0])
        games = [g for g in games if g['name'] != game_name]
        c.execute("UPDATE users SET games=? WHERE user_id=?", (json.dumps(games), user_id))
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/clear_all', methods=['POST'])
def clear_all():
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET games='[]' WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
