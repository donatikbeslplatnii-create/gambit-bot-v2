from flask import Flask, request, jsonify, render_template_string
import sqlite3
import json
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>🎮 Gambit Cabinet</title>
<style>
body { background: #0f0c29; color: white; font-family: Arial; padding: 20px; }
h1 { text-align: center; }
.games { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; }
.game { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; width: 200px; border: 1px solid rgba(255,255,255,0.1); }
.game h3 { color: #f093fb; }
.game p { color: #aaa; font-size: 14px; }
.delete { background: #ff4444; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
.btn { background: #f5576c; color: white; padding: 10px 20px; border-radius: 20px; text-decoration: none; display: inline-block; }
.empty { text-align: center; padding: 50px; color: #666; }
</style>
</head>
<body>
<h1>🎮 Gambit Cabinet</h1>
<div style="text-align:center; margin-bottom:20px;">
    <a href="https://t.me/GambitGame2026_5_bot" target="_blank" class="btn">🤖 Open Bot</a>
</div>
<div class="games">
    {% for game in games %}
    <div class="game">
        <h3>{{ game.name }}</h3>
        <p>{{ game.desc[:50] }}...</p>
        <p>🎯 {{ game.best }}</p>
        <button class="delete" onclick="del('{{ game.name }}')">🗑 Delete</button>
    </div>
    {% endfor %}
</div>
{% if not games %}
<div class="empty"><h2>No games saved</h2><p>Save games from the bot!</p></div>
{% endif %}
<script>
function del(name) {
    if(!confirm('Delete '+name+'?')) return;
    fetch('/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: '{{ user_id }}', game: name})
    }).then(() => location.reload());
}
</script>
</body>
</html>
'''

def get_db():
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"DB Error: {e}")
        return None

@app.route('/')
def index():
    try:
        user_id = request.args.get('user_id', '0')
        if user_id == '0':
            return '<h1>🎮 Gambit Cabinet</h1><p>Open from Telegram bot</p><a href="https://t.me/GambitGame2026_5_bot">Open Bot</a>'
        
        conn = get_db()
        if conn is None:
            return "Database error", 500
            
        c = conn.cursor()
        c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        
        games = json.loads(row[0]) if row and row[0] else []
        return render_template_string(HTML_TEMPLATE, games=games, user_id=user_id)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        user_id = data.get('user_id')
        game_name = data.get('game')
        
        conn = get_db()
        if conn is None:
            return jsonify({"status": "error"}), 500
            
        c = conn.cursor()
        c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        
        if row and row[0]:
            games = json.loads(row[0])
            games = [g for g in games if g['name'] != game_name]
            c.execute("UPDATE users SET games=? WHERE user_id=?", (json.dumps(games), user_id))
            conn.commit()
        
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
