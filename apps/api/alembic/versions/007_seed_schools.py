"""007 seed schools and lifestyle categories

Revision ID: 007
Revises: 006
Create Date: 2026-06-21
"""
from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    bind.exec_driver_sql("""
    INSERT INTO schools (name, school_type, sector, address_suburb, address_postcode, latitude, longitude, acara_school_id, year_range, website_url)
    VALUES
      ('Somerset College',                   'combined',   'independent', 'Mudgeeraba', '4213', -28.0997, 153.3471, '51913', 'Prep-12',    'https://www.somerset.qld.edu.au'),
      ('All Saints Anglican School',         'combined',   'independent', 'Merrimac',   '4226', -28.0622, 153.3783, '51885', 'Prep-12',    'https://www.allsaints.qld.edu.au'),
      ('Varsity College',                    'combined',   'government',  'Miami',      '4220', -28.0739, 153.4273, '50124', 'Prep-12',    'https://varsityssc.eq.edu.au'),
      ('Palm Beach-Currumbin State High School', 'secondary', 'government', 'Palm Beach', '4221', -28.1163, 153.4637, '50134', 'Year 7-12', 'https://palmbeachcurrumbinshs.eq.edu.au'),
      ('St Andrews Lutheran College',        'combined',   'independent', 'Tallebudgera','4228',-28.1413, 153.4363, '51960', 'Prep-12',    'https://www.standrews.qld.edu.au')
    ON CONFLICT (acara_school_id) DO NOTHING
    """)

    bind.exec_driver_sql("""
    INSERT INTO lifestyle_asset_categories (key, label, icon, google_type, osm_tag) VALUES
      ('cafe_restaurant',      'Cafes and Restaurants',    'coffee', 'cafe|restaurant',    'amenity=cafe|amenity=restaurant'),
      ('gym_fitness',          'Gyms and Fitness Centres', 'dumbbell', 'gym',             'leisure=fitness_centre'),
      ('pilates_yoga',         'Pilates and Yoga',         'activity', 'gym',             'leisure=yoga|sport=pilates'),
      ('park_reserve',         'Parks and Reserves',       'tree', 'park',                'leisure=park|leisure=nature_reserve'),
      ('beach_access_point',   'Beach Access Points',      'umbrella', 'natural_feature', 'natural=beach'),
      ('shopping_centre',      'Shopping Centres',         'shopping-bag', 'shopping_mall','shop=mall'),
      ('childcare_centre',     'Childcare Centres',        'baby', 'school',              'amenity=kindergarten'),
      ('medical_gp',           'Medical and GP',           'heart', 'doctor|hospital',    'amenity=doctors|amenity=clinic'),
      ('supermarket',          'Supermarkets',             'shopping-cart', 'supermarket', 'shop=supermarket'),
      ('swimming_pool_public', 'Public Swimming Pools',    'droplets', 'swimming_pool',   'leisure=swimming_pool')
    ON CONFLICT (key) DO NOTHING
    """)

    bind = op.get_bind()
    bind.exec_driver_sql("""
    INSERT INTO market_snapshots (suburb_id, snapshot_date, median_house_price_aud, days_on_market_median, price_growth_1yr_pct, price_growth_3yr_pct, source)
    SELECT id, '2026-03-31', 1850000, 24, 8.2, 31.5, 'manual' FROM suburbs WHERE name = 'Burleigh Heads'
    ON CONFLICT DO NOTHING
    """)
    bind.exec_driver_sql("""
    INSERT INTO market_snapshots (suburb_id, snapshot_date, median_house_price_aud, days_on_market_median, price_growth_1yr_pct, price_growth_3yr_pct, source)
    SELECT id, '2026-03-31', 1250000, 31, 6.8, 28.2, 'manual' FROM suburbs WHERE name = 'Robina'
    ON CONFLICT DO NOTHING
    """)
    bind.exec_driver_sql("""
    INSERT INTO market_snapshots (suburb_id, snapshot_date, median_house_price_aud, days_on_market_median, price_growth_1yr_pct, price_growth_3yr_pct, source)
    SELECT id, '2026-03-31', 1480000, 28, 7.5, 29.8, 'manual' FROM suburbs WHERE name = 'Varsity Lakes'
    ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM market_snapshots WHERE source = 'manual'")
    op.execute("DELETE FROM lifestyle_asset_categories")
    op.execute("DELETE FROM schools WHERE acara_school_id IN ('51913','51885','50124','50134','51960')")
