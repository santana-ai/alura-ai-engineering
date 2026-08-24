-- Banco determinístico da Clínica Alura (dados fictícios)
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS policies;

CREATE TABLE patients (
    id       TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    insurance TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE policies (
    topic TEXT PRIMARY KEY,
    text  TEXT NOT NULL
);

INSERT INTO patients (id, name, insurance, password) VALUES
    ('123', 'Ana Souza',    'Alura Saúde', 'alura123'),
    ('456', 'Bruno Lima',   'Vida+',       'vida456'),
    ('789', 'Carla Nunes',  'Alura Saúde', 'saude789');

INSERT INTO policies (topic, text) VALUES
    ('convênios',            'Convênios aceitos: Alura Saúde e Vida+.'),
    ('preparo exame de sangue', 'Preparo do exame de sangue: jejum de 8 horas.'),
    ('horário de funcionamento', 'A clínica funciona de segunda a sexta, das 7h às 19h.'),
    ('cancelamento',         'Cancelamentos devem ser feitos com 24 horas de antecedência.');
