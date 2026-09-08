from flask import Flask, render_template_string, request, jsonify
import sqlite3
import json
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🎮 Gambit Cabinet</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { 
            background: linear-gradient(135deg, #0f0c29, #302b63);
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5em; margin: 20px 0; }
        h1 span { background: linear-gradient(45deg, #f093fb, #f5576c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .game-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
        .game-item {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .game-item h3 { color: #f093fb; margin: 0 0 10px 0; }
        .game-item p { color: #aaa; font-size: 0.9em; margin: 5px 0; }
        .delete-btn {
            background: #ff4444;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }
        .delete-btn:hover { background: #cc0000; }
        .empty { text-align: center; padding: 50px; color: #666; }
        .stats { text-align: center; font-size: 1.2em; margin: 20px 0; }
        .stats span { color: #f093fb; font-weight: bold; }
        .btn {
            background: linear-gradient(45deg, #f093fb, #f5576c);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }
        .btn:hover { transform: scale(1.05); }
        .user-info { text-align: center; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px; margin-bottom: 20px; }
        .clear-btn { background: #ff6b6b; }
        .clear-btn:hover { background: #ee5a24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 <span>Gambit Cabinet</span></h1>
        
        <div class="user-info">
            👤 User ID: <strong>{{ user_id }}</strong> | 
            👤 Username: <strong>{{ username or 'Unknown' }}</strong>
        </div>

        <div class="stats">
            📊 Total games: <span>{{ games|length }}</span>
        </div>

        <div style="text-align: center; margin: 20px 0;">
            <button class="btn clear-btn" onclick="clearAll()">🗑️ Clear All</button>
            <a href="https://t.me/GambitGame2026_4_bot" target="_blank" class="btn">🤖 Open Bot</a>
        </div>

        <div class="game-grid">
            {% if games %}
                {% for game in games %}
                <div class="game-item">
                    <h3>{{ game.name }}</h3>
                    <p>{{ game.desc[:100] }}{% if game.desc|length > 100 %}...{% endif %}</p>
                    <p>🎯 {{ game.best or 'N/A' }}</p>
                    <p>✨ {{ game.vibe or 'N/A' }}</p>
                    <button class="delete-btn" onclick="deleteGame('{{ game.name }}')">🗑️ Delete</button>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">
                    <h2>No games saved yet</h2>
                    <p>Go to Telegram bot and save some games!</p>
                    <br>
                    <a href="https://t.me/GambitGame2026_4_bot" target="_blank" class="btn">🤖 Open Bot</a>
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        function deleteGame(name) {
            if (!confirm('Delete "' + name + '"?')) return;
            const userId = '{{ user_id }}';
            fetch('/delete_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, game_name: name })
            })
            .then(r => r.json())
            .then(d => { if(d.success) location.reload(); })
            .catch(e => alert('Error: ' + e));
        }

        function clearAll() {
            if (!confirm('Delete ALL games?')) return;
            const userId = '{{ user_id }}';
            fetch('/clear_all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            })
            .then(r => r.json())
            .then(d => { if(d.success) location.reload(); })
            .catch(e => alert('Error: ' + e));
        }
    </script>
</body>
</html>
"""

def get_db():
    conn = sqlite3.connect('gambit_users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    user_id = request.args.get('user_id', '0')
    username = request.args.get('username', 'Unknown')
    
    if user_id == '0':
        return '<h1>🎮 Gambit Cabinet</h1><p>Open this page from Telegram bot!</p><a href="https://t.me/GambitGame2026_4_bot">Open Bot</a>'
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT saved_games FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    
    games = json.loads(result[0]) if result and result[0] else []
    
    return render_template_string(HTML, user_id=user_id, username=username, games=games)

@app.route('/delete_game', methods=['POST'])
def delete_game():
    data = request.json
    user_id = data.get('user_id')
    game_name = data.get('game_name')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT saved_games FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    
    if result and result[0]:
        games = json.loads(result[0])
        games = [g for g in games if g['name'] != game_name]
        c.execute("UPDATE users SET saved_games=? WHERE user_id=?", (json.dumps(games), user_id))
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/clear_all', methods=['POST'])
def clear_all():
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET saved_games='[]' WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
