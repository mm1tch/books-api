
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Books API",
    description="CRUD básico para libros"
)

# Función para conectar a la base de datos
def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

# Modelo para crear/actualizar libros
class Book(BaseModel):
    title: str
    author: str
    year: Optional[int] = None
    genre: Optional[str] = None
    status: str = "to_read"
    rating: Optional[int] = None

# READ - Obtener todos los libros
@app.get("/books")
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM \"Books\"")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return books

# READ - Obtener un libro por ID
@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM \"Books\" WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return book

# CREATE - Crear un libro
@app.post("/books")
def create_book(book: Book):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """INSERT INTO "Books" (title, author, year, genre, status, rating) 
           VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
        (book.title, book.author, book.year, book.genre, book.status, book.rating)
    )
    new_book = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return new_book

# UPDATE - Actualizar un libro
@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """UPDATE "Books" 
           SET title = %s, author = %s, year = %s, genre = %s, status = %s, rating = %s
           WHERE id = %s RETURNING *""",
        (book.title, book.author, book.year, book.genre, book.status, book.rating, book_id)
    )
    updated_book = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    if not updated_book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return updated_book

# DELETE - Eliminar un libro (opcional pero incluido)
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM \"Books\" WHERE id = %s RETURNING id", (book_id,))
    deleted = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return {"message": "Libro eliminado correctamente"}