-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Usuario admin por defecto
INSERT OR IGNORE INTO usuarios (nombre, email, password)
VALUES ('Administrador', 'admin@pixsoft.com', '12345678');

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    img TEXT
);

-- Productos de ejemplo
INSERT OR IGNORE INTO productos (id, nombre, precio, img) VALUES
(1, 'Impresora', 330, 'impresoras.png'),
(2, 'Controles', 160, 'controles.png'),
(3, 'iPhone', 190, 'iPhone.jpg'),
(4, 'Producto genérico', 120, 'imagen_placeholder.png');