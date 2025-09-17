from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
import sqlite3
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
import openpyxl
import re
import json
import difflib
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="FileCompareHub API", description="API for online file comparison and script management")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "filecomparehub_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Database setup
DB_PATH = os.getenv("DB_PATH", "filecomparehub.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create scripts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            supported_formats TEXT,
            owner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    
    # Create comparisons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            config TEXT NOT NULL,
            owner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    
    # Create default user if not exists
    default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")
    cursor.execute("SELECT id FROM users WHERE username = ?", (default_username,))
    if not cursor.fetchone():
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (default_username, password_hash)
        )
    
    conn.commit()
    conn.close()

# JWT functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Helper functions for file processing
def read_excel_file(file_path: str) -> str:
    """Read Excel file and convert to text representation"""
    try:
        df = pd.read_excel(file_path)
        return df.to_string()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")

def read_mif_file(file_path: str) -> str:
    """Read MIF file as text"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading MIF file: {str(e)}")

def read_txt_file(file_path: str) -> str:
    """Read TXT file as text"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading TXT file: {str(e)}")

def extract_with_regex(text: str, pattern: str) -> List[str]:
    """Extract matches using regex pattern"""
    try:
        return re.findall(pattern, text)
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {str(e)}")

def compare_texts(text1: str, text2: str, regex_pattern: Optional[str] = None, 
                  filter_pattern: Optional[str] = None, group_by: Optional[str] = None) -> dict:
    """Compare two texts with optional regex processing"""
    # Apply regex extraction if pattern provided
    if regex_pattern:
        matches1 = extract_with_regex(text1, regex_pattern)
        matches2 = extract_with_regex(text2, regex_pattern)
        # Handle tuple matches (multiple groups) by joining them
        if matches1 and isinstance(matches1[0], tuple):
            matches1 = [' '.join(match) for match in matches1]
        if matches2 and isinstance(matches2[0], tuple):
            matches2 = [' '.join(match) for match in matches2]
        text1 = '\n'.join(matches1) if matches1 else ""
        text2 = '\n'.join(matches2) if matches2 else ""
    
    # Apply filter if pattern provided
    if filter_pattern:
        lines1 = [line for line in text1.split('\n') if not re.search(filter_pattern, line)]
        lines2 = [line for line in text2.split('\n') if not re.search(filter_pattern, line)]
        text1 = '\n'.join(lines1)
        text2 = '\n'.join(lines2)
    
    # Calculate diff
    diff = list(difflib.unified_diff(
        text1.splitlines(keepends=True),
        text2.splitlines(keepends=True),
        fromfile='file1',
        tofile='file2'
    ))
    
    # Group differences if requested
    grouped_diff = {}
    if group_by and regex_pattern:
        # Group by regex groups
        for line in diff:
            match = re.search(group_by, line)
            if match:
                key = match.group(1) if len(match.groups()) > 0 else match.group(0)
                if key not in grouped_diff:
                    grouped_diff[key] = []
                grouped_diff[key].append(line)
    else:
        grouped_diff['default'] = diff
    
    return {
        "diff": diff,
        "grouped_diff": grouped_diff,
        "stats": {
            "lines_added": len([d for d in diff if d.startswith('+') and not d.startswith('+++')]),
            "lines_removed": len([d for d in diff if d.startswith('-') and not d.startswith('---')]),
        }
    }

# API Endpoints
@app.post("/auth/login")
async def login(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"user_id": user[0], "username": user[1]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), token: dict = Depends(verify_token)):
    # Save file temporarily
    file_extension = os.path.splitext(file.filename)[1].lower()
    temp_file_path = f"temp_{int(time.time())}{file_extension}"
    
    with open(temp_file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Process based on file type
    text_content = ""
    if file_extension in ['.xlsx', '.xls']:
        text_content = read_excel_file(temp_file_path)
    elif file_extension == '.mif':
        text_content = read_mif_file(temp_file_path)
    elif file_extension == '.txt':
        text_content = read_txt_file(temp_file_path)
    else:
        # For other files, read as text
        try:
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except:
            text_content = "Binary file content not displayed"
    
    # Clean up temp file
    os.remove(temp_file_path)
    
    return {
        "filename": file.filename,
        "content": text_content,
        "size": len(content)
    }

@app.post("/compare")
async def compare_files(
    file1_content: str,
    file2_content: str,
    regex_pattern: Optional[str] = None,
    filter_pattern: Optional[str] = None,
    group_by: Optional[str] = None,
    token: dict = Depends(verify_token)
):
    try:
        result = compare_texts(file1_content, file2_content, regex_pattern, filter_pattern, group_by)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/scripts")
async def list_scripts(skip: int = 0, limit: int = 100, token: dict = Depends(verify_token)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, description, supported_formats, created_at FROM scripts LIMIT ? OFFSET ?",
        (limit, skip)
    )
    
    scripts = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "supported_formats": json.loads(row[3]) if row[3] else [],
            "created_at": row[4]
        }
        for row in scripts
    ]

@app.post("/scripts")
async def create_script(
    name: str,
    content: str,
    description: Optional[str] = None,
    supported_formats: Optional[str] = None,  # JSON array string
    token: dict = Depends(verify_token)
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO scripts (name, description, content, supported_formats, owner_id) VALUES (?, ?, ?, ?, ?)",
            (name, description, content, supported_formats, token.get("user_id"))
        )
        conn.commit()
        script_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Script name already exists")
    finally:
        conn.close()
    
    return {"id": script_id, "message": "Script created successfully"}

@app.get("/scripts/{script_id}")
async def get_script(script_id: int, token: dict = Depends(verify_token)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, description, content, supported_formats, created_at FROM scripts WHERE id = ?",
        (script_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Script not found")
    
    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "content": row[3],
        "supported_formats": json.loads(row[4]) if row[4] else [],
        "created_at": row[5]
    }

@app.put("/scripts/{script_id}")
async def update_script(
    script_id: int,
    name: Optional[str] = None,
    content: Optional[str] = None,
    description: Optional[str] = None,
    supported_formats: Optional[str] = None,  # JSON array string
    token: dict = Depends(verify_token)
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if script exists and belongs to user
    cursor.execute("SELECT id FROM scripts WHERE id = ? AND owner_id = ?", (script_id, token.get("user_id")))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Script not found or unauthorized")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if name is not None:
        update_fields.append("name = ?")
        params.append(name)
    
    if content is not None:
        update_fields.append("content = ?")
        params.append(content)
    
    if description is not None:
        update_fields.append("description = ?")
        params.append(description)
    
    if supported_formats is not None:
        update_fields.append("supported_formats = ?")
        params.append(supported_formats)
    
    if not update_fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")
    
    params.append(script_id)
    query = f"UPDATE scripts SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    return {"message": "Script updated successfully"}

@app.delete("/scripts/{script_id}")
async def delete_script(script_id: int, token: dict = Depends(verify_token)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if script exists and belongs to user
    cursor.execute("SELECT id FROM scripts WHERE id = ? AND owner_id = ?", (script_id, token.get("user_id")))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Script not found or unauthorized")
    
    cursor.execute("DELETE FROM scripts WHERE id = ?", (script_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Script deleted successfully"}

@app.get("/comparisons")
async def list_comparisons(skip: int = 0, limit: int = 100, token: dict = Depends(verify_token)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, config, created_at FROM comparisons WHERE owner_id = ? LIMIT ? OFFSET ?",
        (token.get("user_id"), limit, skip)
    )
    
    comparisons = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "name": row[1],
            "config": json.loads(row[2]) if row[2] else {},
            "created_at": row[3]
        }
        for row in comparisons
    ]

@app.post("/comparisons")
async def create_comparison(
    name: str,
    config: str,  # JSON string
    token: dict = Depends(verify_token)
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO comparisons (name, config, owner_id) VALUES (?, ?, ?)",
            (name, config, token.get("user_id"))
        )
        conn.commit()
        comparison_id = cursor.lastrowid
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating comparison: {str(e)}")
    finally:
        conn.close()
    
    return {"id": comparison_id, "message": "Comparison template created successfully"}

@app.get("/comparisons/{comparison_id}")
async def get_comparison(comparison_id: int, token: dict = Depends(verify_token)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, config, created_at FROM comparisons WHERE id = ? AND owner_id = ?",
        (comparison_id, token.get("user_id"))
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Comparison template not found or unauthorized")
    
    return {
        "id": row[0],
        "name": row[1],
        "config": json.loads(row[2]) if row[2] else {},
        "created_at": row[3]
    }

@app.put("/comparisons/{comparison_id}")
async def update_comparison(
    comparison_id: int,
    name: Optional[str] = None,
    config: Optional[str] = None,  # JSON string
    token: dict = Depends(verify_token)
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if comparison exists and belongs to user
    cursor.execute("SELECT id FROM comparisons WHERE id = ? AND owner_id = ?", (comparison_id, token.get("user_id")))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Comparison template not found or unauthorized")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if name is not None:
        update_fields.append("name = ?")
        params.append(name)
    
    if config is not None:
        update_fields.append("config = ?")
        params.append(config)
    
    if not update_fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")
    
    params.append(comparison_id)
    query = f"UPDATE comparisons SET {', '.join(update_fields)} WHERE id = ?"
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    return {"message": "Comparison template updated successfully"}

@app.delete("/comparisons/{comparison_id}")
async def delete_comparison(comparison_id: int, token: dict = Depends(verify_token)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if comparison exists and belongs to user
    cursor.execute("SELECT id FROM comparisons WHERE id = ? AND owner_id = ?", (comparison_id, token.get("user_id")))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Comparison template not found or unauthorized")
    
    cursor.execute("DELETE FROM comparisons WHERE id = ?", (comparison_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Comparison template deleted successfully"}

@app.get("/")
async def root():
    return {"message": "Welcome to FileCompareHub API"}

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)