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

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
);

-- Categorías de ejemplo
INSERT OR IGNORE INTO categorias (nombre) VALUES
('Electrónica'),
('Cables'),
('Componentes'),
('Computadoras'),
('Conectividad'),
('Energía'),
('Gaming'),
('Impresión'),
('Punto de Venta'),
('Hogar y Línea Blanca'),
('Accesorios'),
('Software');

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    img TEXT,
    categoria_id INTEGER,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Productos de ejemplo
INSERT OR IGNORE INTO productos (id, nombre, precio, img, categoria_id) VALUES
(1, 'Impresora', 330, 'impresoras.png', 8),
(2, 'Controles', 160, 'controles.png', 7),
(3, 'iPhone', 190, 'iPhone.jpg', 1),
(4, 'Producto genérico', 120, 'imagen_placeholder.png', 1);
