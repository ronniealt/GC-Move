"""006 seed suburbs — 16 Gold Coast suburbs

Revision ID: 006
Revises: 005
Create Date: 2026-06-21
"""
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    INSERT INTO suburbs (name, postcode, latitude, longitude, tier, abs_sa2_code, police_division, bounding_box) VALUES
      ('Burleigh Heads',      '4220', -28.0841, 153.4504, 'A', '316031121', 'Burleigh',       '{"north":-28.074,"south":-28.097,"east":153.462,"west":153.438}'),
      ('Miami',               '4220', -28.0694, 153.4441, 'A', '316031129', 'Burleigh',       '{"north":-28.059,"south":-28.082,"east":153.452,"west":153.432}'),
      ('Mermaid Beach',       '4218', -28.0361, 153.4326, 'A', '316031130', 'Broadbeach',     '{"north":-28.027,"south":-28.048,"east":153.440,"west":153.420}'),
      ('Nobby Beach',         '4218', -28.0563, 153.4406, 'A', '316031132', 'Broadbeach',     '{"north":-28.046,"south":-28.068,"east":153.450,"west":153.430}'),
      ('Palm Beach',          '4221', -28.1148, 153.4633, 'A', '316031134', 'Burleigh',       '{"north":-28.104,"south":-28.128,"east":153.475,"west":153.450}'),
      ('Broadbeach Waters',   '4218', -28.0340, 153.4130, 'A', '316031104', 'Broadbeach',     '{"north":-28.022,"south":-28.048,"east":153.425,"west":153.398}'),
      ('Isle of Capri',       '4217', -27.9880, 153.4130, 'A', '316031124', 'Surfers Paradise','{"north":-27.980,"south":-27.998,"east":153.422,"west":153.404}'),
      ('Mermaid Waters',      '4218', -28.0479, 153.4067, 'B', '316031131', 'Broadbeach',     '{"north":-28.035,"south":-28.062,"east":153.420,"west":153.390}'),
      ('Clear Island Waters', '4226', -28.0681, 153.3718, 'B', '316031108', 'Robina',         '{"north":-28.055,"south":-28.082,"east":153.385,"west":153.357}'),
      ('Varsity Lakes',       '4227', -28.0979, 153.3927, 'B', '316031143', 'Robina',         '{"north":-28.084,"south":-28.113,"east":153.408,"west":153.375}'),
      ('Robina',              '4226', -28.0766, 153.3830, 'B', '316031138', 'Robina',         '{"north":-28.061,"south":-28.094,"east":153.400,"west":153.365}'),
      ('Currumbin',           '4223', -28.1469, 153.4777, 'B', '316031111', 'Burleigh',       '{"north":-28.134,"south":-28.162,"east":153.492,"west":153.462}'),
      ('Tallebudgera',        '4228', -28.1544, 153.4300, 'B', '316031141', 'Burleigh',       '{"north":-28.138,"south":-28.175,"east":153.452,"west":153.405}'),
      ('Mudgeeraba',          '4213', -28.0994, 153.3507, 'C', '316031133', 'Robina',         '{"north":-28.082,"south":-28.120,"east":153.370,"west":153.330}'),
      ('Coomera',             '4209', -27.8777, 153.3313, 'C', '316031109', 'Coomera',        '{"north":-27.856,"south":-27.902,"east":153.358,"west":153.300}'),
      ('Helensvale',          '4212', -27.9267, 153.3485, 'C', '316031120', 'Coomera',        '{"north":-27.908,"south":-27.948,"east":153.372,"west":153.322}')
    ON CONFLICT (name) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("""
    DELETE FROM suburbs WHERE name IN (
      'Burleigh Heads','Miami','Mermaid Beach','Nobby Beach','Palm Beach',
      'Broadbeach Waters','Isle of Capri','Mermaid Waters','Clear Island Waters',
      'Varsity Lakes','Robina','Currumbin','Tallebudgera','Mudgeeraba','Coomera','Helensvale'
    );
    """)
