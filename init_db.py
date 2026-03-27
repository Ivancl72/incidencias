import mysql.connector
import os
import random
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# 1. Cargamos configuración del archivo .env
load_dotenv()

# Intentamos leer los secretos
RAW_USER_PASS = os.getenv('DEFAULT_USER_PASS')
RAW_TECH_PASS = os.getenv('DEFAULT_TECH_PASS')
DB_PASS = os.getenv('DB_ROOT_PASSWORD')
# Leemos el host (será mysql_servidor en el NUC o localhost en Windows)
DB_HOST = os.getenv('DB_HOST', 'localhost')

# --- BLOQUE DE SEGURIDAD ESTRICTA ---
if not RAW_USER_PASS or not RAW_TECH_PASS:
    raise ValueError("❌ ERROR DE SEGURIDAD: No se han encontrado las contraseñas en el archivo .env.")

if not DB_PASS:
     raise ValueError("❌ ERROR: Falta la contraseña de la base de datos (DB_ROOT_PASSWORD) en el archivo .env")
# -------------------------------------

print(f"🔌 Conectando a la base de datos en: {DB_HOST}...")

try:
    db = mysql.connector.connect(
        host=DB_HOST, # <--- Cambio clave para Docker
        user="root",
        password=DB_PASS,
        database=os.getenv('DB_NAME')
    )
except mysql.connector.Error as err:
    print(f"❌ Error de conexión: {err}")
    print("Si estás en Docker, asegúrate de que el servicio 'mysql_servidor' esté levantado.")
    exit()

cursor = db.cursor()

# 2. Limpieza
print("🧹 Borrando tablas antiguas...")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0") # Desactivamos checks para borrar sin errores
cursor.execute("DROP TABLE IF EXISTS incidencias")
cursor.execute("DROP TABLE IF EXISTS usuarios")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# 3. Creación de Tablas
print("🏗️ Creando tablas nuevas...")
cursor.execute("""
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255), 
    rol ENUM('usuario', 'tecnico')
)
""")

cursor.execute("""
CREATE TABLE incidencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100),
    descripcion TEXT,
    estado VARCHAR(20) DEFAULT 'Abierta',
    prioridad VARCHAR(20) DEFAULT 'Media',
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# 4. Creación de Usuarios
print("👥 Creando usuarios...")
pass_user = generate_password_hash(RAW_USER_PASS)
pass_tech = generate_password_hash(RAW_TECH_PASS)

# Usuarios principales
cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)", ('ivan', pass_user, 'usuario'))
cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)", ('tecnico', pass_tech, 'tecnico'))

# Usuarios extra oficina
names = ['Ana', 'Carlos', 'Beatriz', 'David', 'Elena', 'Fernando', 'Gabriela']
for n in names:
    cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)", (f"{n.lower()}_user", pass_user, 'usuario'))

# Técnicos extra
for i in range(1, 5):
    cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)", (f"tec{i}", pass_tech, 'tecnico'))

# 5. Incidencias de prueba
print("📝 Generando incidencias de prueba...")
incidencias_data = [
    ("Fallo impresora planta 2", "Mancha las hojas de negro.", 3),
    ("Wifi lento sala juntas", "Se corta la videollamada.", 4),
    ("Licencia Office", "Caducó ayer.", 1),
    ("PC no arranca", "Pantalla azul al iniciar.", 5),
    ("Ratón roto", "Botón derecho no va.", 6),
    ("Servidor caído", "Error 500 en la web corporativa.", 2),
    ("Teclado sucio", "Teclas pegajosas.", 7),
    ("Monitor parpadea", "Cable HDMI parece roto.", 8)
]

prioridades = ['Baja', 'Media', 'Alta', 'Urgente']

for titulo, desc, uid in incidencias_data:
    prio = random.choice(prioridades)
    # Ajuste por si el usuario_id no existe
    cursor.execute(
        "INSERT INTO incidencias (titulo, descripcion, usuario_id, prioridad) VALUES (%s, %s, %s, %s)",
        (titulo, desc, uid, prio)
    )

db.commit()
cursor.close()
db.close()
print("✅ ¡BASE DE DATOS RESTAURADA CORRECTAMENTE!")