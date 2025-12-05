-- ============================================================
-- TABLA DE USUARIOS
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Usuario admin por defecto
INSERT OR IGNORE INTO usuarios (nombre, email, password)
VALUES ('Administrador', 'admin@pixsoft.com', '12345678');

-- ============================================================
-- TABLA DE CATEGORÍAS
-- ============================================================
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
);

-- Categorías de ejemplo
INSERT OR IGNORE INTO categorias (id, nombre) VALUES
(1, 'Electrónica'),
(2, 'Cables'),
(3, 'Componentes'),
(4, 'Computadoras'),
(5, 'Conectividad'),
(6, 'Energía'),
(7, 'Gaming'),
(8, 'Impresión'),
(9, 'Punto de Venta'),
(10, 'Hogar y Línea Blanca'),
(11, 'Accesorios'),
(12, 'Software');

-- ============================================================
-- TABLA DE PRODUCTOS
-- ============================================================
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    img TEXT,
    categoria_id INTEGER,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Productos de ejemplo (enlazados a categorías)
INSERT OR IGNORE INTO productos (id, nombre, precio, img, categoria_id) VALUES
(1, 'Impresora', 330, 'impresoras.png', 8),      -- Categoria: Impresión
(2, 'Controles', 160, 'controles.png', 7),       -- Categoria: Gaming
(3, 'iPhone', 190, 'iPhone.jpg', 1),             -- Categoria: Electrónica
(4, 'Producto genérico', 120, 'imagen_placeholder.png', 12); -- Categoria: Software
