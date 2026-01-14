

"""
Climate Data API Lab - Learn Python, Flask, and REST APIs

This lab teaches:
1. Data processing with Pandas
2. Building REST APIs with Flask
3. JSON handling and serialization
4. Error handling and validation
"""

from flask import Flask, jsonify, render_template, request
import pandas as pd
from datetime import datetime
import sqlite3
import os

# Initialize Flask with correct paths (since we're in src/ directory)
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# Load climate data
df = pd.read_csv('data/climate_data.csv')

# --- 数据库配置 ---
DATABASE_PATH = 'data/climate.db'

def get_db_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 允许通过列名访问
    return conn

def init_database():
    """初始化数据库表结构"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建用户发布信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            contact TEXT,
            source TEXT DEFAULT '用户发布',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

# 初始化数据库（应用启动时）
init_database()

def get_services():
    """Load and process services from CSV with better data structure"""
    df = pd.read_csv('data/bayarea_services.csv')
    services = []

    for _, row in df.iterrows():
        title = row['Title']
        source = row['Source']

        # Extract category from title (most titles start with category info)
        if '(' in title or '·' in title or '｜' in title:
            parts = title.split('(')[0].split('·')[0].split('｜')[0]
            category = parts.strip() if parts else "其他"
            description = title
        else:
            category = "生活服务"
            description = title

        services.append({
            'Category': category,
            'Title': title,
            'Description': description[:100] + '...' if len(description) > 100 else description,
            'Contact': source,
            'Source': source
        })

    return services

def get_user_posts_from_db():
    """从数据库获取用户发布的信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, title, description, contact, source, created_at
            FROM user_posts
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        posts = []
        for row in rows:
            posts.append({
                'Category': row['category'],
                'Title': row['title'],
                'Description': row['description'] if row['description'] else row['title'],
                'Contact': row['contact'] if row['contact'] else '未提供',
                'Source': row['source']
            })
        return posts
    except Exception as e:
        print(f"Error fetching user posts: {e}")
        return []

def get_all_services():
    """Get both scraped and user-submitted services"""
    services = get_services()
    # Add user-submitted posts from database
    user_posts = get_user_posts_from_db()
    services.extend(user_posts)
    return services

def get_categories(services):
    """Extract unique categories from services"""
    categories = set()
    for service in services:
        categories.add(service['Category'])
    return sorted(list(categories))

# --- 关键部分：首页路由 ---
@app.route('/')
def index():
    # Get query parameters
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20

    # Get all services
    services = get_all_services()

    # Apply filters
    if search_query:
        services = [s for s in services if search_query.lower() in s['Title'].lower()
                   or search_query.lower() in s['Description'].lower()]

    if category_filter:
        services = [s for s in services if s['Category'] == category_filter]

    # Pagination
    total_services = len(services)
    total_pages = (total_services + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_services = services[start_idx:end_idx]

    # Get categories for filter dropdown
    all_categories = get_categories(get_all_services())

    return render_template('bayarea.html',
                         services=paginated_services,
                         categories=all_categories,
                         search_query=search_query,
                         category_filter=category_filter,
                         page=page,
                         total_pages=total_pages,
                         total_services=total_services)

# --- 数据库管理 API ---
@app.route('/api/user-posts', methods=['GET'])
def get_user_posts_api():
    """API endpoint to retrieve all user posts from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, category, title, description, contact, source, created_at
            FROM user_posts
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        posts = []
        for row in rows:
            posts.append({
                'id': row['id'],
                'category': row['category'],
                'title': row['title'],
                'description': row['description'],
                'contact': row['contact'],
                'source': row['source'],
                'created_at': row['created_at']
            })

        return jsonify({
            'total': len(posts),
            'posts': posts
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-posts/<int:post_id>', methods=['DELETE'])
def delete_user_post(post_id):
    """Delete a user post by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_posts WHERE id = ?', (post_id,))
        conn.commit()
        rows_deleted = cursor.rowcount
        conn.close()

        if rows_deleted == 0:
            return jsonify({'error': 'Post not found'}), 404

        return jsonify({'message': f'Post {post_id} deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database-stats', methods=['GET'])
def database_stats():
    """Get statistics about the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count total posts
        cursor.execute('SELECT COUNT(*) as count FROM user_posts')
        total_posts = cursor.fetchone()['count']

        # Count by category
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM user_posts
            GROUP BY category
            ORDER BY count DESC
        ''')
        categories = [{'category': row['category'], 'count': row['count']}
                     for row in cursor.fetchall()]

        # Get most recent post
        cursor.execute('''
            SELECT title, created_at
            FROM user_posts
            ORDER BY created_at DESC
            LIMIT 1
        ''')
        recent = cursor.fetchone()

        conn.close()

        return jsonify({
            'total_user_posts': total_posts,
            'categories': categories,
            'most_recent_post': {
                'title': recent['title'] if recent else None,
                'created_at': recent['created_at'] if recent else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- 新增：处理用户发布信息 ---
@app.route('/post', methods=['POST'])
def post_service():
    """Handle new service posting from users - saves to database"""
    try:
        category = request.form.get('category', '其他').strip()
        title = request.form.get('title', '').strip()
        contact = request.form.get('contact', '').strip()
        description = request.form.get('desc', '').strip()

        # Validation
        if not title:
            return render_template('bayarea.html',
                                 services=get_all_services()[:20],
                                 categories=get_categories(get_all_services()),
                                 error="标题不能为空",
                                 page=1,
                                 total_pages=(len(get_all_services()) + 19) // 20,
                                 total_services=len(get_all_services()))

        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_posts (category, title, description, contact, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (category, title, description, contact if contact else '未提供', '用户发布'))
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()

        print(f"✓ New post created with ID: {post_id}")

        # Redirect to home page with success message
        all_services = get_all_services()
        return render_template('bayarea.html',
                             services=all_services[:20],
                             categories=get_categories(all_services),
                             success="信息发布成功！已保存到数据库",
                             page=1,
                             total_pages=(len(all_services) + 19) // 20,
                             total_services=len(all_services))

    except Exception as e:
        print(f"Error posting service: {e}")
        all_services = get_all_services()
        return render_template('bayarea.html',
                             services=all_services[:20],
                             categories=get_categories(all_services),
                             error=f"发布失败: {str(e)}",
                             page=1,
                             total_pages=(len(all_services) + 19) // 20,
                             total_services=len(all_services))

# ============================================================================
# EXERCISE 1: GET endpoint - Retrieve all climate records
# ============================================================================
@app.route('/api/climate', methods=['GET'])
def get_all_climate():
    """
    TODO: Implement this endpoint
    - Return all climate records as JSON
    - Hint: Use df.to_dict('records')
    """
    records = df.to_dict('records')
    return jsonify(records), 200


# ============================================================================
# EXERCISE 2: GET endpoint with ID - Retrieve specific year
# ============================================================================
@app.route('/api/climate/<int:year>', methods=['GET'])
def get_climate_by_year(year):
    """
    TODO: Implement this endpoint
    - Find record matching the given year
    - Return 404 if year not found
    - Hint: Use df[df['Year'] == year]
    """
    record = df[df['Year'] == year]
    if record.empty:
        return jsonify({'error': 'Year not found'}), 404
    return jsonify(record.iloc[0].to_dict()), 200


# ============================================================================
# EXERCISE 3: POST endpoint - Add new climate record
# ============================================================================
@app.route('/api/climate', methods=['POST'])
def add_climate_record():
    """
    TODO: Implement this endpoint
    - Accept JSON: {"year": 2024, "avg_temp": 15.2}
    - Validate year is not duplicate
    - Add to DataFrame and CSV
    - Return 201 Created with new record
    - Hint: Use df.loc[] to append and df.to_csv()
    """
    global df
    try:
        data = request.get_json()

        # Validate input
        if not data or 'Year' not in data or 'Avg_Temp' not in data:
            return jsonify({'error': 'Missing Year or Avg_Temp'}), 400

        year = data['Year']

        # Check for duplicates
        if not df[df['Year'] == year].empty:
            return jsonify({'error': f'Year {year} already exists'}), 409

        # Add record
        new_record = pd.DataFrame([{'Year': year, 'Avg_Temp': data['Avg_Temp']}])
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv('data/climate_data.csv', index=False)
        
        return jsonify({'message': 'Record added', 'record': new_record.iloc[0].to_dict()}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# EXERCISE 4: Statistics endpoint - Compute analytics
# ============================================================================
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    TODO: Implement this endpoint
    - Return: mean, min, max, std of Avg_Temp
    - Hint: Use df['Avg_Temp'].mean(), .min(), .max(), .std()
    """
    stats = {
        'mean': float(df['Avg_Temp'].mean()),
        'min': float(df['Avg_Temp'].min()),
        'max': float(df['Avg_Temp'].max()),
        'std': float(df['Avg_Temp'].std()),
        'count': len(df)
    }
    return jsonify(stats), 200


# ============================================================================
# EXERCISE 5: Temperature range query
# ============================================================================
@app.route('/api/climate/range', methods=['GET'])
def get_temperature_range():
    """
    TODO: Implement this endpoint
    - Query params: ?min_temp=14&max_temp=15
    - Return records within temperature range
    - Hint: Use df[(df['Avg_Temp'] >= min_temp) & (df['Avg_Temp'] <= max_temp)]
    """
    try:
        min_temp = float(request.args.get('min_temp', 0))
        max_temp = float(request.args.get('max_temp', 100))
        
        filtered = df[(df['Avg_Temp'] >= min_temp) & (df['Avg_Temp'] <= max_temp)]
        return jsonify(filtered.to_dict('records')), 200
    
    except ValueError:
        return jsonify({'error': 'Invalid temperature values'}), 400


# ============================================================================
# Health check endpoint
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'API is running', 'timestamp': datetime.now().isoformat()}), 200


# @app.route('/')
# def index():
#    records = df.to_dict('records')
#    return render_template('index.html', data=records)


if __name__ == '__main__':
    print("🌍 Climate Data API & Bay Area Services starting on http://localhost:5000")
    print("\n📱 Web Interface:")
    print("   GET  /                         - Bay Area Services (主页)")
    print("   POST /post                     - Submit new service")
    print("\n📚 Climate API Endpoints:")
    print("   GET  /api/climate              - All climate records")
    print("   GET  /api/climate/<year>       - Record by year")
    print("   POST /api/climate              - Add new record")
    print("   GET  /api/statistics           - Temperature stats")
    print("   GET  /api/climate/range        - Filter by range")
    print("   GET  /api/health               - Health check")
    print("\n💾 Database API Endpoints:")
    print("   GET  /api/user-posts           - All user posts from database")
    print("   GET  /api/database-stats       - Database statistics")
    print("   DEL  /api/user-posts/<id>      - Delete user post by ID")
    app.run(debug=True, port=5000, host='0.0.0.0')
    
