"""
Data Service - Container Component
Handles storage and retrieval of submission records using SQLite.
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = Path(os.getenv("DATABASE_PATH", "/data/submissions.db"))
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 5002))


def get_connection():
    """Get a database connection with row factory for dict-like access."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Initialize the database schema."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                poster_filename TEXT,
                status TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        connection.commit()


def generate_id():
    """Generate a unique submission ID."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"SUB-{timestamp}"


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'data_service',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/records', methods=['POST'])
def create_record():
    """
    Create a new submission record.
    Called by Workflow Service after user submits the form.
    """
    data = request.get_json(force=True)

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    submission_id = data.get('id', generate_id())
    now = datetime.now().isoformat()

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO submissions (id, title, description, poster_filename, status, note, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    submission_id,
                    data.get('title', ''),
                    data.get('description', ''),
                    data.get('poster_filename', ''),
                    data.get('status', 'PENDING'),
                    data.get('note', ''),
                    now,
                    now
                )
            )
            connection.commit()

        record = {
            'id': submission_id,
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'poster_filename': data.get('poster_filename', ''),
            'status': data.get('status', 'PENDING'),
            'note': data.get('note', ''),
            'created_at': now,
            'updated_at': now
        }
        print(f"[Data Service] Created record: {submission_id}")

        return jsonify(record), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'Submission ID already exists'}), 409


@app.route('/records/<record_id>', methods=['GET'])
def get_record(record_id):
    """
    Retrieve a submission record by ID.
    Called by Presentation Service to display results to user.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, description, poster_filename, status, note, created_at, updated_at
            FROM submissions
            WHERE id = ?
            """,
            (record_id,)
        ).fetchone()

    if row is None:
        return jsonify({'error': 'submission not found'}), 404

    return jsonify(dict(row))


@app.route('/records/<record_id>', methods=['PUT'])
def update_record(record_id):
    """
    Update a submission record.
    Called by Result Update Function after processing.
    """
    data = request.get_json(force=True)

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    with get_connection() as connection:
        current = connection.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (record_id,)
        ).fetchone()

        if current is None:
            return jsonify({'error': 'submission not found'}), 404

        # Update fields
        updated = {
            'title': data.get('title', current['title']),
            'description': data.get('description', current['description']),
            'poster_filename': data.get('poster_filename', current['poster_filename']),
            'status': data.get('status', current['status']),
            'note': data.get('note', current['note']),
        }
        updated['updated_at'] = datetime.now().isoformat()

        connection.execute(
            """
            UPDATE submissions
            SET title = ?, description = ?, poster_filename = ?, status = ?, note = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                updated['title'],
                updated['description'],
                updated['poster_filename'],
                updated['status'],
                updated['note'],
                updated['updated_at'],
                record_id
            )
        )
        connection.commit()

    print(f"[Data Service] Updated record: {record_id} -> {updated['status']}")
    return jsonify({'id': record_id, **updated})


# Backward compatibility aliases
@app.route('/submissions', methods=['POST'])
def create_submission():
    return create_record()


@app.route('/submissions/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    return get_record(submission_id)


@app.route('/submissions/<submission_id>', methods=['PUT'])
def update_submission(submission_id):
    return update_record(submission_id)


@app.route('/submissions', methods=['GET'])
def list_submissions():
    """List all submissions (for debugging/admin purposes)."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM submissions ORDER BY created_at DESC"
        ).fetchall()

    return jsonify({
        'success': True,
        'count': len(rows),
        'submissions': [dict(row) for row in rows]
    })


if __name__ == '__main__':
    init_db()
    print(f"[Data Service] Starting on port {SERVICE_PORT}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
