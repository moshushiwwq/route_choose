from flask import Flask, render_template, request, jsonify
import heapq

app = Flask(__name__)

def dijkstra(nodes, edges, start_id, end_id):
    """
    标准 Dijkstra 算法，使用加权距离 (edge.weight * edge.factor)
    返回路径和加权总长度
    """
    graph = {node['id']: {} for node in nodes}
    for edge in edges:
        u, v = edge['from'], edge['to']
        # 加权权重
        w = edge['weight'] * edge.get('factor', 1.0)
        graph[u][v] = w
        graph[v][u] = w

    dist = {node['id']: float('inf') for node in nodes}
    prev = {node['id']: None for node in nodes}
    dist[start_id] = 0
    pq = [(0, start_id)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == end_id:
            break
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    path = []
    node = end_id
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    if path[0] != start_id:
        return None
    return path, dist[end_id]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/multi-path', methods=['POST'])
def multi_path():
    """多起点到多终点，返回所有组合的最短路径（加权距离）"""
    data = request.get_json()
    nodes = data['nodes']
    edges = data['edges']
    start_ids = data['startIds']
    end_ids = data['endIds']

    results = []
    for s in start_ids:
        for e in end_ids:
            if s == e:
                continue
            res = dijkstra(nodes, edges, s, e)
            if res:
                path, length = res
                results.append({
                    'start': s,
                    'end': e,
                    'path': path,
                    'length': length
                })
    # 按加权长度排序
    results.sort(key=lambda x: x['length'])
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)