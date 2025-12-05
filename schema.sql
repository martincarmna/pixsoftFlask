-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);
-- Usuario admin por defecto
INSERT OR IGNORE INTO usuarios (nombre, email, password)
VALUES ('Administrador', 'admin@pixsoft.com', '12345678');

-- Tabla de productos (MODIFICADA para incluir categoria_id)
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    img TEXT,
    categoria_id INTEGER,
    -- Definición de la Clave Foránea
    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
);

-- Insertar categorías por defecto
INSERT OR IGNORE INTO categorias (id, nombre) VALUES
(1, 'Electrónica'),
(2, 'Gaming'),
(3, 'Periféricos'),
(4, 'Software');

-- Productos de ejemplo (ENLAZADOS A CATEGORÍAS)
INSERT OR IGNORE INTO productos (id, nombre, precio, img, categoria_id) VALUES
(1, 'Impresora', 330, 'impresoras.png', 3),     -- Categoria: Periféricos (ID 3)
(2, 'Controles', 160, 'controles.png', 2),     -- Categoria: Gaming (ID 2)
(3, 'iPhone', 190, 'iPhone.jpg', 1),           -- Categoria: Electrónica (ID 1)
(4, 'Producto genérico', 120, 'imagen_placeholder.png', 4); -- Categoria: Software (ID 4)