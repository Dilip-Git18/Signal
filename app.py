from flask import Flask, render_template, jsonify
import sqlite3
import datetime
app = Flask(__name__)

# Function to fetch graph data from ambulance.db
def fetch_graph_data():
    conn = sqlite3.connect('ambulance.db', check_same_thread=False, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("SELECT start_node, end_node, distance FROM distances")
    rows = cursor.fetchall()
    conn.close()

    nodes = set()
    edges = []

    for start, end, distance in rows:
        nodes.add(start)
        nodes.add(end)
        edges.append({'from': start, 'to': end, 'label': str(distance)})

    node_list = [{'id': node, 'label': node} for node in nodes]
    return node_list, edges

@app.route('/')
def index():
    nodes, edges = fetch_graph_data()
    return render_template('index.html', nodes=nodes, edges=edges)

@app.route('/node_info/<node>')
def node_info(node):
    conn = sqlite3.connect('node_metadata.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT phone, capacity, website, specialties, status FROM node_details WHERE node_id = ?", (node,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'phone': row[0],
            'capacity': row[1],
            'website': row[2],
            'specialties': row[3],
            'status': row[4]
        })
    else:
        return jsonify({'error': 'No info found'})

@app.route('/record_click/<node>', methods=['POST'])
def record_click(node):
    try:
        with sqlite3.connect('ambulance.db', check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO node_clicks (node_id, node_label) VALUES (?, ?)", (node, node))
            conn.commit()
        return jsonify({'status': 'success'}), 200
    except sqlite3.OperationalError as e:
        print("error:", e)
        return jsonify({'error': 'Database is locked, try again later'}), 500

@app.route('/record_action/<node>', methods=['POST'])
def record_action(node):
    try:
        with sqlite3.connect('ambulance.db', check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO node_actions (node_id, action_type) VALUES (?, ?)", (node, 'button_click'))
            conn.commit()
        return jsonify({'status': 'success'}), 200
    except sqlite3.OperationalError as e:
        print("error:", e)
        return jsonify({'error': 'Database is locked, try again later'}), 500

if __name__ == '__main__':
    app.run(debug=True)
