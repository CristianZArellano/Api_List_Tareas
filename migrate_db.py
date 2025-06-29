import sqlite3
from datetime import datetime, timedelta
import os

def migrate_database():
    """Migra la base de datos a la nueva estructura"""
    
    # Backup de la base de datos existente
    if os.path.exists("tareas.db"):
        backup_name = f"tareas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.rename("tareas.db", backup_name)
        print(f"Backup creado: {backup_name}")
    
    # Conectar a la nueva base de datos
    conn = sqlite3.connect("tareas.db")
    cursor = conn.cursor()
    
    # Crear tablas con la nueva estructura
    cursor.executescript("""
    -- Tabla de usuarios
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    );
    
    -- Tabla de refresh tokens
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        usuario_id INTEGER NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_revoked BOOLEAN DEFAULT 0,
        device_info TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
    );
    
    -- Tabla de tareas
    CREATE TABLE IF NOT EXISTS tareas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        completado BOOLEAN DEFAULT 0,
        prioridad INTEGER DEFAULT 1,
        fecha_vencimiento TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        usuario_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
    );
    
    -- Índices para mejor rendimiento
    CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
    CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_usuario ON refresh_tokens(usuario_id);
    CREATE INDEX IF NOT EXISTS idx_tareas_usuario ON tareas(usuario_id);
    CREATE INDEX IF NOT EXISTS idx_tareas_completado ON tareas(completado);
    CREATE INDEX IF NOT EXISTS idx_tareas_prioridad ON tareas(prioridad);
    """)
    
    # Si existe un backup, migrar los datos
    if os.path.exists(backup_name):
        try:
            # Conectar al backup
            backup_conn = sqlite3.connect(backup_name)
            backup_cursor = backup_conn.cursor()
            
            # Migrar usuarios
            backup_cursor.execute("SELECT * FROM usuarios")
            usuarios = backup_cursor.fetchall()
            for usuario in usuarios:
                cursor.execute(
                    "INSERT INTO usuarios (id, email, username, hashed_password, is_active, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    usuario
                )
            
            # Migrar tareas
            backup_cursor.execute("SELECT * FROM tareas")
            tareas = backup_cursor.fetchall()
            for tarea in tareas:
                cursor.execute(
                    "INSERT INTO tareas (id, titulo, descripcion, completado, created_at, updated_at, usuario_id) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    tarea
                )
            
            backup_conn.close()
            print("Datos migrados exitosamente")
            
        except Exception as e:
            print(f"Error al migrar datos: {e}")
            # En caso de error, restaurar el backup
            conn.close()
            os.remove("tareas.db")
            os.rename(backup_name, "tareas.db")
            print("Se restauró el backup debido a un error en la migración")
            return
    
    conn.commit()
    conn.close()
    print("Migración completada exitosamente")

if __name__ == "__main__":
    migrate_database() 